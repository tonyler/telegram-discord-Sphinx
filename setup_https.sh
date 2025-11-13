#!/bin/bash
set -e

echo "=== HTTPS Setup for Sphinx Binding App ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo: sudo bash setup_https.sh"
    exit 1
fi

# Get domain name
read -p "Enter your domain name (e.g., binding.example.com): " DOMAIN
read -p "Enter your email for SSL certificate: " EMAIL

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "Domain and email are required!"
    exit 1
fi

echo ""
echo "=== Step 1: Installing Nginx ==="
apt update
apt install -y nginx

echo ""
echo "=== Step 2: Installing Certbot (for SSL) ==="
apt install -y certbot python3-certbot-nginx

echo ""
echo "=== Step 3: Creating Nginx configuration ==="
cat > /etc/nginx/sites-available/binding <<EOF
server {
    listen 80;
    server_name ${DOMAIN};

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/binding /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo ""
echo "=== Step 4: Testing Nginx configuration ==="
nginx -t

echo ""
echo "=== Step 5: Starting Nginx ==="
systemctl restart nginx
systemctl enable nginx

echo ""
echo "=== Step 6: Getting SSL certificate ==="
certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos --email ${EMAIL} --redirect

echo ""
echo "=== Step 7: Setting up auto-renewal ==="
systemctl enable certbot.timer
systemctl start certbot.timer

echo ""
echo "=== Step 8: Creating systemd service for your app ==="
cat > /etc/systemd/system/binding.service <<EOF
[Unit]
Description=Sphinx Binding App
After=network.target

[Service]
Type=simple
User=${SUDO_USER}
WorkingDirectory=/home/${SUDO_USER}/Desktop/binding
Environment="PATH=/home/${SUDO_USER}/Desktop/binding/venv/bin"
ExecStart=/home/${SUDO_USER}/Desktop/binding/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable binding.service
systemctl restart binding.service

echo ""
echo "=== ✅ SETUP COMPLETE! ==="
echo ""
echo "Your app is now running with HTTPS at: https://${DOMAIN}"
echo ""
echo "Useful commands:"
echo "  - View app logs: sudo journalctl -u binding -f"
echo "  - Restart app: sudo systemctl restart binding"
echo "  - Stop app: sudo systemctl stop binding"
echo "  - Check status: sudo systemctl status binding"
echo ""
echo "⚠️  IMPORTANT: Update your .env file:"
echo "  - Set ENVIRONMENT=production"
echo "  - Update BASE_URL=https://${DOMAIN}"
echo "  - Update Discord/Telegram redirect URIs to use https://${DOMAIN}"
echo ""
echo "Then restart: sudo systemctl restart binding"
