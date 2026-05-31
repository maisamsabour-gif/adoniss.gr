#!/bin/bash
#
# Adonis Site - Safe Restart Script
# Usage: ./restart.sh [--force]
#

set -e

PROJECT_DIR="/root/adonis_site"
VENV_PATH="$PROJECT_DIR/venv"
SERVICE_NAME="adonis"
BACKUP_DIR="$PROJECT_DIR/backups"
LOG_FILE="$PROJECT_DIR/restart.log"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "[ERROR] $1" >> "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

cd "$PROJECT_DIR"

log "========== Starting Restart Process =========="

log "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

log "Collecting static files..."
python manage.py collectstatic --noinput --clear 2>/dev/null || {
    warn "collectstatic had warnings (this is usually fine)"
}

log "Running database migrations..."
python manage.py migrate --noinput 2>&1 | tee -a "$LOG_FILE" || {
    error "Migration failed! Aborting restart."
    exit 1
}

log "Checking Django configuration..."
python manage.py check --deploy 2>&1 | grep -v "WARNINGS" | head -5 || true

log "Restarting $SERVICE_NAME service..."
sudo systemctl restart "$SERVICE_NAME"

sleep 2

if systemctl is-active --quiet "$SERVICE_NAME"; then
    log "✓ Service $SERVICE_NAME is running"
else
    error "✗ Service $SERVICE_NAME failed to start!"
    sudo systemctl status "$SERVICE_NAME" --no-pager
    exit 1
fi

log "Restarting nginx..."
sudo systemctl restart nginx

if systemctl is-active --quiet nginx; then
    log "✓ Nginx is running"
else
    error "✗ Nginx failed to start!"
    exit 1
fi

log "Testing local connection..."
sleep 1
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000 | grep -qE "200|301|302"; then
    log "✓ Application is responding"
else
    warn "Application may need a moment to fully start"
fi

log "========== Restart Complete =========="
echo ""
echo -e "${GREEN}✓ All services restarted successfully!${NC}"
echo ""
