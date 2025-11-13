# Deployment Guide

## Local Development (HTTP)

```bash
./start_dev.sh
```

Your app will run at `http://localhost:8000`

---

## Production Deployment (HTTPS)

### Prerequisites
- A domain name pointed to your server's IP
- Ubuntu/Debian Linux server
- Port 80 and 443 open in firewall

### One-Command Setup

```bash
sudo bash setup_https.sh
```

This script will:
1. ✅ Install Nginx (web server)
2. ✅ Install Certbot (for free SSL certificates)
3. ✅ Configure Nginx to proxy your app
4. ✅ Get a free SSL certificate from Let's Encrypt
5. ✅ Set up automatic certificate renewal
6. ✅ Create a systemd service (auto-start on boot)
7. ✅ Start your app

### After Setup

**1. Update your `.env` file:**
```bash
ENVIRONMENT=production
BASE_URL=https://yourdomain.com
DISCORD_REDIRECT_URI=https://yourdomain.com/auth/discord/callback
TELEGRAM_BOT_TOKEN=your-token
```

**2. Restart the app:**
```bash
sudo systemctl restart binding
```

**3. Update OAuth App Settings:**

**Discord:**
- Go to https://discord.com/developers/applications
- Update Redirect URI to: `https://yourdomain.com/auth/discord/callback`

**Telegram:**
- Set webhook: `https://yourdomain.com/auth/telegram/webhook`

---

## Useful Commands

### Check if app is running
```bash
sudo systemctl status binding
```

### View live logs
```bash
sudo journalctl -u binding -f
```

### Restart app (after .env changes)
```bash
sudo systemctl restart binding
```

### Stop app
```bash
sudo systemctl stop binding
```

### Start app
```bash
sudo systemctl start binding
```

### Check Nginx status
```bash
sudo systemctl status nginx
```

### Test Nginx config
```bash
sudo nginx -t
```

### View Nginx error logs
```bash
sudo tail -f /var/log/nginx/error.log
```

### Check SSL certificate
```bash
sudo certbot certificates
```

### Renew SSL certificate manually
```bash
sudo certbot renew
```

---

## Troubleshooting

### App won't start
```bash
# Check logs for errors
sudo journalctl -u binding -n 50

# Common issues:
# - Wrong .env values
# - Database/CSV file permissions
# - Port 8000 already in use
```

### Can't access website
```bash
# Check if Nginx is running
sudo systemctl status nginx

# Check if app is running
sudo systemctl status binding

# Check if ports are open
sudo netstat -tulpn | grep -E '(80|443|8000)'
```

### SSL certificate issues
```bash
# Check certificate status
sudo certbot certificates

# Try renewing
sudo certbot renew --dry-run
```

---

## Security Notes

✅ SSL certificates auto-renew every 90 days
✅ Session cookies are secure in production
✅ App only listens on localhost (Nginx proxies)
✅ HTTPS enforced automatically

## File Structure
```
/home/tony/Desktop/binding/
├── app/                    # Your application code
├── venv/                   # Python virtual environment
├── data/                   # CSV data storage
├── .env                    # Configuration (NEVER commit)
├── setup_https.sh          # Production setup script
├── start_dev.sh            # Development server script
└── DEPLOYMENT.md           # This file

/etc/nginx/sites-available/binding  # Nginx config
/etc/systemd/system/binding.service # Auto-start service
```

## Support

If something goes wrong, check logs first:
```bash
sudo journalctl -u binding -f
sudo tail -f /var/log/nginx/error.log
```
