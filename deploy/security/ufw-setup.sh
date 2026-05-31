#!/usr/bin/env bash
set -euo pipefail

echo "[ufw] reset and configure base rules"
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing

echo "[ufw] allow SSH, HTTP, HTTPS"
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

echo "[ufw] enable firewall"
sudo ufw --force enable
sudo ufw status verbose
