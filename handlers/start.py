from time import time
from datetime import datetime
from config import BOT_USERNAME, BOT_NAME, ASSISTANT_NAME, OWNER_NAME, UPDATES_CHANNEL, GROUP_SUPPORT
from helpers.filters import command
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from helpers.decorators import authorized_users_only


START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ('week', 60 * 60 * 24 * 7),
    ('day', 60 * 60 * 24),
    ('hour', 60 * 60),
    ('min', 60),
    ('sec', 1)
)

async def _human_time_duration(seconds):
    if seconds == 0:
        return 'inf'
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append('{} {}{}'
                         .format(amount, unit, "" if amount == 1 else "s"))
    return ', '.join(parts)


@Client.on_message(command("start") & filters.private & ~filters.edited)
async def start_(client: Client, message: Message):
    await message.reply_text(
        f"""<b>✨ Pɪᴋᴀ Pɪᴋᴀ, Wᴇʟᴄᴏᴍᴇ</b> {query.from_user.mention}!\n\n💭 [{BOT_NAME}](t.me/{UPDATES_CHANNEL}) <b>Aʟʟᴏᴡs Yᴏᴜ Tᴏ Pʟᴀʏ Mᴜsɪᴄ Oɴ Gʀᴏᴜᴘs Tʜʀᴏᴜɢʜ Tʜᴇ Nᴇᴡ Tᴇʟᴇɢʀᴀᴍ's Vᴏɪᴄᴇ Cʜᴀᴛs!</b>\n\n💡 <b>Fɪɴᴅ Oᴜᴛ</b> Aʟʟ Tʜᴇ <b>Bᴏᴛ</b>'s <b>Cᴏᴍᴍᴀᴍᴅs</b> Aɴᴅ Hᴏᴡ Tʜᴇʏ <b>Wᴏʀᴋ</b> Bʏ Cʟɪᴄᴋɪɴɢ Oɴ Tʜᴇ » 📚 <b>Cᴏᴍᴍᴀɴᴅs</b> Bᴜᴛᴛᴏɴ!""",
        reply_markup=InlineKeyboardMarkup(
           [ 
                [
                    InlineKeyboardButton(
                        "➕ Sᴜᴍᴍᴏɴ Mᴇ ➕", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
                ],[
                    InlineKeyboardButton(
                         "📚 Dᴇᴍᴏ", callback_data="https://t.me/Dramaa_Club"
                    ),
                    InlineKeyboardButton(
                        "❤️ Dᴏɴᴀᴛᴇ", url=f"https://t.me/{OWNER_USERNAME}")
                ],[
                    InlineKeyboardButton(
                        "👥 Oғғɪᴄɪᴀʟ Gʀᴏᴜᴘ", url=f"https://t.me/{GROUP_SUPPORT}"
                    ),
                    InlineKeyboardButton(
                        "📣 Oғғɪᴄɪᴀʟ Cʜᴀɴɴᴇʟ", url=f"https://t.me/{UPDATES_CHANNEL}")
                ],[
                    InlineKeyboardButton(
                        "❗️ Iɴғᴏ & Aʙᴏᴜᴛ 👨‍💻", callback_data="cbinfo")
                ],[
                    InlineKeyboardButton(
                        "🧪 Sᴏᴜʀᴄᴇ Cᴏᴅᴇ 🧪", url="https://t.me/Sanki_BOTs"
                    )
                ]
            ]
        ),


@Client.on_message(command(["start", f"start@{BOT_USERNAME}"]) & filters.group & ~filters.edited)
async def start(client: Client, message: Message):
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await message.reply_text(
        f"""✅ **Pɪᴋᴀ Pɪᴋᴀ, ʙᴏᴛ ɪs ʀᴜɴɴɪɴɢ**\n<b>⚡ **ᴜᴘᴛɪᴍᴇ :**</b> `{uptime}`""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "👥 ɢʀᴏᴜᴘ", url=f"https://t.me/Dramaa_Club"
                    ),
                    InlineKeyboardButton(
                        "ᴄʜᴀɴɴᴇʟ 📣", url=f"https://t.me/Sanki_BOTs"
                    )
                ]
            ]
        )
    )

@Client.on_message(command(["help", f"help@{BOT_USERNAME}"]) & filters.group & ~filters.edited)
async def help(client: Client, message: Message):
    await message.reply_text(
        f"""<b>👋🏻 Pɪᴋᴀ Pɪᴋᴀ, {message.from_user.mention()}, ᴘʟᴇᴀsᴇ ᴛᴀᴘ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ sᴇᴇ ᴛʜᴇ ʜᴇʟᴘ ᴍᴇssᴀɢᴇ ʏᴏᴜ ᴄᴀɴ ʀᴇᴀᴅ ғᴏʀ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ</b>""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="❔ ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ", url=f"https://t.me/PikachuXdBot?start=help"
                    )
                ]
            ]
        )
    )

@Client.on_message(command("help") & filters.private & ~filters.edited)
async def help_(client: Client, message: Message):
    await message.reply_text(
        f"""<b>👋🏻 Pɪᴋᴀ Pɪᴋᴀ, {message.from_user.mention()}, ᴡᴇʟᴄᴏᴍᴇ ᴛo ʜᴇʟᴘ ᴍᴇɴᴜ ✨
\n📌HOW TO USE ME ?
\n1. first add me to your group.
2. promote me as admin and give all permission.
3. then, add @PikachuXdAssistant to your group or type /userbotjoin.
3. make sure you turn on the voice chat first before start playing music.
\n📌**commands for all user:**
\n/play (song name) - play song from youtube
/stream (reply to audio) - play song using audio file
/playlist - show the list song in queue
/current - show the song in streaming
/song (song name) - download song from youtube
/search (video name) - search video from youtube detailed
/vsong (video name) - download video from youtube detailed
/vk (song name) - download song from inline mode
\n📌 **commands for admins:**
\n/player - open music player settings panel
/pause - pause the music streaming
/resume - resume the music was paused
/skip - skip to the next song
/end - stop music streaming
/userbotjoin - invite assistant join to your group
/reload - for refresh the admin list
/cache - for cleared admin cache
/musicplayer (on / off) - disable / enable music player in your group
\n🎧 channel streaming commands:
\n/cplay - stream music on channel voice chat
/cplayer - show the song in streaming
/cpause - pause the streaming music
/cresume - resume the streaming was paused
/cskip - skip streaming to the next song
/cend - end the streaming music
/admincache - refresh the admin cache
\n🧙‍♂️ command for sudo users:
\n/userbotleaveall - order the assistant to leave from all group
/gcast - send a broadcast message trought the assistant
\n📌 **commands for fun:**
\n/lyric - (song name) lyrics scrapper
</b>""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "👥 ɢʀᴏᴜᴘ", url=f"https://t.me/Dramaa_Club"
                    ),
                    InlineKeyboardButton(
                        "ᴄʜᴀɴɴᴇʟ 📣", url=f"https://t.me/Sanki_BOTs"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "💚 ᴅᴇᴠᴇʟᴏᴘᴇʀ 💚", url=f"https://t.me/iTs_Nitric"
                    )
                ]
            ]
        )
    )


@Client.on_message(command(["ping", f"ping@{BOT_USERNAME}"]) & ~filters.edited)
async def ping_pong(client: Client, message: Message):
    start = time()
    m_reply = await message.reply_text("Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ᴘɪɴɢɪɴɢ...")
    delta_ping = time() - start
    await m_reply.edit_text(
        "`Pɪᴋᴀ Pɪᴋᴀ, ᴘɪɴɢ ᴘᴏɴɢ !!`\n"
        f"⚡️ `{delta_ping * 1000:.3f} Ms`"
    )


@Client.on_message(command(["uptime", f"uptime@{BOT_USERNAME}"]) & ~filters.edited)
@authorized_users_only
async def get_uptime(client: Client, message: Message):
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await message.reply_text(
        "🤖 Pɪᴋᴀ Pɪᴋᴀ, ᴍɪɴᴇ sᴛᴀᴛᴜs :\n"
        f"• **ᴜᴘᴛɪᴍᴇ :** `{uptime}`\n"
        f"• **sᴛᴀʀᴛ ᴛɪᴍᴇ :** `{START_TIME_ISO}`"
    )
