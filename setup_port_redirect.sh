#!/bin/bash
# Redirect external port 80 to local port 8002

echo "Setting up port redirection from 80 to 8002..."

# Allow traffic on port 80
sudo ufw allow 80/tcp

# Redirect port 80 to 8002 using iptables
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8002

# Save iptables rules
sudo iptables-save | sudo tee /etc/iptables/rules.v4

echo "✅ Port 80 now redirects to 8002"
echo ""
echo "Now when people visit http://madbet.xyz, they'll reach your app on port 8002"
