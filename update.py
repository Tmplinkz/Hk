# ==================== IMPORTS ====================
from os import path as ospath, getenv, makedirs, remove
import os
import shutil
from logging import basicConfig, INFO, getLogger
from logging.handlers import RotatingFileHandler
from subprocess import run as srun, DEVNULL
from dotenv import load_dotenv
from io import BytesIO, StringIO
import time
import logging
import sys

# ==================== LOGGING SETUP ====================
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
load_dotenv('config.env', override=False)

# ==================== BOT START TIME ====================
botStartTime = time.time()

# ==================== CONFIG VARIABLES ====================

# Telegram API
API_ID = int(getenv("API_ID", "0") or "0")
API_HASH = getenv("API_HASH", "").strip()
BOT_TOKEN = getenv("BOT_TOKEN", "").strip()

# Session & Database
SESSION_NAME = getenv("SESSION_NAME", "VideoEncoderBot")
MONGO_URI = getenv("MONGO_URI")

# Folders
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

# ==================== INSTALL FFMPEG ====================
FFMPEG_VERSION = "n7.1"

def _ffmpeg_ok():
    """Returns True if ffmpeg is installed, working, and is the BtbN static build."""
    try:
        result = srun(
            ["ffmpeg", "-version"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0 and "BtbN" in result.stdout
    except Exception:
        return False

def _install_ffmpeg():
    """Downloads and installs the BtbN static ffmpeg build. Returns True on success."""
    try:
        arch_raw = srun(
            "arch | sed 's/aarch64/arm64/' | sed 's/x86_64/64/'",
            shell=True, capture_output=True, text=True, timeout=10
        ).stdout.strip()
        ffmpeg_url = (
            f"https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/"
            f"ffmpeg-{FFMPEG_VERSION}-latest-linux{arch_raw}-gpl-{FFMPEG_VERSION[1:]}.tar.xz"
        )
        result = srun(
            f"wget -q '{ffmpeg_url}' -O /tmp/ffmpeg.tar.xz && "
            "tar -xf /tmp/ffmpeg.tar.xz -C /tmp && "
            "cp /tmp/ffmpeg-*/bin/* /usr/local/bin/ && "
            "chmod +x /usr/local/bin/ffmpeg /usr/local/bin/ffprobe && "
            "rm -rf /tmp/ffmpeg*",
            shell=True, stdout=DEVNULL, stderr=DEVNULL, timeout=120
        )
        return _ffmpeg_ok()
    except Exception as e:
        LOGGER.error(f"ffmpeg install error: {e}")
        return False

if _ffmpeg_ok():
    LOGGER.info("ffmpeg already installed and verified.")
else:
    for attempt in range(1, 4):
        LOGGER.info(f"Installing static ffmpeg (attempt {attempt}/3)...")
        if _install_ffmpeg():
            LOGGER.info(f"Static ffmpeg {FFMPEG_VERSION} installed successfully.")
            break
        LOGGER.warning(f"ffmpeg install attempt {attempt} failed.")
        time.sleep(3)
    else:
        LOGGER.error("ffmpeg installation failed after 3 attempts! Encoding will not work.")

# ==================== AUTO UPDATER ====================
if UPSTREAM_REPO:
    try:
        # Save update.py and run.sh before git wipes the directory
        update_py_path = os.path.abspath(__file__)
        run_sh_path = os.path.join(os.path.dirname(update_py_path), "run.sh")

        with open(update_py_path, "r") as f:
            update_py_content = f.read()

        run_sh_content = None
        if os.path.exists(run_sh_path):
            with open(run_sh_path, "r") as f:
                run_sh_content = f.read()

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
            LOGGER.info(f"Bot Auto-Updated → Upstream Repo! ({UPSTREAM_BRANCH})")

            # Restore update.py and run.sh so restarts still work
            with open(update_py_path, "w") as f:
                f.write(update_py_content)
            LOGGER.info("Restored update.py after git reset.")

            if run_sh_content:
                with open(run_sh_path, "w") as f:
                    f.write(run_sh_content)
                os.chmod(run_sh_path, 0o755)
                LOGGER.info("Restored run.sh after git reset.")

            # Install dependencies from upstream requirements.txt
            if os.path.exists("requirements.txt"):
                LOGGER.info("Installing upstream dependencies...")
                pip_result = srun(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt",
                     "-q", "--no-warn-script-location"],
                    stdout=DEVNULL, stderr=DEVNULL
                )
                if pip_result.returncode == 0:
                    LOGGER.info("Dependencies installed successfully.")
                else:
                    LOGGER.warning("pip install failed! Bot may crash on missing modules.")
            else:
                LOGGER.warning("No requirements.txt found after update.")

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
        
