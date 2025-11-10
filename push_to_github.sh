#!/bin/bash
# Script to push to GitHub

cd "/Users/stevekim/Library/Mobile Documents/com~apple~CloudDocs/cursorai/AI Checker2"

echo "=========================================="
echo "Pushing to GitHub Repository"
echo "=========================================="
echo ""
echo "Repository: https://github.com/MikeVenge/write-aid-mcp.git"
echo "Branch: main"
echo ""
echo "Attempting to push..."
echo ""

# Try to push
if git push -u origin main; then
    echo ""
    echo "=========================================="
    echo "✅ SUCCESS! Code pushed to GitHub"
    echo "=========================================="
    echo ""
    echo "View your repository at:"
    echo "https://github.com/MikeVenge/write-aid-mcp"
    echo ""
    open https://github.com/MikeVenge/write-aid-mcp
else
    echo ""
    echo "=========================================="
    echo "❌ Push failed"
    echo "=========================================="
    echo ""
    echo "Please make sure you've added your SSH key to GitHub:"
    echo "1. Go to: https://github.com/settings/keys"
    echo "2. Click 'New SSH key'"
    echo "3. Paste the key (already in your clipboard)"
    echo "4. Click 'Add SSH key'"
    echo "5. Run this script again: ./push_to_github.sh"
    echo ""
fi

