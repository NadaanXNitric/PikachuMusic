from asyncio import QueueEmpty
from config import que
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from cache.admins import set
from helpers.channelmusic import get_chat_id
from helpers.decorators import authorized_users_only, errors
from helpers.filters import command, other_filters
from callsmusic import callsmusic
from callsmusic.queues import queues


@Client.on_message(filters.command("reload"))
async def update_admin(client, message: Message):
    chat_id = get_chat_id(message.chat)
    set(
        chat_id,
        [
            member.user
            for member in await message.chat.get_members(filter="administrators")
        ],
    )
    await message.reply_text("""✅ Pɪᴋᴀ Pɪᴋᴀ, Bᴏᴛ **ʀᴇғʀᴇsʜᴇᴅ!**\n\n**• Aᴅᴍɪɴ ʟɪsᴛ** ʜᴀs ʙᴇᴇɴ **ᴜᴘᴅᴀᴛᴇᴅ!**""",
      reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📣 ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/Sanki_BOTs"
                    ),
                    InlineKeyboardButton(
                        "👥 ɢʀᴏᴜᴘ", url=f"https://t.me/Sanki_BOTs_Support"
                    )
                ]
            ]
        )
   )


@Client.on_message(command("pause") & other_filters)
@errors
@authorized_users_only
async def pause(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if (chat_id not in callsmusic.pytgcalls.active_calls) or (
        callsmusic.pytgcalls.active_calls[chat_id] == "paused"
    ):
        await message.reply_text("❗Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ɴᴏᴛʜɪɴɢ sᴛʀᴇᴀᴍɪɴɢ!")
    else:
        callsmusic.pytgcalls.pause_stream(chat_id)
        await message.reply_text("▶️ Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ᴘᴀᴜsᴇᴅ!")


@Client.on_message(command("resume") & other_filters)
@errors
@authorized_users_only
async def resume(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if (chat_id not in callsmusic.pytgcalls.active_calls) or (
        callsmusic.pytgcalls.active_calls[chat_id] == "playing"
    ):
        await message.reply_text("❗Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ɴᴏᴛʜɪɴɢ ᴘᴀᴜsᴇᴅ!")
    else:
        callsmusic.pytgcalls.resume_stream(chat_id)
        await message.reply_text("⏸ Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ʀᴇsᴜᴍᴇᴅ!")


@Client.on_message(command("end") & other_filters)
@errors
@authorized_users_only
async def stop(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❗Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ɴᴏᴛʜɪɴɢ sᴛʀᴇᴀᴍɪɴɢ!")
    else:
        try:
            queues.clear(chat_id)
        except QueueEmpty:
            pass

        callsmusic.pytgcalls.leave_group_call(chat_id)
        await message.reply_text("✅ __Pɪᴋᴀ Pɪᴋᴀ, Usᴇʀʙᴏᴛ ʜᴀs ʙᴇᴇɴ ᴅɪsᴄᴏɴɴᴇᴄᴛᴇᴅ__.")


@Client.on_message(command("skip") & other_filters)
@errors
@authorized_users_only
async def skip(_, message: Message):
    global que
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❗Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ɴᴏᴛʜɪɴɢ ɪs ᴘʟᴀʏɪɴɢ ᴛᴏ sᴋɪᴘ!")
    else:
        queues.task_done(chat_id)

        if queues.is_empty(chat_id):
            callsmusic.pytgcalls.leave_group_call(chat_id)
        else:
            callsmusic.pytgcalls.change_stream(
                chat_id, queues.get(chat_id)["file"]
            )

    qeue = que.get(chat_id)
    if qeue:
        skip = qeue.pop(0)
    if not qeue:
        return
    await message.reply_text(f"⏭ **Pɪᴋᴀ Pɪᴋᴀ, ʏᴏᴜ sᴋɪᴘᴘᴇᴅ ᴛᴏ ᴛʜᴇ ɴᴇxᴛ sᴏɴɢ!**")


@Client.on_message(filters.command("cache"))
@errors
async def admincache(client, message: Message):
    set(
        message.chat.id,
        [
            member.user
            for member in await message.chat.get_members(filter="administrators")
        ],
    )
    await message.reply_text("✅ Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ʀᴇғʀᴇsʜᴇᴅ !!")
