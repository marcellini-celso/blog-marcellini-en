#!/bin/bash
set -euo pipefail

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

# Opcional: primeiro argumento = quantidade de posts na lista (padrão: 10)
NUM_POSTS="${1:-10}"

# 1) Gera o JSON (necessário para tags e categorias)
log "📦 Generating docs/posts.json..."
python3 generate_posts_json.py || { echo "❌ Failed to generate posts.json."; exit 1; }

# 2) Atualiza a lista de últimos posts no index
log "🔄 Updating latest posts..."
./update_latest_posts.sh "$NUM_POSTS" || { echo "❌ Failed to update latest posts."; exit 1; }

# 3) Atualiza Tags (freq, nuvem e páginas por tag)
log "🏷️ Updating tags..."
./update_tags.sh || { echo "❌ Failed to update tags."; exit 1; }

# 4) Atualiza Categories (lista e páginas por categoria)
log "🗂️ Updating categories..."
./update_categories.sh || { echo "❌ Failed to update categories."; exit 1; }

log "✅ Update complete!"

