# Configuration Management Guide

This app uses a simple JSON-based configuration system to easily switch between development and production.

## Files

- **`config.json`** - Contains all environment configurations
- **`apply_config.py`** - Applies config to .env file
- **`switch_config.py`** - Quick switcher between environments

---

## Quick Start

### View Current Configuration
```bash
cat config.json | grep -A2 '"current"'
```

### Switch to Production (When Ready)
```bash
# 1. First, edit config.json and replace YOUR_DOMAIN_HERE with your actual domain
nano config.json

# 2. Switch and apply
python3 switch_config.py production
```

### Switch Back to Development
```bash
python3 switch_config.py development
```

---

## Before Going to Production

### Step 1: Update config.json

Edit `config.json` and replace all instances of `YOUR_DOMAIN_HERE`:

```json
{
  "production": {
    "ENVIRONMENT": "production",
    "BASE_URL": "https://binding.example.com",  // ← Your domain
    "DISCORD_REDIRECT_URI": "https://binding.example.com/auth/discord/callback"  // ← Your domain
  }
}
```

### Step 2: What URLs Change

When you switch from development to production, these URLs change:

| Setting | Development | Production |
|---------|-------------|------------|
| `ENVIRONMENT` | development | production |
| `BASE_URL` | http://localhost:8000 | https://yourdomain.com |
| `DISCORD_REDIRECT_URI` | http://localhost:8000/auth/discord/callback | https://yourdomain.com/auth/discord/callback |

**Note:** Your credentials (CLIENT_ID, CLIENT_SECRET, BOT_TOKEN) stay the same!

### Step 3: Update External Services

After switching to production, you need to update:

#### Discord Developer Portal
1. Go to: https://discord.com/developers/applications/YOUR_APP_ID/oauth2
2. Add redirect URI: `https://yourdomain.com/auth/discord/callback`

#### Telegram Bot Webhook
Run this after switching to production:
```bash
source venv/bin/activate
python3 setup_telegram_webhook.py
```

---

## Configuration Structure

```json
{
  "development": {
    // Local testing config
    "BASE_URL": "http://localhost:8000",
    ...
  },
  "production": {
    // Live server config
    "BASE_URL": "https://yourdomain.com",
    ...
  },
  "current": "development",  // ← Which config is active
  "_instructions": {
    // Help text
  },
  "_urls_to_update": {
    // Checklist of what to update externally
  }
}
```

---

## Manual Method (Without Scripts)

If you prefer to edit `.env` directly:

1. Open `.env`
2. Change these lines:
   ```
   ENVIRONMENT=production
   BASE_URL=https://yourdomain.com
   DISCORD_REDIRECT_URI=https://yourdomain.com/auth/discord/callback
   ```
3. Save and restart: `sudo systemctl restart binding`

---

## Workflow Examples

### First Deployment to Production

```bash
# 1. Edit config with your domain
nano config.json
# Replace YOUR_DOMAIN_HERE with binding.example.com

# 2. Deploy server with HTTPS
sudo bash setup_https.sh

# 3. Switch configuration
python3 switch_config.py production

# 4. Restart app
sudo systemctl restart binding

# 5. Setup Telegram
python3 setup_telegram_webhook.py

# 6. Update Discord OAuth settings
# Visit Discord Developer Portal
```

### Testing Changes Locally First

```bash
# Make sure you're on development
python3 switch_config.py development

# Start dev server
./start_dev.sh

# Test your changes at http://localhost:8000
```

### Switching Back and Forth

```bash
# Going to production
python3 switch_config.py production
sudo systemctl restart binding

# Going back to dev
python3 switch_config.py development
./start_dev.sh
```

---

## Validation

The `apply_config.py` script automatically:
- ✅ Shows you what will change before applying
- ✅ Warns if production config has placeholder values
- ✅ Preserves your secrets and credentials
- ✅ Maintains .env file formatting and comments

---

## What Stays the Same

These values **never** change between environments:
- `DISCORD_CLIENT_ID`
- `DISCORD_CLIENT_SECRET`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_BOT_USERNAME`
- `SECRET_KEY`
- `STORAGE_BACKEND`
- `CSV_DATA_DIR`
- Google Sheets configuration

Only URLs and environment mode change!

---

## Troubleshooting

### "Configuration already up to date"
Your .env already matches the config. No changes needed.

### "Production config still has placeholder values"
Edit `config.json` and replace `YOUR_DOMAIN_HERE` with your actual domain.

### Changes not taking effect
Restart your app after applying config:
```bash
# Development
./start_dev.sh

# Production
sudo systemctl restart binding
```

---

## Best Practices

1. ✅ Always edit `config.json` first, then apply
2. ✅ Test changes locally before switching to production
3. ✅ Keep `config.json` in version control (it has no secrets)
4. ✅ Never commit `.env` to git (it has secrets)
5. ✅ Use `switch_config.py` instead of manual edits (safer)

---

## Quick Reference

```bash
# View current config
cat config.json

# Switch to production
python3 switch_config.py production

# Switch to development
python3 switch_config.py development

# Just apply current config (no switch)
python3 apply_config.py

# View what changed
git diff .env  # (if using git)
```
