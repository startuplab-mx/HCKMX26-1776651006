#!/usr/bin/env bash
# Daily SQLite backup. Run via cron on the droplet:
#   0 3 * * * /opt/nahual/scripts/backup_db.sh >> /var/log/nahual-backup.log 2>&1
#
# Strategy:
#   • SQLite Online Backup API via `.backup` (avoids file-locking issues
#     with WAL while uvicorn is writing alerts)
#   • Compress with gzip
#   • Keep 14 daily + 8 weekly + 6 monthly snapshots
#   • Print disk usage at the end

set -euo pipefail

DB="/opt/nahual/backend/nahual.db"
BACKUP_DIR="/opt/nahual/backups"
DATE=$(date '+%Y%m%d_%H%M%S')
DAILY_DIR="$BACKUP_DIR/daily"
WEEKLY_DIR="$BACKUP_DIR/weekly"
MONTHLY_DIR="$BACKUP_DIR/monthly"

mkdir -p "$DAILY_DIR" "$WEEKLY_DIR" "$MONTHLY_DIR"

# Live snapshot via SQLite's Online Backup API.
DAILY_FILE="$DAILY_DIR/nahual_$DATE.db.gz"
sqlite3 "$DB" ".backup '$DAILY_DIR/nahual_$DATE.db'"
gzip -9 "$DAILY_DIR/nahual_$DATE.db"
echo "[$(date '+%F %T')] daily snapshot -> $DAILY_FILE"

# Weekly: copy Sunday's snapshot
if [[ "$(date '+%u')" == "7" ]]; then
  cp "$DAILY_FILE" "$WEEKLY_DIR/"
  echo "[$(date '+%F %T')] weekly snapshot copied"
fi

# Monthly: copy day-1 snapshot
if [[ "$(date '+%d')" == "01" ]]; then
  cp "$DAILY_FILE" "$MONTHLY_DIR/"
  echo "[$(date '+%F %T')] monthly snapshot copied"
fi

# Retention: keep 14 daily, 8 weekly, 6 monthly.
find "$DAILY_DIR" -name 'nahual_*.db.gz' -mtime +14 -delete
find "$WEEKLY_DIR" -name 'nahual_*.db.gz' -mtime +56 -delete
find "$MONTHLY_DIR" -name 'nahual_*.db.gz' -mtime +186 -delete

# Bayesian model snapshot too (small, but separate file).
cp /opt/nahual/backend/classifier/bayesian_model.json \
   "$DAILY_DIR/bayesian_$DATE.json" 2>/dev/null || true
gzip -9 "$DAILY_DIR/bayesian_$DATE.json" 2>/dev/null || true

echo "[$(date '+%F %T')] backup complete · disk usage:"
du -sh "$BACKUP_DIR"/*
