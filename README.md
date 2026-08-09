# Rex Deploy – Heroku Deployment via Google Colab

A simple method to deploy your **Aiogram Encoding Bot** to **Heroku** using a **Google Colab** notebook.

## 🚀 Deploy Steps

1. Open the Colab notebook in this repository.
2. Login to Heroku with your email/API key.
3. Create or select your Heroku app.
4. Configure the bot using one of the supported methods:
   - **Manual** – enter the settings directly in Colab.
   - **Gist URL** – provide a raw `config.env` URL.
   - **Upload File** – upload an existing `config.env`.
5. Deploy the configured app.

The deployment creates `config.env` and starts the encoder with:

```bash
python3 update.py && python3 -m VideoEncoder
```

## 📋 Configuration

### Required

- `BOT_TOKEN` – Telegram Bot Token from `@BotFather`.
- `OWNER_ID` – Telegram user ID of the bot owner.
- `LOG_CHANNEL` – Telegram channel ID used for logging.
- `MONGO_URI` – MongoDB connection string.

### Optional

- `SUDO_USERS` – comma-separated user IDs with sudo access.
- `EVERYONE_CHATS` – comma-separated chat IDs where everyone can use the bot.
- `DOWNLOAD_DIR` – download directory (default: `VideoEncoder/downloads/`).
- `ENCODE_DIR` – encode directory (default: `VideoEncoder/encodes/`).
- `INDEX_URL` – optional index URL.
- `UPSTREAM_REPO` – repository URL used for automatic updates.
- `UPSTREAM_BRANCH` – branch used for automatic updates (default: `main`).

## ⚠️ Aiogram migration note

This deployment repository is configured for **Aiogram 3.x / Telegram Bot API**.

You do **not** need:

- `API_ID`
- `API_HASH`
- `SESSION_NAME`
- Pyrogram
- TgCrypto
- Google Drive API credentials/dependencies

Only a Telegram **Bot Token** is required for Telegram authentication.

## 📌 Configuration loading

The encoder loads `config.env` using `python-dotenv`. Keep the file private and never commit secrets to a public repository.

## 🔧 Troubleshooting

- **Bot not starting:** check the Heroku logs and verify `BOT_TOKEN`.
- **Database errors:** verify `MONGO_URI` and MongoDB network access.
- **Encoding errors:** verify FFmpeg installation and available disk/RAM.
- **Deployment errors:** verify your Heroku app name, credentials, and required config values.
