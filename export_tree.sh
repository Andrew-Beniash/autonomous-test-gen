#!/bin/bash

# Set the name of the output file
OUTPUT_FILE="project_tree.txt"

# Exclude patterns
EXCLUDE_PATTERNS=(
  "./.git/*"
  "./venv/*"
  "./__pycache__/*"
  "*.pyc"
  "./.coverage"
  "./htmlcov/*"
  "./.env"
  "./.pytest_cache/*"
  "./.mypy_cache/*"
  "*.log"
  "./dist/*"
  "./build/*"
  "./*.egg-info/*"
  "./node_modules/*"
  "./frontend/node_modules/*"
  "./frontend/build/*"
  "./frontend/coverage/*"
  "./frontend/.env"
  "./frontend/.env.local"
  "./frontend/.env.development.local"
  "./frontend/.env.test.local"
  "./frontend/.env.production.local"
  "./.vscode/*"
  "*.tsbuildinfo"
  "./.npm/*"
  "./.eslintcache"
  "./.DS_Store"
  "./.AppleDouble"
  "./.LSOverride"
  "./._*"
  "./logs/*"
  "npm-debug.log*"
  "yarn-debug.log*"
  "yarn-error.log*"
  "./coverage/*"
  "./.nyc_output/*"
  "./build/*"
  "./dist/*"
  "./.env.local"
  "./.env.development.local"
  "./.env.test.local"
  "./.env.production.local"
  "./.cache/*"
  "./.parcel-cache/*"
  "./.stylelintcache"
)

# Build the find command with exclusions
FIND_CMD="find ."
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
  FIND_CMD+=" -path '$pattern' -prune -o"
done

# Complete the find command
FIND_CMD+=" -type f -print"

# Execute the command and save to the output file
eval "$FIND_CMD" > "$OUTPUT_FILE"

echo "Project tree has been exported to $OUTPUT_FILE"