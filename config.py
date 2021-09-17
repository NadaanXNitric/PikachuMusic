import os
from os import getenv
from dotenv import load_dotenv

if os.path.exists("local.env"):
    load_dotenv("local.env")

load_dotenv()
que = {}
SESSION_NAME = getenv("SESSION_NAME", "session")
BOT_TOKEN = getenv("BOT_TOKEN")
BOT_NAME = getenv("BOT_NAME", "「ᴘɪᴋᴀᴄʜᴜχᴅ」")
BG_IMAGE = getenv("BG_IMAGE", None)
THUMB_IMG = getenv("THUMB_IMG", "https://telegra.ph/file/707fda22ee5dc349b50ab.jpg")
AUD_IMG = getenv("AUD_IMG", None)
QUE_IMG = getenv("QUE_IMG", None)
admins = {}
API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
BOT_USERNAME = getenv("BOT_USERNAME", "PikachuXdBot")
ASSISTANT_NAME = getenv("ASSISTANT_NAME", "PikachuXdBot")
GROUP_SUPPORT = getenv("GROUP_SUPPORT", "Sanki_BOTs_Support")
UPDATES_CHANNEL = getenv("UPDATES_CHANNEL", "Sanki_BOTs")
OWNER_NAME = getenv("OWNER_NAME", "iTs_Nitric") # isi dengan username kamu tanpa simbol @
DEV_NAME = getenv("DEV_NAME", "iTs_Nitric")
PMPERMIT = getenv("PMPERMIT", None)

DURATION_LIMIT = int(getenv("DURATION_LIMIT", "90"))

COMMAND_PREFIXES = list(getenv("COMMAND_PREFIXES", "/ ! .").split())

SUDO_USERS = list(map(int, getenv("SUDO_USERS").split()))
