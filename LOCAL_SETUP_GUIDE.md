# Local Setup Guide - Test in 5 Minutes

## Step 1: Download the Code

Download or clone this entire `/root/binding/` directory to your local machine.

## Step 2: Install Dependencies

```bash
cd binding
pip install -r requirements.txt
```

## Step 3: Get Discord OAuth Credentials (Required)

1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Name it "Web3 Community Test"
4. Go to "OAuth2" tab in left sidebar
5. Under "Redirects", add: `http://localhost:8000/auth/discord/callback`
6. Copy your **Client ID**
7. Copy your **Client Secret**

## Step 4: Get Telegram Credentials (Optional but recommended)

1. Open Telegram, search for `@BotFather`
2. Send `/newbot`
3. Follow prompts to create bot
4. Copy the **Bot Token** (looks like: `123456:ABC-DEF...`)
5. Your bot username is what you chose (e.g., `my_test_bot`)

## Step 5: Get Twitter/X Credentials (Optional)

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Create a new project and app
3. Enable OAuth 2.0
4. Add callback URL: `http://localhost:8000/auth/twitter/callback`
5. Copy **Client ID** and **Client Secret**

## Step 6: Create .env File

Create a file named `.env` in the binding directory:

```env
STORAGE_BACKEND=csv
CSV_DATA_DIR=data
SECRET_KEY=your-random-secret-key-here-change-this

DISCORD_CLIENT_ID=paste_your_discord_client_id_here
DISCORD_CLIENT_SECRET=paste_your_discord_client_secret_here
DISCORD_REDIRECT_URI=http://localhost:8000/auth/discord/callback

TELEGRAM_BOT_TOKEN=paste_your_bot_token_here
TELEGRAM_BOT_USERNAME=your_bot_username

TWITTER_CLIENT_ID=paste_your_twitter_client_id_here
TWITTER_CLIENT_SECRET=paste_your_twitter_client_secret_here
TWITTER_REDIRECT_URI=http://localhost:8000/auth/twitter/callback

BASE_URL=http://localhost:8000
```

## Step 7: Run the App

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Step 8: Test It

1. Open browser: `http://localhost:8000`
2. Click "Sign in with Discord"
3. Authorize the app
4. You'll land on the dashboard
5. Try connecting Telegram or X

## Step 9: View Your Data

Open these files to see your data:
- `data/users.csv`
- `data/bindings.csv`

You can open them in Excel, Google Sheets, or any text editor!

## Troubleshooting

**"Client ID not found"**
- Make sure you copied the credentials correctly to `.env`
- Restart the server after editing `.env`

**"Redirect URI mismatch"**
- Ensure the redirect URI in Discord/Twitter dashboard exactly matches:
  - `http://localhost:8000/auth/discord/callback`
  - `http://localhost:8000/auth/twitter/callback`

**"Module not found"**
- Run: `pip install -r requirements.txt`

## Minimum Test (Discord Only)

If you only want to test the core flow, you only need Discord credentials:

1. Setup Discord OAuth (Steps 3)
2. Create `.env` with just Discord credentials:
```env
STORAGE_BACKEND=csv
SECRET_KEY=test-secret-key

DISCORD_CLIENT_ID=your_id
DISCORD_CLIENT_SECRET=your_secret
DISCORD_REDIRECT_URI=http://localhost:8000/auth/discord/callback

TELEGRAM_BOT_TOKEN=dummy
TELEGRAM_BOT_USERNAME=dummy
TWITTER_CLIENT_ID=dummy
TWITTER_CLIENT_SECRET=dummy
TWITTER_REDIRECT_URI=http://localhost:8000/auth/twitter/callback

BASE_URL=http://localhost:8000
```

3. Run the app and test Discord sign-in
4. Telegram/Twitter buttons won't work but you'll see the flow

## Accessing from Phone/Other Device on Same Network

If you want to test from your phone:

1. Find your computer's local IP:
   - Windows: `ipconfig` (look for IPv4)
   - Mac/Linux: `ifconfig` or `ip addr`

2. Run with your local IP:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Update `.env`:
```env
BASE_URL=http://192.168.1.XXX:8000
DISCORD_REDIRECT_URI=http://192.168.1.XXX:8000/auth/discord/callback
TWITTER_REDIRECT_URI=http://192.168.1.XXX:8000/auth/twitter/callback
```

4. Update Discord/Twitter dashboard with new redirect URIs

5. Access from phone: `http://192.168.1.XXX:8000`

Note: Telegram OAuth may not work from mobile browser due to Telegram app redirects.
