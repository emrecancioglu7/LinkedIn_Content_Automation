#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

if [ ! -f "$project_dir/.env" ]; then
  printf 'Missing %s/.env. Create it from .env.example first.\n' "$project_dir" >&2
  exit 1
fi

docker compose -f "$project_dir/compose.yaml" --env-file "$project_dir/.env" \
  exec -T n8n n8n import:workflow \
  --separate \
  --input=/opt/linkedin-workflows

printf 'Workflows imported. Open n8n and assign Postgres/OpenAI credentials.\n'
