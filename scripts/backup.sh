#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
timestamp=$(date '+%Y%m%d-%H%M%S')
backup_dir="$project_dir/backups/runtime-$timestamp"

mkdir -p "$backup_dir"

docker compose -f "$project_dir/compose.yaml" --env-file "$project_dir/.env" \
  exec -T postgres pg_dump \
  -U "${POSTGRES_USER:-n8n}" \
  -d "${POSTGRES_DB:-linkedin_content}" \
  --format=custom > "$backup_dir/postgres.dump"

tar -czf "$backup_dir/content-data.tar.gz" \
  -C "$project_dir" content-data

docker compose -f "$project_dir/compose.yaml" --env-file "$project_dir/.env" \
  exec -T n8n n8n export:workflow --backup --output=/tmp/workflow-backup >/dev/null

docker compose -f "$project_dir/compose.yaml" --env-file "$project_dir/.env" \
  cp n8n:/tmp/workflow-backup "$backup_dir/workflows"

printf 'Backup created: %s\n' "$backup_dir"
