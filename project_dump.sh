#!/bin/bash

# Script to display Python project structure and file contents
# Usage: ./project_dump.sh [directory_path] [output_file]

# Set the target directory (default to current directory)
TARGET_DIR="${1:-.}"
OUTPUT_FILE="${2:-project_dump.txt}"

# Check if the directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory '$TARGET_DIR' does not exist."
    exit 1
fi

# Create or clear the output file
> "$OUTPUT_FILE"

# Function to print separator lines
print_separator() {
    echo "=================================================================" >> "$OUTPUT_FILE"
    echo "$1" >> "$OUTPUT_FILE"
    echo "=================================================================" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Function to check if file should be included
should_include_file() {
    local file="$1"
    
    # Exclude common Python cache and database files
    case "$file" in
        *.pyc|*.pyo|*.pyd) return 1 ;;
        __pycache__/*) return 1 ;;
        *.db|*.sqlite|*.sqlite3) return 1 ;;
        *.log|*.tmp|*.temp) return 1 ;;
        *.egg-info/*) return 1 ;;
        *.egg) return 1 ;;
        *.so|*.dll|*.dylib) return 1 ;;
        *.bak|*.swp|*.swo) return 1 ;;
        .git/*) return 1 ;;
        .venv/*|venv/*|env/*|.env/*) return 1 ;;
        .pytest_cache/*) return 1 ;;
        .mypy_cache/*) return 1 ;;
        .coverage) return 1 ;;
        .DS_Store) return 1 ;;
        "$OUTPUT_FILE") return 1 ;;  # Exclude the output file itself
        *)
            # Only include text files (common Python extensions and config files)
            case "$file" in
                *.py|*.txt|*.md|*.json|*.yml|*.yaml|*.ini|*.cfg|\
                *.toml|*.rst|*.html|*.css|*.js|*.sh|*.env.example|\
                .gitignore|.dockerignore|Dockerfile|Makefile|\
                requirements*.txt|pyproject.toml|setup.py|setup.cfg|\
                README*|LICENSE*|CHANGELOG*)
                    return 0 ;;
                *)
                    # Check if it's a text file using file command
                    if file "$file" | grep -q "text"; then
                        return 0
                    fi
                    return 1 ;;
            esac ;;
    esac
}

print_separator "PROJECT STRUCTURE"
echo "Project directory: $(realpath "$TARGET_DIR")" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Generate tree structure (if tree command is available)
if command -v tree &> /dev/null; then
    echo "Directory structure (using tree):" >> "$OUTPUT_FILE"
    tree -I '__pycache__|*.pyc|*.db|*.sqlite|*.sqlite3|*.log|.git|.venv|venv|env|.env|*.egg-info|.pytest_cache|.mypy_cache' "$TARGET_DIR" >> "$OUTPUT_FILE" 2>/dev/null
else
    echo "Note: Install 'tree' command for better directory visualization." >> "$OUTPUT_FILE"
    echo "Basic directory listing:" >> "$OUTPUT_FILE"
    find "$TARGET_DIR" -type d -not -path "*/__pycache__/*" -not -path "*/.git/*" \
        -not -path "*/.venv/*" -not -path "*/venv/*" -not -path "*/env/*" \
        -not -path "*/.pytest_cache/*" -not -path "*/.mypy_cache/*" | sort >> "$OUTPUT_FILE"
fi

echo "" >> "$OUTPUT_FILE"
print_separator "FILE CONTENTS"

# Find and display contents of all text files
find "$TARGET_DIR" -type f -not -path "*/__pycache__/*" -not -path "*/.git/*" \
    -not -path "*/.venv/*" -not -path "*/venv/*" -not -path "*/env/*" \
    -not -path "*/.pytest_cache/*" -not -path "*/.mypy_cache/*" \
    -not -name "*.pyc" -not -name "*.pyo" -not -name "*.pyd" \
    -not -name "*.db" -not -name "*.sqlite" -not -name "*.sqlite3" \
    -not -name "*.log" -not -name "*.egg" \
    -not -path "*.egg-info/*" | sort | while read -r file; do
    
    # Double-check if file should be included
    if should_include_file "$file"; then
        # Get relative path
        rel_path="${file#$TARGET_DIR/}"
        if [ "$rel_path" = "$file" ]; then
            rel_path="$file"
        fi
        
        print_separator "FILE: $rel_path"
        
        # Try to display file with line numbers
        if [ -r "$file" ]; then
            # Check if file is empty
            if [ -s "$file" ]; then
                # Use cat -n for line numbers
                cat -n "$file" >> "$OUTPUT_FILE" 2>/dev/null || echo "Error reading file" >> "$OUTPUT_FILE"
            else
                echo "(empty file)" >> "$OUTPUT_FILE"
            fi
        else
            echo "(file not readable)" >> "$OUTPUT_FILE"
        fi
        echo "" >> "$OUTPUT_FILE"
    fi
done

echo "Project dump complete! Output saved to: $OUTPUT_FILE"
echo "Total size: $(du -h "$OUTPUT_FILE" | cut -f1)"

# Optional: Show summary
echo ""
echo "Summary of processed files:"
find "$TARGET_DIR" -type f -not -path "*/__pycache__/*" -not -path "*/.git/*" \
    -not -path "*/.venv/*" -not -path "*/venv/*" -not -path "*/env/*" \
    -not -path "*/.pytest_cache/*" -not -path "*/.mypy_cache/*" \
    -not -name "*.pyc" -not -name "*.pyo" -not -name "*.pyd" \
    -not -name "*.db" -not -name "*.sqlite" -not -name "*.sqlite3" \
    -not -name "*.log" -not -name "*.egg" \
    -not -path "*.egg-info/*" | wc -l | xargs echo "Total files included:"