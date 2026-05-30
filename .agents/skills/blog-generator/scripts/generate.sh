#!/bin/bash
set -e

# Blog Post Generator Script
# Usage: ./generate.sh <title> [--template <template.md>] [--tags <comma-separated>] [--excerpt <text>]

TITLE="$1"
TEMPLATE="${2:-templates/default.md}"
TAGS=""
EXCERPT=""

# Parse additional arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --template)
            TEMPLATE="$2"
            shift 2
            ;;
        --tags)
            TAGS="$2"
            shift 2
            ;;
        --excerpt)
            EXCERPT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: ./generate.sh <title> [--template <template.md>] [--tags <tags>] [--excerpt <text>]"
            exit 0
            ;;
        *)
            TITLE="$1"
            shift
            ;;
    esac
done

# Validate title is provided
if [ -z "$TITLE" ]; then
    echo "Error: Title required"
    echo "Usage: ./generate.sh <title> [--template <template.md>] [--tags <tags>] [--excerpt <text>]"
    exit 1
fi

# Check template exists
if [ ! -f "$TEMPLATE" ]; then
    echo "Error: Template file '$TEMPLATE' not found"
    exit 1
fi

# Create output directory
OUTPUT_DIR="output"
mkdir -p "$OUTPUT_DIR"

# Generate filename from title (slugify)
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g')
FILENAME="${SLUG}.md"

# Copy template with placeholder replacement
cp "$TEMPLATE" "$OUTPUT_DIR/$FILENAME"

# Replace title placeholder if exists
if grep -q "{{TITLE}}" "$OUTPUT_DIR/$FILENAME"; then
    sed -i "s/{{TITLE}}/$TITLE/g" "$OUTPUT_DIR/$FILENAME" 2>/dev/null || \
    sed -i '' "s/{{TITLE}}/$TITLE/g" "$OUTPUT_DIR/$FILENAME" 2>/dev/null || \
    echo "Note: Title placeholder '{{TITLE}}' not found in template"
fi

# Add frontmatter if tags provided
if [ -n "$TAGS" ]; then
    # Check if file has frontmatter (starts with ---)
    if head -1 "$OUTPUT_DIR/$FILENAME" | grep -q "^---"; then
        # Extract everything until closing ---
        BEFORE=$(head -n 2 "$OUTPUT_DIR/$FILENAME")
        AFTER=$(tail -n +3 "$OUTPUT_DIR/$FILENAME")
        
        # Add tags to frontmatter
        echo "$BEFORE" > "$OUTPUT_DIR/tmp.md"
        echo "tags: $TAGS" >> "$OUTPUT_DIR/tmp.md"
        echo "---" >> "$OUTPUT_DIR/tmp.md"
        echo "$AFTER" >> "$OUTPUT_DIR/tmp.md"
        
        # Replace original with updated version
        mv "$OUTPUT_DIR/tmp.md" "$OUTPUT_DIR/$FILENAME"
    else
        echo "Error: Template must have YAML frontmatter (start with '---')"
        exit 1
    fi
fi

# Calculate read time (approx. 200 chars per minute)
CHAR_COUNT=$(wc -c < "$OUTPUT_DIR/$FILENAME")
READ_TIME=$((($CHAR_COUNT + 199) / 200))

echo "✓ Generated: $OUTPUT_DIR/$FILENAME"
echo "  Title: $TITLE"
[ -n "$TAGS" ] && echo "  Tags: $TAGS"
echo "  Read time: ~${READ_TIME} minute(s)"
echo ""
echo "Edit the file and run:"
echo "  ./scripts/validate.sh output/$FILENAME"
