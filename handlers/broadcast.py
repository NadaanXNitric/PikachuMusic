# Copyright (C) 2021 By KennedyProject


import asyncio

from pyrogram import Client, filters
from pyrogram.types import Dialog, Chat, Message
from pyrogram.errors import UserAlreadyParticipant

from callsmusic.callsmusic import client as kennedy
from config import SUDO_USERS

@Client.on_message(filters.command(["gcast"]))
async def broadcast(_, message: Message):
    sent=0
    failed=0
    if message.from_user.id not in SUDO_USERS:
        return
    else:
        wtf = await message.reply("`Pɪᴋᴀ Pɪᴋᴀ, sᴛᴀʀᴛᴇᴅ ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ...`")
        if not message.reply_to_message:
            await wtf.edit("Pɪᴋᴀ Pɪᴋᴀ, ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ sᴛᴀʀᴛ ʙʀᴏᴀᴅᴄᴀsᴛ.")
            return
        lmao = message.reply_to_message.text
        async for dialog in kennedy.iter_dialogs():
            try:
                await kennedy.send_message(dialog.chat.id, lmao)
                sent = sent+1
                await wtf.edit(f"`Pɪᴋᴀ Pɪᴋᴀ, ᴀᴍ ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴘʟᴢ ᴡᴀɪᴛ...` \n\n**• Sᴇɴᴛ ᴛᴏ :** `{sent}` ᴄʜᴀᴛs. \n**• Fᴀɪʟᴇᴅ ɪɴ :** {failed} ᴄʜᴀᴛs.")
                await asyncio.sleep(3)
            except:
                failed=failed+1
        await message.reply_text(f"`Pɪᴋᴀ Pɪᴋᴀ, Gᴄᴀsᴛ sᴜᴄᴇssғᴜʟʟʏ ᴅᴏɴᴇ...` \n\n**• Sᴇɴᴛ ᴛᴏ :** `{sent}` ᴄʜᴀᴛs. \n**• Fᴀɪʟᴇᴅ ɪɴ :** {failed} ᴄʜᴀᴛs.")
