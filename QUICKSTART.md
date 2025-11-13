# Quick Start Guide

Get up and running in 5 minutes with CSV storage (no database required).

## Prerequisites

- Python 3.9 or higher
- Discord, Telegram, and/or Twitter OAuth credentials

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure OAuth Credentials

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your OAuth credentials:

```env
STORAGE_BACKEND=csv

DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret
DISCORD_REDIRECT_URI=http://localhost:8000/auth/discord/callback

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_BOT_USERNAME=your_bot_username

TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret
TWITTER_REDIRECT_URI=http://localhost:8000/auth/twitter/callback

BASE_URL=http://localhost:8000
```

## Step 3: Run the Application

```bash
uvicorn app.main:app --reload
```

## Step 4: Open Browser

Visit: http://localhost:8000

## Step 5: View Your Data

Your data is stored in CSV files:
- `data/users.csv` - All users
- `data/bindings.csv` - All account bindings

Open these files with Excel, Google Sheets, or any spreadsheet app.

## Getting OAuth Credentials

### Discord
1. Visit https://discord.com/developers/applications
2. Click "New Application"
3. Go to "OAuth2" tab
4. Add redirect URI: `http://localhost:8000/auth/discord/callback`
5. Copy Client ID and Client Secret

### Telegram
1. Open Telegram and message @BotFather
2. Send `/newbot` and follow instructions
3. Copy the bot token
4. Your bot username is what you chose during creation

### X (Twitter)
1. Visit https://developer.twitter.com/portal
2. Create a new project and app
3. Enable OAuth 2.0
4. Add callback: `http://localhost:8000/auth/twitter/callback`
5. Copy Client ID and Client Secret

## Testing the Flow

1. Click "Sign in with Discord" - this creates your user account and logs you in
2. After Discord auth, you're redirected to your dashboard
3. See your Discord account connected with ✓ indicator
4. Click "Connect Telegram" or "Connect X" to add additional platforms
5. Watch status indicators update in real-time
6. Try re-authenticating any platform to update tokens
7. Check `data/` folder to see your data in CSV format

## Using the Dashboard

**View Your Accounts:**
- See all connected platforms with usernames and IDs
- Status indicators show what's connected (✓) and what's not (✗)
- Requirements box shows completion status

**Re-authenticate:**
- Click any "Re-authenticate" button to refresh OAuth tokens
- Useful if you change usernames or tokens expire

**Sign Out:**
- Click "Sign Out" button in top right
- Session cleared, but all bindings remain
- Sign back in anytime with Discord

## Switching to PostgreSQL

To use PostgreSQL instead of CSV:

1. Install and start PostgreSQL
2. Create database: `createdb binding_db`
3. Change `.env`: `STORAGE_BACKEND=sql`
4. Update `DATABASE_URL` in `.env`
5. Restart application

## Troubleshooting

**Port already in use:**
```bash
uvicorn app.main:app --reload --port 8001
```
Update redirect URIs to match the new port.

**Module not found:**
```bash
pip install -r requirements.txt
```

**OAuth error:**
- Verify credentials in `.env`
- Check redirect URIs match exactly
- Ensure BASE_URL is correct

**CSV files not created:**
- Check `CSV_DATA_DIR` setting
- Verify write permissions in project directory

## Next Steps

- Read [README.md](README.md) for full documentation
- See [CSV_STORAGE_GUIDE.md](CSV_STORAGE_GUIDE.md) for CSV tips
- Customize the frontend in `templates/index.html`
- Extend with points tracking or other features
