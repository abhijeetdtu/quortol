#!/bin/bash
set -e

# Blog Post Validator Script
# Usage: ./validate.sh <post.md> [--output report]

POST_FILE="$1"
REPORT="${2:-validation-report.txt}"

if [ -z "$POST_FILE" ]; then
    echo "Usage: ./validate.sh <post.md> [--output report.md]"
    exit 1
fi

if [ ! -f "$POST_FILE" ]; then
    echo "Error: File '$POST_FILE' not found"
    exit 1
fi

echo "Validating: $POST_FILE"
echo ""

# Check for frontmatter
if head -1 "$POST_FILE" | grep -q "^---"; then
    echo "✓ Has YAML frontmatter"
else
    echo "✗ Missing YAML frontmatter (start with '---')"
fi

# Check title
TITLE=$(head -1 "$POST_FILE" | sed 's/^# //')
if [ -n "$TITLE" ]; then
    echo "✓ Title: $TITLE"
else
    echo "✗ No title found"
fi

# Check for tags in frontmatter
if grep -q "^tags:" "$POST_FILE"; then
    TAGS=$(grep "^tags:" "$POST_FILE" | head -1)
    echo "  $TAGS"
fi

# Check excerpt/intro
if grep -q "^## Executive Summary\|^# Introduction\|> \*" "$POST_FILE"; then
    echo "✓ Has executive summary or introduction"
else
    echo "✗ Missing executive summary or introduction"
fi

# Check for sources/citations
if grep -q "Source:\|source:\|\[.*\](http" "$POST_FILE"; then
    SOURCE_COUNT=$(grep -c "Source:\|source:" "$POST_FILE")
    echo "✓ Has $SOURCE_COUNT source citations"
else
    echo "✗ No source citations found"
fi

# Check for images/figures
if grep -q "!\\[.*\\](https\|!\\[.*\\](/api" "$POST_FILE"; then
    IMAGE_COUNT=$(grep -c "!\\[" "$POST_FILE")
    echo "✓ Has $IMAGE_COUNT image references"
else
    echo "✗ No images referenced"
fi

# Check for tables
if grep -q "|" "$POST_FILE"; then
    TABLE_COUNT=$(grep -c "^[|].*[|]" "$POST_FILE")
    echo "✓ Has $TABLE_COUNT table(s)"
else
    echo "  No tables found (optional)"
fi

# Calculate statistics
CHARS=$(wc -c < "$POST_FILE")
WORDS=$(wc -w < "$POST_FILE")
LINES=$(wc -l < "$POST_FILE")
READ_TIME=$((($CHARS + 199) / 200))

echo ""
echo "Statistics:"
echo "  Characters: $CHARS"
echo "  Words: $WORDS"
echo "  Lines: $LINES"
echo "  Read time: ~${READ_TIME} minute(s)"

# Generate validation report
cat > "$REPORT" << EOF
Blog Post Validation Report
============================
File: $POST_FILE
Date: $(date)

Results:
- Frontmatter: $(head -1 "$POST_FILE" | grep -q "^---" && echo "✓ Present" || echo "✗ Missing")
- Title: $(head -1 "$POST_FILE" | sed 's/^# //' | head -c 50)
- Sources: $(grep -c "Source:" "$POST_FILE") citations
- Images: $(grep -c "!\\[" "$POST_FILE") references
- Tables: $(grep -c "^[|].*[|]" "$POST_FILE") tables

Statistics:
- Characters: $CHARS
- Words: $WORDS
- Read time: ~${READ_TIME} minutes
EOF

echo ""
echo "Validation report saved to: $REPORT"
