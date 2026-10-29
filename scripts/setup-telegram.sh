#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
secret_dir="$project_dir/.secrets"
token_file="$secret_dir/telegram_bot_token"
code_file="$secret_dir/telegram_pairing_code"

mkdir -p "$secret_dir"
chmod 700 "$secret_dir"

printf 'BotFather tokenini girin (ekranda gorunmez): '
stty -echo
IFS= read -r token
stty echo
printf '\n'

token=$(printf '%s' "$token" | LC_ALL=C grep -Eo '[0-9]{8,15}:[A-Za-z0-9_-]{30,}' | head -n 1 || true)

case "$token" in
  *:*) ;;
  *) printf 'Token bicimi gecersiz.\n' >&2; exit 1 ;;
esac

umask 077
printf '%s' "$token" > "$token_file"
pairing_code=$(openssl rand -hex 4)
printf '%s' "$pairing_code" > "$code_file"

printf 'Telegram secrets kaydedildi.\n'
printf 'Bot basladiktan sonra Telegram botuna su mesaji gonderin: /pair %s\n' "$pairing_code"
