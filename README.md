# Sphinx Protocol Account Binding

OAuth-based account binding system for Discord and Telegram.

## Quick Start

### Development (Local)
```bash
./start_dev.sh
```
Open http://localhost:8000

### Production (HTTPS)
```bash
sudo bash setup_https.sh
```
Follow the prompts. See [DEPLOYMENT.md](DEPLOYMENT.md) for details.

## Setup

1. **Install dependencies:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Download ngrok (for local development):**
```bash
# Download from https://ngrok.com/download
# Linux example:
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xvzf ngrok-v3-stable-linux-amd64.tgz
rm ngrok-v3-stable-linux-amd64.tgz
# Add your authtoken: ./ngrok authtoken YOUR_TOKEN
```

3. **Configure `.env`:**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Run:**
```bash
./start_dev.sh
```

## Project Structure
```
app/
├── main.py              # FastAPI app
├── routes/
│   └── auth.py          # OAuth routes
├── oauth/
│   ├── discord.py       # Discord OAuth
│   ├── telegram_authz.py
│   └── telegram_webhook.py
├── storage/
│   └── user_storage.py  # CSV storage
└── session.py           # Session management

templates/
├── index.html           # Login page
└── dashboard.html       # Dashboard

static/
└── styles.css           # Styling
```

## Features
- ✅ Discord OAuth 2.0
- ✅ Telegram Bot Auth
- ✅ CSV-based storage
- ✅ Session management
- ✅ HTTPS support
- ✅ Auto-renewal SSL

## Tech Stack
- FastAPI
- Python 3.12
- Nginx (production)
- Let's Encrypt (SSL)

## Documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Full deployment guide
- `.env.example` - Configuration reference

## License
Proprietary - Sphinx Protocol
