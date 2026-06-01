#!/bin/bash
#
# SSL Setup Script for adonis.gr
# Run this AFTER DNS is pointing to this server (116.203.240.156)
#
# Usage: ./setup-ssl.sh [email]
# Example: ./setup-ssl.sh admin@adonis.gr

set -e

EMAIL="${1:-admin@adonis.gr}"
DOMAIN="adonis.gr"
WWW_DOMAIN="www.adonis.gr"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== SSL Setup for $DOMAIN ===${NC}"

# Check DNS
echo "Checking DNS..."
CURRENT_IP=$(dig +short $DOMAIN A 2>/dev/null | head -1)
SERVER_IP="116.203.240.156"

if [ "$CURRENT_IP" != "$SERVER_IP" ]; then
    echo -e "${RED}ERROR: DNS not pointing to this server!${NC}"
    echo "Domain $DOMAIN resolves to: $CURRENT_IP"
    echo "Expected: $SERVER_IP"
    echo ""
    echo "Please update DNS records in Arvan Cloud:"
    echo "  A record: @ -> $SERVER_IP"
    echo "  A record: www -> $SERVER_IP (or CNAME www -> $DOMAIN)"
    exit 1
fi

echo -e "${GREEN}DNS check passed! $DOMAIN -> $SERVER_IP${NC}"

# Obtain certificate
echo ""
echo "Obtaining SSL certificate..."
certbot certonly \
    --webroot \
    -w /var/www/certbot \
    -d $DOMAIN \
    -d $WWW_DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --non-interactive

# Check if certificate was obtained
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo -e "${RED}ERROR: Certificate not obtained!${NC}"
    exit 1
fi

echo -e "${GREEN}SSL certificate obtained successfully!${NC}"

# Switch to HTTPS config
echo ""
echo "Enabling HTTPS configuration..."

# Disable HTTP-only config
rm -f /etc/nginx/sites-enabled/adonis.gr.conf

# Enable HTTPS config
ln -sf /etc/nginx/sites-available/adonis.gr-ssl.conf /etc/nginx/sites-enabled/adonis.gr-ssl.conf

# Test nginx config
nginx -t

# Reload nginx
systemctl reload nginx

echo ""
echo -e "${GREEN}=== SSL Setup Complete ===${NC}"
echo ""
echo "Site is now available at: https://$DOMAIN"
echo "www.$DOMAIN redirects to: https://$DOMAIN"
echo ""
echo "Certificate renewal is automatic via certbot timer."
echo "Check timer status: systemctl status certbot.timer"
