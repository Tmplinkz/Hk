# ==================== IMPORTS ====================
from os import path as ospath, getenv, makedirs, remove
import os
from logging import basicConfig, INFO, getLogger
from logging.handlers import RotatingFileHandler
from subprocess import run as srun, DEVNULL
from dotenv import load_dotenv
from io import BytesIO, StringIO
import time
import logging
import sys

# ==================== LOGGING SETUP (Clean & Professional) ====================
if os.path.exists("log.txt"):
    try:
        remove("log.txt")
    except:
        pass

basicConfig(
    format="[%(asctime)s] [%(name)s | %(levelname)s] - %(message)s [%(filename)s:%(lineno)d]",
    datefmt="%m/%d/%Y, %H:%M:%S %p",
    level=INFO,
    handlers=[
        RotatingFileHandler("log.txt", maxBytes=10*1024*1024, backupCount=10),
        logging.StreamHandler()
    ]
)

LOGGER = getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# ==================== LOAD ENV ====================
# Load env file if exists
load_dotenv('config.env', override=True)

# ==================== BOT START TIME ====================
botStartTime = time.time()

# ==================== ALL CONFIG VARIABLES (Safe & Clean) ====================

# Telegram API
API_ID = int(getenv("API_ID", "0") or "0")
API_HASH = getenv("API_HASH", "").strip()
BOT_TOKEN = getenv("BOT_TOKEN", "").strip()

# Helper function to validate critical config variables
def _validate_config(var_name, value, check_zero=False):
    """Validate that a critical config variable is set"""
    is_invalid = (not value or (check_zero and value == 0))
    if is_invalid:
        raise RuntimeError(f"❌ {var_name} is not set in config.env! Please configure it properly.")

# Validate critical variables
_validate_config("API_ID", API_ID, check_zero=True)
_validate_config("API_HASH", API_HASH)
_validate_config("BOT_TOKEN", BOT_TOKEN)

# Session & Database
SESSION_NAME = getenv("SESSION_NAME", "VideoEncoderBot")
MONGO_URI = getenv("MONGO_URI")

# Folders (Auto fix trailing slash)
DOWNLOAD_DIR = getenv("DOWNLOAD_DIR", "VideoEncoder/downloads/").rstrip("/") + "/"
ENCODE_DIR = getenv("ENCODE_DIR", "VideoEncoder/encodes/").rstrip("/") + "/"

# Google Drive & Index (Optional)
DRIVE_DIR = getenv("DRIVE_DIR", "").strip()
INDEX_URL = getenv("INDEX_URL", "").strip()

if DRIVE_DIR and not DRIVE_DIR.endswith("/"):
    DRIVE_DIR += "/"
if INDEX_URL and not INDEX_URL.endswith("/"):
    INDEX_URL += "/"


OWNER_ID = getenv("OWNER_ID", "0")

SUDO_USERS = getenv("SUDO_USERS")
EVERYONE_CHATS = getenv("EVERYONE_CHATS")

# Log Channel
LOG_CHANNEL = getenv("LOG_CHANNEL", "").strip()

UPSTREAM_REPO = getenv("UPSTREAM_REPO", "").strip()
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "").strip()

# Progress Format
PROGRESS = """
• {0} of {1}
• Speed: {2}/s
• ETA: {3}
"""

# Video Mimetypes
video_mimetype = [
    "video/x-flv", "video/mp4", "application/x-mpegURL", "video/MP2T",
    "video/3gpp", "video/quicktime", "video/x-msvideo", "video/x-ms-wmv",
    "video/x-matroska", "video/webm", "video/x-m4v", "video/mpeg"
]

# ==================== CREATE REQUIRED FOLDERS ====================
for folder in [DOWNLOAD_DIR, ENCODE_DIR, "VideoEncoder/utils/extras"]:
    makedirs(folder, exist_ok=True)

# ==================== AUTO UPDATER (Safe & Silent) ====================
if UPSTREAM_REPO:
    try:
        if os.path.exists('.git'):
            srun(["rm", "-rf", ".git"], stdout=DEVNULL, stderr=DEVNULL)

        cmd = f"""
        git init -q &&
        git config --global user.email "auto@update.com" &&
        git config --global user.name "VideoEncoderBot" &&
        git add . &&
        git commit -sm "update" -q &&
        git remote add origin "{UPSTREAM_REPO}" &&
        git fetch origin -q &&
        git reset --hard origin/{UPSTREAM_BRANCH} -q
        """
        result = srun(cmd, shell=True, stdout=DEVNULL, stderr=DEVNULL)
        if result.returncode == 0:
            LOGGER.info(f"Bot Auto-Updated → {UPSTREAM_REPO} ({UPSTREAM_BRANCH})")
        else:
            LOGGER.warning("Auto-update failed! Check UPSTREAM_REPO & BRANCH.")
    except Exception as e:
        LOGGER.error(f"Updater Error: {e}")
else:
    LOGGER.info("UPSTREAM_REPO not set → No auto-update.")

# ==================== FINAL STARTUP LOG ====================
LOGGER.info("═" * 50)
LOGGER.info("   VIDEO ENCODER BOT STARTED SUCCESSFULLY!")
LOGGER.info("═" * 50)
LOGGER.info(f"Owner ID     : {OWNER_ID[0]}")
if DRIVE_DIR: LOGGER.info(f"Drive Folder : {DRIVE_DIR}")
if INDEX_URL: LOGGER.info(f"Index Link   : {INDEX_URL}")
if LOG_CHANNEL: LOGGER.info(f"Log Channel  : {LOG_CHANNEL}")
LOGGER.info("═" * 50)
