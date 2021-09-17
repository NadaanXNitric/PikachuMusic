import os
import json
import ffmpeg
import aiohttp
import aiofiles
import asyncio
import requests
import converter
from os import path
from asyncio.queues import QueueEmpty
from pyrogram import Client, filters
from typing import Callable
from helpers.channelmusic import get_chat_id
from callsmusic import callsmusic
from callsmusic.queues import queues
from helpers.admins import get_administrators
from youtube_search import YoutubeSearch
from callsmusic.callsmusic import client as USER
from pyrogram.errors import UserAlreadyParticipant
from downloaders import youtube

from config import que, THUMB_IMG, DURATION_LIMIT, BOT_USERNAME, BOT_NAME, UPDATES_CHANNEL, GROUP_SUPPORT, ASSISTANT_NAME, OWNER_NAME
from helpers.filters import command, other_filters
from helpers.decorators import authorized_users_only
from helpers.gets import get_file_name, get_url
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, Voice
from cache.admins import admins as a
from PIL import Image, ImageFont, ImageDraw

aiohttpsession = aiohttp.ClientSession()
chat_id = None
DISABLED_GROUPS = []
useer ="NaN"
def cb_admin_check(func: Callable) -> Callable:
    async def decorator(client, cb):
        admemes = a.get(cb.message.chat.id)
        if cb.from_user.id in admemes:
            return await func(client, cb)
        else:
            await cb.answer("Pɪᴋᴀ Pɪᴋᴀ, ᴘᴇʀᴍɪssɪᴏɴ ғɪʀsᴛ !!", show_alert=True)
            return

    return decorator


def transcode(filename):
    ffmpeg.input(filename).output(
        "input.raw", format="s16le", acodec="pcm_s16le", ac=2, ar="48k"
    ).overwrite_output().run()
    os.remove(filename)


# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


# Change image size
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


async def generate_cover(requested_by, title, views, duration, thumbnail):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()
    image1 = Image.open("./background.png")
    image2 = Image.open("etc/foreground.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")


@Client.on_message(filters.command("playlist") & filters.group & ~filters.edited)
async def playlist(client, message):
    global que
    if message.chat.id in DISABLED_GROUPS:
        return    
    queue = que.get(message.chat.id)
    if not queue:
        await message.reply_text("**Pɪᴋᴀ Pɪᴋᴀ, ɴᴏᴛ ᴘʟᴀʏɪɴɢ ᴀ sᴏɴɢ!**")
    temp = []
    for t in queue:
        temp.append(t)
    now_playing = temp[0][0]
    by = temp[0][1].mention(style="md")
    msg = "**ᴄᴜʀʀᴇɴᴛ sᴏɴɢ** ᴏɴ {}".format(message.chat.title)
    msg += "\n• " + now_playing
    msg += "\n• ʀᴇǫ ʙʏ : " + by
    temp.pop(0)
    if temp:
        msg += "\n\n"
        msg += "**sᴏɴɢ ǫᴜᴇᴜᴇ**"
        for song in temp:
            name = song[0]
            usr = song[1].mention(style="md")
            msg += f"\n• {name}"
            msg += f"\n• ʀᴇǫ ʙʏ : {usr}\n"
    await message.reply_text(msg)


# ============================= Settings =========================================


def updated_stats(chat, queue, vol=100):
    if chat.id in callsmusic.pytgcalls.active_calls:
        # if chat.id in active_chats:
        stats = "Sᴇᴛᴛɪɴɢs ᴏғ **{}**".format(chat.title)
        if len(que) > 0:
            stats += "\n\n"
            stats += "ᴠᴏʟᴜᴍᴇ : {}%\n".format(vol)
            stats += "sᴏɴɢs ɪɴ ǫᴜᴇᴜᴇ : `{}`\n".format(len(que))
            stats += "ᴘʟᴀʏɪɴɢ sᴏɴɢ : **{}**\n".format(queue[0][0])
            stats += "ʀᴇǫᴜᴇsᴛ ʙʏ : {}".format(queue[0][1].mention)
    else:
        stats = None
    return stats


def r_ply(type_):
    if type_ == "play":
        pass
    else:
        pass
    mar = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⏹", "leave"),
                InlineKeyboardButton("⏸", "puse"),
                InlineKeyboardButton("▶️", "resume"),
                InlineKeyboardButton("⏭", "skip"),
            ],
            [
                InlineKeyboardButton("📖 ᴘʟᴀʏʟɪsᴛ", "playlist"),
            ],
            [InlineKeyboardButton("🗑 ᴄʟᴏsᴇ", "cls")],
        ]
    )
    return mar


@Client.on_message(filters.command("current") & filters.group & ~filters.edited)
async def ee(client, message):
    if message.chat.id in DISABLED_GROUPS:
        return
    queue = que.get(message.chat.id)
    stats = updated_stats(message.chat, queue)
    if stats:
        await message.reply(stats)
    else:
        await message.reply("**Pɪᴋᴀ Pɪᴋᴀ, ᴛᴜʀɴ ᴏɴ ᴛʜᴇ ᴠᴄ!!**")


@Client.on_message(filters.command("player") & filters.group & ~filters.edited)
@authorized_users_only
async def settings(client, message):
    if message.chat.id in DISABLED_GROUPS:
        await message.reply("**Pɪᴋᴀ Pɪᴋᴀ, ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ɪs ᴛᴜʀɴᴇᴅ ᴏғғ!!**")
        return    
    playing = None
    chat_id = get_chat_id(message.chat)
    if chat_id in callsmusic.pytgcalls.active_calls:
        playing = True
    queue = que.get(chat_id)
    stats = updated_stats(message.chat, queue)
    if stats:
        if playing:
            await message.reply(stats, reply_markup=r_ply("pause"))

        else:
            await message.reply(stats, reply_markup=r_ply("play"))
    else:
        await message.reply("**Pɪᴋᴀ Pɪᴋᴀ, ᴛᴜʀɴ ᴏɴ ᴠᴄ!!**")


@Client.on_message(
    filters.command("musicplayer") & ~filters.edited & ~filters.bot & ~filters.private
)
@authorized_users_only
async def hfmm(_, message):
    global DISABLED_GROUPS
    try:
        user_id = message.from_user.id
    except:
        return
    if len(message.command) != 2:
        await message.reply_text(
            "**Pɪᴋᴀ Pɪᴋᴀ, ɪ ᴏɴʟʏ ʀᴇᴄᴏɢɴɪᴢᴇ** `/musicplayer On` **ᴀɴᴅ** `/musicplayer Off`."
        )
        return
    status = message.text.split(None, 1)[1]
    message.chat.id
    if status == "ON" or status == "on" or status == "On":
        lel = await message.reply("`Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ᴘʀᴏᴄᴇssɪɴɢ...`")
        if not message.chat.id in DISABLED_GROUPS:
            await lel.edit("**Pɪᴋᴀ Pɪᴋᴀ, ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ**")
            return
        DISABLED_GROUPS.remove(message.chat.id)
        await lel.edit(
            f"✅ **Pɪᴋᴀ Pɪᴋᴀ, ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ᴀᴄᴛɪᴠᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ғᴏʀ ᴜsᴇʀ ɪɴ ᴄʜᴀᴛ** {message.chat.id}"
        )

    elif status == "OFF" or status == "off" or status == "Off":
        lel = await message.reply("`Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ᴘʀᴏᴄᴇssɪɴɢ...`")
        
        if message.chat.id in DISABLED_GROUPS:
            await lel.edit("**Pɪᴋᴀ Pɪᴋᴀ, ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʜᴀs ʙᴇᴇɴ ᴏғғ ɪɴ ᴛʜɪs ᴄʜᴀᴛ**")
            return
        DISABLED_GROUPS.append(message.chat.id)
        await lel.edit(
            f"✅ **Pɪᴋᴀ Pɪᴋᴀ, ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ᴅɪsᴀʙʟᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ғᴏʀ ᴜsᴇʀ ɪɴ ᴄʜᴀᴛ** {message.chat.id}"
        )
    else:
        await message.reply_text(
            "**Pɪᴋᴀ Pɪᴋᴀ, ɪ ᴏɴʟʏ ʀᴇᴄᴏɢɴɪᴢᴇ** `/musicplayer On` **ᴀɴᴅ** `/musicplayer Off`."
        )    
        

@Client.on_callback_query(filters.regex(pattern=r"^(playlist)$"))
async def p_cb(b, cb):
    global que
    que.get(cb.message.chat.id)
    type_ = cb.matches[0].group(1)
    cb.message.chat.id
    cb.message.chat
    cb.message.reply_markup.inline_keyboard[1][0].callback_data
    if type_ == "playlist":
        queue = que.get(cb.message.chat.id)
        if not queue:
            await cb.message.edit("**Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ɴᴏᴛ ᴘʟᴀʏɪɴɢ ᴀ sᴏɴɢ!**")
        temp = []
        for t in queue:
            temp.append(t)
        now_playing = temp[0][0]
        by = temp[0][1].mention(style="md")
        msg = "**ᴄᴜʀʀᴇɴᴛ sᴏɴɢ** On {}".format(cb.message.chat.title)
        msg += "\n• " + now_playing
        msg += "\n• ʀᴇǫᴜᴇsᴛ ʙʏ : " + by
        temp.pop(0)
        if temp:
            msg += "\n\n"
            msg += "**sᴏɴɢ ǫᴜᴇᴜᴇ**"
            for song in temp:
                name = song[0]
                usr = song[1].mention(style="md")
                msg += f"\n• {name}"
                msg += f"\n• ʀᴇǫᴜᴇsᴛ ʙʏ : {usr}\n"
        await cb.message.edit(msg)


@Client.on_callback_query(
    filters.regex(pattern=r"^(play|pause|skip|leave|puse|resume|menu|cls)$")
)
@cb_admin_check
async def m_cb(b, cb):
    global que
    if (
        cb.message.chat.title.startswith("Channel Music: ")
        and chat.title[14:].isnumeric()
    ):
        chet_id = int(chat.title[13:])
    else:
        chet_id = cb.message.chat.id
    qeue = que.get(chet_id)
    type_ = cb.matches[0].group(1)
    cb.message.chat.id
    m_chat = cb.message.chat

    the_data = cb.message.reply_markup.inline_keyboard[1][0].callback_data
    if type_ == "pause":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "paused"
        ):
            await cb.answer("Pɪᴋᴀ Pɪᴋᴀ, ᴄʜᴀᴛ ɪs ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ !!", show_alert=True)
        else:
            callsmusic.pytgcalls.pause_stream(chet_id)

            await cb.answer("Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ᴘᴀᴜsᴇᴅ !!")
            await cb.message.edit(
                updated_stats(m_chat, qeue), reply_markup=r_ply("play")
            )

    elif type_ == "play":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "playing"
        ):
            await cb.answer("Pɪᴋᴀ Pɪᴋᴀ, ᴄʜᴀᴛ ɪs ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ !!", show_alert=True)
        else:
            callsmusic.pytgcalls.resume_stream(chet_id)
            await cb.answer("Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ʀᴇsᴜᴍᴇᴅ !!")
            await cb.message.edit(
                updated_stats(m_chat, qeue), reply_markup=r_ply("pause")
            )

    elif type_ == "playlist":
        queue = que.get(cb.message.chat.id)
        if not queue:
            await cb.message.edit("Player Is Idle")
        temp = []
        for t in queue:
            temp.append(t)
        now_playing = temp[0][0]
        by = temp[0][1].mention(style="md")
        msg = "**ᴄᴜʀʀᴇɴᴛ sᴏɴɢ** On {}".format(cb.message.chat.title)
        msg += "\n• " + now_playing
        msg += "\n• ʀᴇǫᴜᴇsᴛ ʙʏ : " + by
        temp.pop(0)
        if temp:
            msg += "\n\n"
            msg += "**sᴏɴɢ ǫᴜᴇᴜᴇ**"
            for song in temp:
                name = song[0]
                usr = song[1].mention(style="md")
                msg += f"\n• {name}"
                msg += f"\n• ʀᴇǫ,ᴜᴇsᴛ ʙʏ : {usr}\n"
        await cb.message.edit(msg)

    elif type_ == "resume":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "playing"
        ):
            await cb.answer("Pɪᴋᴀ Pɪᴋᴀ, ᴄʜᴀᴛ ɪs ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴏʀ ᴀʟʀᴇᴀᴅʏ ᴘʟᴀʏɪɴɢ!", show_alert=True)
        else:
            callsmusic.pytgcalls.resume_stream(chet_id)
            await cb.answer("Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ʀᴇsᴜᴍᴇᴅ !!")
    elif type_ == "puse":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "paused"
        ):
            await cb.answer("Pɪᴋᴀ Pɪᴋᴀ, ᴄʜᴀᴛ ɪs ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴏʀ ᴀʟʀᴇᴀᴅʏ ᴘᴀᴜsᴇᴅ!", show_alert=True)
        else:
            callsmusic.pytgcalls.pause_stream(chet_id)

            await cb.answer("Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ᴘᴀᴜsᴇᴅ !!")
    elif type_ == "cls":
        await cb.answer("ᴄʟᴏsᴇᴅ ᴍᴇɴᴜ")
        await cb.message.delete()

    elif type_ == "menu":
        stats = updated_stats(cb.message.chat, qeue)
        await cb.answer("ᴍᴇɴᴜ ᴏᴘᴇɴᴇᴅ")
        marr = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⏹", "leave"),
                    InlineKeyboardButton("⏸", "puse"),
                    InlineKeyboardButton("▶️", "resume"),
                    InlineKeyboardButton("⏭", "skip"),
                ],
                [
                    InlineKeyboardButton("📖 ᴘʟᴀʏʟɪsᴛ", "playlist"),
                ],
                [InlineKeyboardButton("❌ ᴄʟᴏsᴇ", "cls")],
            ]
        )
        await cb.message.edit(stats, reply_markup=marr)
    elif type_ == "skip":
        if qeue:
            qeue.pop(0)
        if chet_id not in callsmusic.pytgcalls.active_calls:
            await cb.answer("Pɪᴋᴀ Pɪᴋᴀ, ᴄʜᴀᴛ ɪs ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ !!", show_alert=True)
        else:
            callsmusic.queues.task_done(chet_id)

            if callsmusic.queues.is_empty(chet_id):
                callsmusic.pytgcalls.leave_group_call(chet_id)

                await cb.message.edit("- Pɪᴋᴀ Pɪᴋᴀ, ɴᴏ ᴍᴏʀᴇ ᴘʟᴀʏʟɪsᴛ...\n- ʟᴇᴀᴠɪɴɢ ᴠᴄ !!")
            else:
                callsmusic.pytgcalls.change_stream(
                    chet_id, callsmusic.queues.get(chet_id)["file"]
                )
                await cb.answer("Skipped")
                await cb.message.edit((m_chat, qeue), reply_markup=r_ply(the_data))
                await cb.message.reply_text(
                    f"- Pɪᴋᴀ Pɪᴋᴀ, sᴋɪᴘᴘᴇᴅ ᴛʀᴀᴄᴋ :\n- ɴᴏᴡ ᴘʟᴀʏɪɴɢ : **{qeue[0][0]}**"
                )

    else:
        if chet_id in callsmusic.pytgcalls.active_calls:
            try:
                callsmusic.queues.clear(chet_id)
            except QueueEmpty:
                pass

            callsmusic.pytgcalls.leave_group_call(chet_id)
            await cb.message.edit("Pɪᴋᴀ Pɪᴋᴀ, sᴜᴄᴄᴇssғᴜʟʟʏ ʟᴇғᴛ ᴛʜᴇ ᴄʜᴀᴛ !!")
        else:
            await cb.answer("Pɪᴋᴀ Pɪᴋᴀ, ᴄʜᴀᴛ ɪs ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ !!", show_alert=True)


@Client.on_message(command("play") & other_filters)
async def play(_, message: Message):
    global que
    global useer
    if message.chat.id in DISABLED_GROUPS:
        return    
    lel = await message.reply("🔁 **Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ᴘʀᴏᴄᴇssɪɴɢ...**")
    administrators = await get_administrators(message.chat)
    chid = message.chat.id

    try:
        user = await USER.get_me()
    except:
        user.first_name = "PikachuXMusic"
    usar = user
    wew = usar.id
    try:
        # chatdetails = await USER.get_chat(chid)
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                if message.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        f"<b>Pɪᴋᴀ Pɪᴋᴀ, ʀᴇᴍᴇᴍʙᴇʀ ᴛᴏ ᴀᴅᴅ @{ASSISTANT_NAME} ᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ.</b>",
                    )
                    pass
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>Pɪᴋᴀ Pɪᴋᴀ, ᴀᴅᴅ ᴍᴇ ᴀs ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴ ғɪʀsᴛ.</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message.chat.id, "🤖 Pɪᴋᴀ Pɪᴋᴀ, ɪ ᴊᴏɪɴᴇᴅ ᴛʜɪs ɢʀᴏᴜᴘ ғᴏʀ ᴘʟᴀʏɪɴɢ ᴍᴜsɪᴄ ɪɴ ᴠᴄ."
                    )
                    await lel.edit(
                        "<b>Pɪᴋᴀ Pɪᴋᴀ, ʜᴇʟᴘᴇʀ ᴜsᴇʀʙᴏᴛ ᴊᴏɪɴᴇᴅ ʏᴏᴜʀ ᴄʜᴀᴛ.</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>Pɪᴋᴀ Pɪᴋᴀ, ⛑ ғʟᴏᴏᴅ ᴡᴀɪᴛ ᴇʀʀᴏʀ ⛑\n{user.first_name} ᴄᴀɴ'ᴛ ᴊᴏɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴅᴜᴇ ᴛᴏ ᴍᴀɴʏ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ғᴏʀ ᴜsᴇʀʙᴏᴛ !! ᴍᴀᴋs sᴜʀᴇ ᴛʜᴇ ᴜsᴇʀ ɪs ɴᴏᴛ ʙᴀɴɴᴇᴅ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ."
                        f"\n\nᴏʀ ᴀᴅᴅ @{ASSISTANT_NAME} ᴍᴀɴᴜᴀʟʟʏ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i>{user.first_name} ᴡʜʏ ɪs ᴍʏ ᴀssɪsᴛᴀɴᴛ ʙᴀɴɴᴇᴅ, ᴀsᴋ ᴛʜᴇ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴ ᴛᴏ ᴀᴅᴅ ᴛʜᴇ @{ASSISTANT_NAME} ᴀsɪsᴛᴀɴᴛ ᴀɢᴀɪɴ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ :).</i>"
        )
        return
    text_links=None
    await lel.edit("🔎 **Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ʟᴏᴏᴋɪɴɢ ғᴏʀ ᴀ sᴏɴɢ...**")
    if message.reply_to_message:
        entities = []
        toxt = message.reply_to_message.text or message.reply_to_message.caption
        if message.reply_to_message.entities:
            entities = message.reply_to_message.entities + entities
        elif message.reply_to_message.caption_entities:
            entities = message.reply_to_message.entities + entities
        urls = [entity for entity in entities if entity.type == 'url']
        text_links = [
            entity for entity in entities if entity.type == 'text_link'
        ]
    else:
        urls=None
    if text_links:
        urls = True
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"❌ **Pɪᴋᴀ Pɪᴋᴀ, Eʀʀᴏʀ !!🛑 Sᴏʀʀʏ, ᴏɴʟʏ {DURATION_LIMIT} ᴍɪɴᴜᴛᴇs sᴏɴɢ ɪs ᴀʟʟᴏᴡᴇᴅ.**"
            )
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🖱 ᴍᴇɴᴜ", callback_data="menu"),
                    InlineKeyboardButton("🗑 ᴄʟᴏsᴇ", callback_data="cls"),
                ],[
                    InlineKeyboardButton("📣 ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{UPDATES_CHANNEL}")
                ],
            ]
        )
        file_name = get_file_name(audio)
        title = file_name
        thumb_name = "https://telegra.ph/file/ddc29625ac13587916700.png"
        thumbnail = thumb_name
        duration = round(audio.duration / 60)
        views = "Locally Added"
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await converter.convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name))
            else file_name
        )
    elif urls:
        query = toxt
        await lel.edit("🔁 **https://telegra.ph/file/ddc29625ac13587916700.pngProcessing Song...**")
        ydl_opts = {"format": "bestaudio[ext=m4a]"}
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            # print(results)
            title = results[0]["title"][:25]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            results[0]["url_suffix"]
            views = results[0]["views"]

        except Exception as e:
            await lel.edit(
                "**Pɪᴋᴀ Pɪᴋᴀ, sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ.** ᴛʀʏ sᴇᴀʀᴄʜɪɴɢ ᴡɪᴛʜ ᴀ ᴄʟᴇᴀʀᴇʀ sᴏɴɢ ᴛɪᴛᴛʟᴇ, ᴛʏᴘᴇ /help ɪғ ʏᴏᴜ ɴᴇᴇᴅ ʜᴇʟᴘ."
            )
            print(str(e))
            return
        dlurl=url
        dlurl=dlurl.replace("youtube","youtubepp")
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🖱 ᴍᴇɴᴜ", callback_data="menu"),
                    InlineKeyboardButton("🗑 ᴄʟᴏsᴇ", callback_data="cls"),
                ],[
                    InlineKeyboardButton("📣 ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{UPDATES_CHANNEL}")
                ],
            ]
        )
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await converter.convert(youtube.download(url))        
    else:
        query = ""
        for i in message.command[1:]:
            query += " " + str(i)
        print(query)
        await lel.edit("🔁 **Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ᴘʀᴏᴄᴇssɪɴɢ sᴏɴɢ...**")
        ydl_opts = {"format": "bestaudio[ext=m4a]"}
        
        try:
          results = YoutubeSearch(query, max_results=5).to_dict()
        except:
          await lel.edit("**Pɪᴋᴀ Pɪᴋᴀ, ɢɪᴠᴇ ᴛʜᴇ ᴛɪᴛᴛʟᴇ ᴏғ ᴛʜᴇ sᴏɴɢ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴘʟᴀʏ !!**")
        # Looks like hell. Aren't it?? FUCK OFF
        try:
            toxxt = "**__🌻 ᴄʜᴏᴏsᴇ ᴀ sᴏɴɢ ᴛᴏ ᴘʟᴀʏ :__**\n\n"
            j = 0
            useer=user_name
            emojilist = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣"]

            while j < 5:
                toxxt += f"{emojilist[j]} [{results[j]['title'][:25]}](https://youtube.com{results[j]['url_suffix']})...\n"
                toxxt += f" ├ 💡 ᴅᴜʀᴀᴛɪᴏɴ - {results[j]['duration']}\n"
                toxxt += f" └ ⚡ Pᴏᴡᴇʀᴇᴅ ʙʏ - 「ᴘɪᴋᴀᴄʜᴜχᴅ」\n\n"

                j += 1            
            keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🖱 ᴍᴇɴᴜ", callback_data="menu"),
                    InlineKeyboardButton("🗑 ᴄʟᴏsᴇ", callback_data="cls"),
                ],[
                    InlineKeyboardButton("📣 ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{UPDATES_CHANNEL}")
                ],
            ]
        )       
            await message.reply_photo(
                photo=f"{THUMB_IMG}",
                caption=toxxt,
                reply_markup=keyboard
            )

            await lel.delete()
            # veez project
            return
            # veez project
        except:
            await lel.edit("__Pɪᴋᴀ Pɪᴋᴀ, ɴᴏ ᴍᴏʀᴇ ʀᴇsᴜʟᴛs, sᴛᴀʀᴛɪɴɢ ᴛᴏ ᴘʟᴀʏɪɴɢ...__")
                        
            # print(results)
            try:
                url = f"https://youtube.com{results[0]['url_suffix']}"
                title = results[0]["title"][:25]
                thumbnail = results[0]["thumbnails"][0]
                thumb_name = f"thumb{title}.jpg"
                thumb = requests.get(thumbnail, allow_redirects=True)
                open(thumb_name, "wb").write(thumb.content)
                duration = results[0]["duration"]
                results[0]["url_suffix"]
                views = results[0]["views"]

            except Exception as e:
                await lel.edit(
                "**Pɪᴋᴀ Pɪᴋᴀ, sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ.** ᴛʀʏ sᴇᴀʀᴄʜɪɴɢ ᴡɪᴛʜ ᴀ ᴄʟᴇᴀʀᴇʀ sᴏɴɢ ᴛɪᴛʟᴇ, ᴛʏᴘᴇ /help ɪғ ʏᴏᴜ ɴᴇᴇᴅ ʜᴇʟᴘ"
            )
                print(str(e))
                return
            dlurl=url
            dlurl=dlurl.replace("youtube","youtubepp")
            keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🖱 ᴍᴇɴᴜ", callback_data="menu"),
                    InlineKeyboardButton("🗑 ᴄʟᴏsᴇ", callback_data="cls"),
                ],[
                    InlineKeyboardButton("📣 ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{UPDATES_CHANNEL}")
                ],
            ]
        )
            requested_by = message.from_user.first_name
            await generate_cover(requested_by, title, views, duration, thumbnail)
            file_path = await converter.convert(youtube.download(url))   
    chat_id = get_chat_id(message.chat)
    if chat_id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await message.reply_photo(
            photo="final.png",
            caption = f"🏷 **ᴛɪᴛᴛʟᴇ :** [{title[:30]}]({url})...\n⏱ **ᴅᴜʀᴀᴛɪᴏɴ :** {duration}\n💡 **sᴛᴀᴛᴜs :** ǫᴜᴇᴜᴇᴅ ᴛᴏ `{position}`\n" \
                    + f"🎧 **ʀᴇǫᴜᴇsᴛ ʙʏ :** {message.from_user.mention}",
                   reply_markup=keyboard)
       
    else:
        chat_id = get_chat_id(message.chat)
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        try:
            callsmusic.pytgcalls.join_group_call(chat_id, file_path)
        except:
            message.reply("**Pɪᴋᴀ Pɪᴋᴀ, ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ɢʀᴏᴜᴘ ɪs ɴᴏᴛ ᴀᴄᴛɪᴠᴇ, ɪ ᴄᴀɴ'ᴛ ᴊᴏɪɴ.**")
            return
        await message.reply_photo(
            photo="final.png",
            caption = f"🏷 **ᴛɪᴛᴛʟᴇ :** [{title[:30]}]({url})...\n⏱ **ᴅᴜʀᴀᴛɪᴏɴ :** {duration}\n💡 **sᴛᴀᴛᴜs :** ᴘʟᴀʏɪɴɢ\n" \
                    + f"🎧 **ʀᴇǫᴜᴇsᴛ ʙʏ :** {message.from_user.mention}",
                   reply_markup=keyboard)

    os.remove("final.png")
    return await lel.delete()


@Client.on_message(filters.command("ytplay") & filters.group & ~filters.edited)
async def ytplay(_, message: Message):
    global que
    if message.chat.id in DISABLED_GROUPS:
        return
    lel = await message.reply("🔁 **Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ᴘʀᴏᴄᴇssɪɴɢ sᴏɴɢ**")
    administrators = await get_administrators(message.chat)
    chid = message.chat.id

    try:
        user = await USER.get_me()
    except:
        user.first_name = "PikachuXMusic"
    usar = user
    wew = usar.id
    try:
        # chatdetails = await USER.get_chat(chid)
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                if message.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        f"<b>Pɪᴋᴀ Pɪᴋᴀ, ʀᴇᴍᴇᴍʙᴇʀ ᴛᴏ ᴀᴅᴅ @{ASSISTANT_NAME} ᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ.</b>",
                    )
                    pass
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>Pɪᴋᴀ Pɪᴋᴀ, ᴀᴅᴅ ᴍᴇ ᴀs ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴ ғɪʀsᴛ.</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message.chat.id, "🤖 Pɪᴋᴀ Pɪᴋᴀ, ɪ ᴊᴏɪɴᴇᴅ ᴛʜɪs ɢʀᴏᴜᴘ ғᴏʀ ᴘʟᴀʏɪɴɢ ᴍᴜsɪᴄ ɪɴ ᴠᴄ."
                    )
                    await lel.edit(
                        "<b>Pɪᴋᴀ Pɪᴋᴀ, ʜᴇʟᴘᴇʀ ᴜsᴇʀʙᴏᴛ ᴊᴏɪɴᴇᴅ ʏᴏᴜʀ ᴄʜᴀᴛ.</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>Pɪᴋᴀ Pɪᴋᴀ, ⛑ ғʟᴏᴏᴅ ᴡᴀɪᴛ ᴇʀʀᴏʀ ⛑\n{user.first_name} ᴄᴀɴ'ᴛ ᴊᴏɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴅᴜᴇ ᴛᴏ ᴍᴀɴʏ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ғᴏʀ ᴜsᴇʀʙᴏᴛ !! ᴍᴀᴋs sᴜʀᴇ ᴛʜᴇ ᴜsᴇʀ ɪs ɴᴏᴛ ʙᴀɴɴᴇᴅ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ."
                        f"\n\nᴏʀ ᴀᴅᴅ @{ASSISTANT_NAME} ᴍᴀɴᴜᴀʟʟʏ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i>{user.first_name} ᴡʜʏ ɪs ᴍʏ ᴀssɪsᴛᴀɴᴛ ʙᴀɴɴᴇᴅ, ᴀsᴋ ᴛʜᴇ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴ ᴛᴏ ᴀᴅᴅ ᴛʜᴇ @{ASSISTANT_NAME} ᴀsɪsᴛᴀɴᴛ ᴀɢᴀɪɴ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ :).</i>"
        )
        return
    await lel.edit("🔎 **Pɪᴋᴀ Pɪᴋᴀ, ʟᴏᴏᴋɪɴɢ ғᴏʀ ᴀ sᴏɴɢ...**")
    user_id = message.from_user.id
    user_name = message.from_user.first_name
     

    query = ""
    for i in message.command[1:]:
        query += " " + str(i)
    print(query)
    await lel.edit("🔁 **Pɪᴋᴀ Pɪᴋᴀ, ᴘʀᴏᴄᴇssɪɴɢ sᴏɴɢ...**")
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        url = f"https://youtube.com{results[0]['url_suffix']}"
        # print(results)
        title = results[0]["title"][:25]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"thumb{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        duration = results[0]["duration"]
        results[0]["url_suffix"]
        views = results[0]["views"]

    except Exception as e:
        await lel.edit(
            "**Pɪᴋᴀ Pɪᴋᴀ, sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ.** ᴛʀʏ sᴇᴀʀᴄʜɪɴɢ ᴡɪᴛʜ ᴀ ᴄʟᴇᴀʀᴇʀ sᴏɴɢ ᴛɪᴛʟᴇ, ᴛʏᴘᴇ /help ɪғ ʏᴏᴜ ɴᴇᴇᴅ ʜᴇʟᴘ."
        )
        print(str(e))
        return
    dlurl=url
    dlurl=dlurl.replace("youtube","youtubepp")
    keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🖱 ᴍᴇɴᴜ", callback_data="menu"),
                    InlineKeyboardButton("🗑 ᴄʟᴏsᴇ", callback_data="cls"),
                ],[
                    InlineKeyboardButton("📣 ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{UPDATES_CHANNEL}")
                ],
            ]
        )
    requested_by = message.from_user.first_name
    await generate_cover(requested_by, title, views, duration, thumbnail)
    file_path = await converter.convert(youtube.download(url))
    chat_id = get_chat_id(message.chat)
    if chat_id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await message.reply_photo(
            photo="final.png",
            caption = f"🏷 **ᴛɪᴛᴛʟᴇ :** [{title[:30]}]({url})...\n⏱ **ᴅᴜʀᴀᴛɪᴏɴ :** {duration}\n💡 **sᴛᴀᴛᴜs :** ǫᴜᴇᴜᴇᴅ ᴛᴏ `{position}`\n" \
                    + f"🎧 **ʀᴇǫᴜᴇsᴛ ʙʏ :** {message.from_user.mention}",
                   reply_markup=keyboard,
        )
        os.remove("final.png")
        return await lel.delete()
    else:
        chat_id = get_chat_id(message.chat)
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        try:
            callsmusic.pytgcalls.join_group_call(chat_id, file_path)
        except:
            message.reply("**Pɪᴋᴀ Pɪᴋᴀ, ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ɢʀᴏᴜᴘ ɪs ɴᴏᴛ ᴀᴄᴛɪᴠᴇ, ɪ ᴄᴀɴ'ᴛ ᴊᴏɪɴ**")
            return
        await message.reply_photo(
            photo="final.png",
            caption = f"🏷 **ᴛɪᴛᴛʟᴇ :** [{title[:30]}]({url})...\n⏱ **ᴅᴜʀᴀᴛɪᴏɴ :** {duration}\n💡 **sᴛᴀᴛᴜs :** ᴘʟᴀʏɪɴɢ\n" \
                    + f"🎧 **ʀᴇǫᴜᴇsᴛ ʙʏ :** {message.from_user.mention}",
                   reply_markup=keyboard,)
        os.remove("final.png")
        return await lel.delete()
    

@Client.on_message(filters.command("dplay") & filters.group & ~filters.edited)
async def deezer(client: Client, message_: Message):
    if message_.chat.id in DISABLED_GROUPS:
        return
    global que
    lel = await message_.reply("🔁 **Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ᴘʀᴏᴄᴇssɪɴɢ sᴏɴɢ...**")
    administrators = await get_administrators(message_.chat)
    chid = message_.chat.id
    try:
        user = await USER.get_me()
    except:
        user.first_name = "PikachuXMusic"
    usar = user
    wew = usar.id
    try:
        # chatdetails = await USER.get_chat(chid)
        await client.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message_.from_user.id:
                if message_.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        f"<b>Pɪᴋᴀ Pɪᴋᴀ, ʀᴇᴍᴇᴍʙᴇʀ ᴛᴏ ᴀᴅᴅ @{ASSISTANT_NAME} ᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ.</b>",
                    )
                    pass
                try:
                    invitelink = await client.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>Pɪᴋᴀ Pɪᴋᴀ, ᴀᴅᴅ ᴍᴇ ᴀs ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴ ғɪʀsᴛ.</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message_.chat.id, "🤖 Pɪᴋᴀ Pɪᴋᴀ, ɪ ᴊᴏɪɴᴇᴅ ᴛʜɪs ɢʀᴏᴜᴘ ғᴏʀ ᴘʟᴀʏɪɴɢ ᴍᴜsɪᴄ ɪɴ ᴠᴄ."
                    )
                    await lel.edit(
                        "<b>Pɪᴋᴀ Pɪᴋᴀ, ʜᴇʟᴘᴇʀ ᴜsᴇʀʙᴏᴛ ᴊᴏɪɴᴇᴅ ʏᴏᴜʀ ᴄʜᴀᴛ.</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>Pɪᴋᴀ Pɪᴋᴀ, ⛑ ғʟᴏᴏᴅ ᴡᴀɪᴛ ᴇʀʀᴏʀ ⛑\n{user.first_name} ᴄᴀɴ'ᴛ ᴊᴏɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴅᴜᴇ ᴛᴏ ᴍᴀɴʏ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ғᴏʀ ᴜsᴇʀʙᴏᴛ !! ᴍᴀᴋs sᴜʀᴇ ᴛʜᴇ ᴜsᴇʀ ɪs ɴᴏᴛ ʙᴀɴɴᴇᴅ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ."
                        f"\n\nᴏʀ ᴀᴅᴅ @{ASSISTANT_NAME} ᴍᴀɴᴜᴀʟʟʏ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i>{user.first_name} ᴡʜʏ ɪs ᴍʏ ᴀssɪsᴛᴀɴᴛ ʙᴀɴɴᴇᴅ, ᴀsᴋ ᴛʜᴇ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴ ᴛᴏ ᴀᴅᴅ ᴛʜᴇ @{ASSISTANT_NAME} ᴀsɪsᴛᴀɴᴛ ᴀɢᴀɪɴ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ :).</i>"
        )
        return
    requested_by = message_.from_user.first_name

    text = message_.text.split(" ", 1)
    queryy = text[1]
    query = queryy
    res = lel
    await res.edit(f"**Pɪᴋᴀ Pɪᴋᴀ, ʟᴏᴏᴋɪɴɢ ғᴏʀ ᴀ sᴏɴɢ...** `{query}`")
    try:
        songs = await arq.deezer(query,1)
        if not songs.ok:
            await message_.reply_text(songs.result)
            return
        title = songs.result[0].title
        url = songs.result[0].url
        artist = songs.result[0].artist
        duration = songs.result[0].duration
        thumbnail = "https://telegra.ph/file/ddc29625ac13587916700.png"

    except:
        await res.edit("**Pɪᴋᴀ Pɪᴋᴀ, ɴᴏ ᴀɴʏ sᴏɴɢ ғᴏᴜɴᴅ, sᴏʀʀʏ !!**")
        return
    try:    
        duuration= round(duration / 60)
        if duuration > DURATION_LIMIT:
            await cb.message.edit(f"**Pɪᴋᴀ Pɪᴋᴀ, ᴍᴜsɪᴄ ɪs ʟᴏɴɢᴇʀ ᴛʜᴀɴ** `{DURATION_LIMIT}` **ᴍɪɴᴜᴛᴇs ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴘʟᴀʏ.**")
            return
    except:
        pass    
    
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="📍 ᴄʜᴀɴɴᴇʟ", url="https://t.me/Sanki_BOTs")],
        ]
    )
    file_path = await converter.convert(wget.download(url))
    await res.edit("📥 **Pɪᴋᴀ Pɪᴋᴀ, ɢᴇɴᴇʀᴀᴛɪɴɢ ᴛʜᴜᴍʙɴᴀɪʟs...**")
    await generate_cover(requested_by, title, artist, duration, thumbnail)
    chat_id = get_chat_id(message_.chat)
    if chat_id in callsmusic.pytgcalls.active_calls:
        await res.edit("Pɪᴋᴀ Pɪᴋᴀ, ᴀᴅᴅɪɴɢ ɪɴ ǫᴜᴇᴜᴇ...")
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        r_by = message_.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await res.edit_text(f"🎼 **Pɪᴋᴀ Pɪᴋᴀ, ᴛʜᴇ sᴏɴɢ ʏᴏᴜ ᴀsᴋᴇᴅ ғᴏʀ ɪs ɪɴ ʟɪɴᴇ** `{position}`")
    else:
        await res.edit_text(f"🎼️ **Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ᴘʟᴀʏɪɴɢ...**")

        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message_.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        try:
            callsmusic.pytgcalls.join_group_call(chat_id, file_path)
        except:
            res.edit("Pɪᴋᴀ Pɪᴋᴀ, ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ɢʀᴏᴜᴘ ɪs ɴᴏᴛ ᴀᴄᴛɪᴠᴇ, ɪ ᴄᴀɴ'ᴛ ᴊᴏɪɴ.")
            return

    await res.delete()

    m = await client.send_photo(
        chat_id=message_.chat.id,
        reply_markup=keyboard,
        photo="final.png",
        caption=f"🎼️ **ᴘʟᴀʏɪɴɢ sᴏɴɢ** : [{title}]({url}).**",
    )
    os.remove("final.png")


@Client.on_callback_query(filters.regex(pattern=r"plll"))
async def lol_cb(b, cb):
    global que

    cbd = cb.data.strip()
    chat_id = cb.message.chat.id
    typed_=cbd.split(None, 1)[1]
    #useer_id = cb.message.reply_to_message.from_user.id
    try:
        x,query,useer_id = typed_.split("|")      
    except:
        await cb.message.edit("Pɪᴋᴀ Pɪᴋᴀ, sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ!!")
        return
    useer_id = int(useer_id)
    if cb.from_user.id != useer_id:
        await cb.answer("Pɪᴋᴀ Pɪᴋᴀ, ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴛʜᴇ ᴏɴᴇ ᴀsᴋɪɴɢ ᴛᴏ ᴘʟᴀʏ ᴛʜᴇ sᴏɴɢ !!", show_alert=True)
        return
    await cb.message.edit("**Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ...**")
    x=int(x)
    try:
        useer_name = cb.message.reply_to_message.from_user.first_name
    except:
        useer_name = cb.message.from_user.first_name
    
    results = YoutubeSearch(query, max_results=5).to_dict()
    resultss=results[x]["url_suffix"]
    title=results[x]["title"][:25]
    thumbnail=results[x]["thumbnails"][0]
    duration=results[x]["duration"]
    views=results[x]["views"]
    url = f"https://youtube.com{resultss}"
    
    try:    
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        if (dur / 60) > DURATION_LIMIT:
             await cb.message.edit(f"❌ **Pɪᴋᴀ Pɪᴋᴀ, Eʀʀᴏʀ !!🛑 Sᴏʀʀʏ, ᴏɴʟʏ {DURATION_LIMIT} ᴍɪɴᴜᴛᴇs sᴏɴɢ ɪs ᴀʟʟᴏᴡᴇᴅ.")
             return
    except:
        pass
    try:
        thumb_name = f"thumb{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
    except Exception as e:
        print(e)
        return
    dlurl=url
    dlurl=dlurl.replace("youtube","youtubepp")
    keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🖱 ᴍᴇɴᴜ", callback_data="menu"),
                    InlineKeyboardButton("🗑 ᴄʟᴏsᴇ", callback_data="cls"),
                ],[
                    InlineKeyboardButton("📣 ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{UPDATES_CHANNEL}")
                ],
            ]
        )
    requested_by = useer_name
    await generate_cover(requested_by, title, views, duration, thumbnail)
    file_path = await converter.convert(youtube.download(url))  
    if chat_id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        try:
            r_by = cb.message.reply_to_message.from_user
        except:
            r_by = cb.message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await cb.message.delete()
        await b.send_photo(chat_id,
            photo="final.png",
            caption = f"🏷 **ᴛɪᴛᴛʟᴇ :** [{title[:30]}]({url})...\n⏱ **ᴅᴜʀᴀᴛɪᴏɴ :** {duration}\n💡 **sᴛᴀᴛᴜs :** ǫᴜᴇᴜᴇ ᴛᴏ `{position}`\n" \
                    + f"🎧 **ʀᴇǫᴜᴇsᴛ ʙʏ :** {r_by.mention}",
                   reply_markup=keyboard,
        )
        os.remove("final.png")
        
    else:
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        try:
            r_by = cb.message.reply_to_message.from_user
        except:
            r_by = cb.message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)

        callsmusic.pytgcalls.join_group_call(chat_id, file_path)
        await cb.message.delete()
        await b.send_photo(chat_id,
            photo="final.png",
            caption = f"🏷 **ᴛɪᴛᴛʟᴇ :** [{title[:30]}]({url})...\n⏱ **ᴅᴜʀᴀᴛɪᴏɴ :** {duration}\n💡 **sᴛᴀᴛᴜs :** ᴘʟᴀʏɪɴɢ\n" \
                    + f"🎧 **ʀᴇǫᴜᴇsᴛ ʙʏ :** {r_by.mention}",
                    reply_markup=keyboard,
        )
        os.remove("final.png")
