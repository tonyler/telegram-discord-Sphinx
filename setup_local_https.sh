#!/bin/bash
# Setup HTTPS for madbet.xyz on local PC

set -e

echo "=== Setting up HTTPS for madbet.xyz ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo: sudo bash setup_local_https.sh"
    exit 1
fi

DOMAIN="madbet.xyz"
APP_PORT=8002

echo "Step 1: Installing nginx..."
apt update
apt install -y nginx

echo ""
echo "Step 2: Installing certbot for Let's Encrypt SSL..."
apt install -y certbot python3-certbot-nginx

echo ""
echo "Step 3: Creating nginx configuration..."
cat > /etc/nginx/sites-available/madbet <<EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    location / {
        proxy_pass http://127.0.0.1:${APP_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/madbet /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo ""
echo "Step 4: Testing nginx configuration..."
nginx -t

echo ""
echo "Step 5: Starting nginx..."
systemctl restart nginx
systemctl enable nginx

echo ""
echo "Step 6: Opening firewall ports..."
ufw allow 80/tcp
ufw allow 443/tcp

echo ""
echo "Step 7: Getting SSL certificate from Let's Encrypt..."
echo "NOTE: Your domain must be pointing to this server's IP (2.86.13.236)"
echo "Press ENTER to continue or Ctrl+C to cancel..."
read

certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --agree-tos --redirect --non-interactive --email your-email@example.com

echo ""
echo "Step 8: Setting up auto-renewal..."
systemctl enable certbot.timer
systemctl start certbot.timer

echo ""
echo "=== ✅ HTTPS Setup Complete! ==="
echo ""
echo "Your app is now accessible at:"
echo "  https://madbet.xyz"
echo "  https://www.madbet.xyz"
echo ""
echo "⚠️  IMPORTANT: Update your .env file:"
echo "  BASE_URL=https://madbet.xyz"
echo ""
echo "Then restart your app!"
echo ""
echo "Useful commands:"
echo "  - Check nginx status: sudo systemctl status nginx"
echo "  - Restart nginx: sudo systemctl restart nginx"
echo "  - Check SSL renewal: sudo certbot renew --dry-run"
echo ""
