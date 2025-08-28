#!/bin/bash
set -euo pipefail

# Number of most recent posts to list (can be overridden as first arg)
NUM_POSTS="${1:-10}"
echo "🔍 Looking for the $NUM_POSTS most recent posts with valid metadata..."

# Temp files
TMP_CANDIDATES="$(mktemp)"
TMP_LIST="$(mktemp)"

# Step 1: Scan valid files (skip *-estatico.qmd and *-static.qmd)
find posts -type f \( -name '*.qmd' -o -name '*.md' \) \
  ! -name '*-estatico.qmd' ! -name '*-static.qmd' | \
while read -r FILE; do
  TITLE=$(grep -m 1 '^title:' "$FILE" | sed -E 's/^title:[[:space:]]*["'\'']?([^"'\'']+)["'\'']?/\1/')
  DATE=$(grep -m 1 '^date:'  "$FILE" | sed -E 's/^date:[[:space:]]*//')

  if [[ -z "${TITLE}" ]]; then
    echo "⚠️  Skipping $FILE (no title)"
    continue
  fi
  if [[ -z "${DATE}" ]]; then
    echo "⚠️  Skipping $FILE (no date)"
    continue
  fi

  echo "✅ Included: $FILE | $DATE | $TITLE"
  echo "$DATE|$TITLE|$FILE" >> "$TMP_CANDIDATES"
done

# Step 2: Sort by date (desc) and build the list
sort -r "$TMP_CANDIDATES" | head -n "$NUM_POSTS" | \
while IFS='|' read -r DATE TITLE FILE; do
  LINK=${FILE%.qmd}.html
  LINK=${LINK%.md}.html
  echo "- [$TITLE]($LINK)"
done > "$TMP_LIST"

# Step 3: Replace the block between markers in index.qmd
awk -v new="$(cat "$TMP_LIST")" '
  /<!-- inicio-ultimos-posts -->/ {
    print
    print new
    in_block=1
    next
  }
  /<!-- fim-ultimos-posts -->/ { in_block=0 }
  !in_block
' index.qmd > index_temp.qmd && mv index_temp.qmd index.qmd

# Cleanup
rm -f "$TMP_CANDIDATES" "$TMP_LIST"

echo "✅ Latest posts updated successfully in index.qmd"

