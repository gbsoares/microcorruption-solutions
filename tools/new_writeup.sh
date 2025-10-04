#!/bin/bash

# Script to create a new writeup from template
# Usage: ./new_writeup.sh "Challenge Name" difficulty

if [ $# -ne 2 ]; then
    echo "Usage: $0 \"Challenge Name\" [beginner|intermediate|advanced|expert]"
    echo "Example: $0 \"Hanoi\" beginner"
    exit 1
fi

CHALLENGE_NAME="$1"
DIFFICULTY="$2"

# Convert challenge name to filename format
FILENAME=$(echo "$CHALLENGE_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

# Determine challenge number (simple counter based on existing files)
COUNTER=$(find writeups/ -name "*.md" -not -name "TEMPLATE.md" | wc -l)
COUNTER_FORMATTED=$(printf "%02d" $COUNTER)

# Full filename
FULL_FILENAME="${COUNTER_FORMATTED}-${FILENAME}.md"
FILEPATH="writeups/${FULL_FILENAME}"

# Check if file already exists
if [ -f "$FILEPATH" ]; then
    echo "Error: File $FILEPATH already exists!"
    exit 1
fi

# Copy template and replace placeholders
cp writeups/TEMPLATE.md "$FILEPATH"

# Replace placeholders in the new file
sed -i "s/\[Challenge Name\]/$CHALLENGE_NAME/g" "$FILEPATH"
sed -i "s/\[Beginner\/Intermediate\/Advanced\/Expert\]/$DIFFICULTY/g" "$FILEPATH"
sed -i "s/\[XX\]/$COUNTER_FORMATTED/g" "$FILEPATH"
sed -i "s/\[challenge-name\]/$FILENAME/g" "$FILEPATH"
sed -i "s/\[ChallengeName\]/$CHALLENGE_NAME/g" "$FILEPATH"

# Create corresponding image directory
IMAGE_DIR="images/$DIFFICULTY"
mkdir -p "$IMAGE_DIR"

echo "Created new writeup: $FILEPATH"
echo "Image directory: $IMAGE_DIR"
echo "Don't forget to update the main README.md progress table!"