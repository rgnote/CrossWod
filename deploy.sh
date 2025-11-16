#!/bin/bash

# CrossWod Deployment Script
# Usage: ./deploy.sh [start|stop|restart|logs|backup]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "$1" in
  start)
    echo "Starting CrossWod..."
    docker-compose up -d --build
    echo "CrossWod is now running at http://localhost:3000"
    ;;

  stop)
    echo "Stopping CrossWod..."
    docker-compose down
    echo "CrossWod stopped."
    ;;

  restart)
    echo "Restarting CrossWod..."
    docker-compose down
    docker-compose up -d --build
    echo "CrossWod restarted."
    ;;

  logs)
    docker-compose logs -f
    ;;

  backup)
    BACKUP_DIR="$SCRIPT_DIR/backups"
    mkdir -p "$BACKUP_DIR"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/crosswod_backup_$TIMESTAMP.db"

    if [ -f "$SCRIPT_DIR/backend/data/crosswod.db" ]; then
      cp "$SCRIPT_DIR/backend/data/crosswod.db" "$BACKUP_FILE"
      echo "Backup created: $BACKUP_FILE"
    else
      echo "No database file found to backup."
    fi
    ;;

  *)
    echo "CrossWod Deployment Script"
    echo ""
    echo "Usage: $0 {start|stop|restart|logs|backup}"
    echo ""
    echo "Commands:"
    echo "  start   - Start CrossWod (builds and runs containers)"
    echo "  stop    - Stop CrossWod"
    echo "  restart - Restart CrossWod"
    echo "  logs    - View live logs"
    echo "  backup  - Create a backup of the database"
    echo ""
    echo "After starting, access the app at: http://localhost:3000"
    ;;
esac
