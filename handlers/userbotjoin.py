from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant
import asyncio
from helpers.decorators import authorized_users_only, errors
from callsmusic.callsmusic import client as USER
from config import SUDO_USERS


@Client.on_message(filters.command(["userbotjoin"]) & ~filters.private & ~filters.bot)
@authorized_users_only
@errors
async def addchannel(client, message):
    chid = message.chat.id
    try:
        invitelink = await client.export_chat_invite_link(chid)
    except:
        await message.reply_text(
            "<b>Pɪᴋᴀ Pɪᴋᴀ, ᴍᴀᴋᴇ ᴍᴇ ᴀs ᴀᴅᴍɪɴ ғɪʀsᴛ !!</b>",
        )
        return

    try:
        user = await USER.get_me()
    except:
        user.first_name = "helper"

    try:
        await USER.join_chat(invitelink)
        await USER.send_message(message.chat.id, "🤖: Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ᴊᴏɪɴᴇᴅ ʜᴇʀᴇ ғᴏʀ ᴘʟᴀʏɪɴᴛ ᴍᴜsɪᴄ ᴏɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ.")
    except UserAlreadyParticipant:
        await message.reply_text(
            "<b>Pɪᴋᴀ Pɪᴋᴀ, ʜᴇᴀʟᴘᴇʀ ʀᴇᴀᴅʏ ɪɴ ʏᴏᴜʀ ᴄʜᴀᴛ ʙᴀʙʏ.</b>",
        )
    except Exception as e:
        print(e)
        await message.reply_text(
            f"<b>Pɪᴋᴀ Pɪᴋᴀ, ⛑ ғʟᴏᴏᴅ ᴡᴀɪᴛ ᴇʀʀᴏʀ ⛑\n{user.first_name} ᴄᴀɴ'ᴛ ᴊᴏɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴅᴜᴇ ᴛᴏ ᴍᴀɴʏ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ғᴏʀ ᴜsᴇʀʙᴏᴛ !! ᴍᴀᴋs sᴜʀᴇ ᴛʜᴇ ᴜsᴇʀ ɪs ɴᴏᴛ ʙᴀɴɴᴇᴅ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ."
                        f"\n\nᴏʀ ᴀᴅᴅ @{ASSISTANT_NAME} ᴍᴀɴᴜᴀʟʟʏ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</b>",
        )
        return
    await message.reply_text(
        "<b>Pɪᴋᴀ Pɪᴋᴀ, ʜᴇʟᴘᴇʀ ᴜsᴇʀʙᴏᴛ ᴊᴏɪɴᴇᴅ ʏᴏᴜʀ ᴄʜᴀᴛ.</b>",
    )


@USER.on_message(filters.group & filters.command(["userbotleave"]))
@authorized_users_only
async def rem(USER, message):
    try:
        await USER.leave_chat(message.chat.id)
    except:
        await message.reply_text(
            f"<b>Pɪᴋᴀ Pɪᴋᴀ, ᴜsᴇʀ ᴄᴏᴜʟᴅ'ɴᴛ ʟᴇᴀᴠᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ !! ᴍᴀʏ ʙᴇ ғʟᴏᴏᴅᴡᴀɪᴛs."
            "\n\nᴏʀ ᴍᴀɴᴜᴀʟʟʏ ᴋɪᴄᴋ ᴍᴇ ғʀᴏᴍ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ.</b>",
        )
        return
    
@Client.on_message(filters.command(["userbotleaveall"]))
async def bye(client, message):
    if message.from_user.id in SUDO_USERS:
        left=0
        failed=0
        lol = await message.reply("Pɪᴋᴀ Pɪᴋᴀ, ᴀssɪsᴛᴀɴᴛ ʟᴇᴀᴠɪɴᴛ ᴀʟʟ ᴄʜᴀᴛs.")
        async for dialog in USER.iter_dialogs():
            try:
                await USER.leave_chat(dialog.chat.id)
                left = left+1
                await lol.edit(f"Pɪᴋᴀ Pɪᴋᴀ, ᴀssɪsᴛᴀɴᴛ ʟᴇᴀᴠɪɴɢ... ʟᴇғᴛ : {left} ᴄʜᴀᴛs. ғᴀɪʟᴇᴅ : {failed} ᴄʜᴀᴛs.")
            except:
                failed=failed+1
                await lol.edit(f"Assistant leaving... ʟᴇғᴛ : {left} ᴄʜᴀᴛs. ғᴀɪʟᴇᴅ : {failed} ᴄʜᴀᴛs.")
            await asyncio.sleep(0.7)
        await client.send_message(message.chat.id, f"ʟᴇғᴛ : {left} ᴄʜᴀᴛs. ғᴀɪʟᴇᴅ : {failed} ᴄʜᴀᴛs.")
