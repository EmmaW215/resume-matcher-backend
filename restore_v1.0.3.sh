#!/bin/bash

# MatchWise AI v1.0.3 Restore Script

echo "🔄 MatchWise AI v1.0.3 Restore Script"
echo "="*50

# Find the latest v1.0.3 backup file
BACKUP_FILE=$(ls -t v1.0.3_MatchWise_AI_Backup_*.tar.gz 2>/dev/null | head -1)

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ No v1.0.3 backup file found!"
    echo "Please ensure the backup file exists in the current directory."
    exit 1
fi

echo "📁 Found backup file: $BACKUP_FILE"
echo "📊 File size: $(du -h "$BACKUP_FILE" | cut -f1)"

# Ask for confirmation
echo ""
echo "⚠️  This will overwrite the current project files!"
read -p "Do you want to continue? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Restore cancelled."
    exit 1
fi

# Create backup of current state (if not already a backup)
if [[ ! "$PWD" =~ "Backup" ]]; then
    echo "📦 Creating backup of current state..."
    CURRENT_BACKUP="current_state_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf "$CURRENT_BACKUP" \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.DS_Store' \
        --exclude='*.log' \
        --exclude='*.tmp' \
        --exclude='*_Backup_*.tar.gz' \
        .
    echo "✅ Current state backed up as: $CURRENT_BACKUP"
fi

# Extract the backup
echo "🔄 Extracting backup..."
tar -xzf "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Restore completed successfully!"
    echo ""
    echo "📋 Restored Features:"
    echo "• Enhanced local mock AI with proper Markdown table format"
    echo "• Improved comparison table display with clear column structure"
    echo "• Maintained user's custom formatting preferences"
    echo "• Added proper table headers and separators"
    echo "• Enhanced readability with bold total score"
    echo "• All changes tested and verified"
    echo ""
    echo "🎯 Next Steps:"
    echo "1. Install dependencies:"
    echo "   - Frontend: cd resume-matcher-frontend && npm install"
    echo "   - Backend: cd resume-matcher-backend && pip install -r requirements.txt"
    echo "2. Set up environment variables"
    echo "3. Start the application"
    echo ""
    echo "🎉 MatchWise AI v1.0.3 restored successfully!"
else
    echo "❌ Restore failed!"
    exit 1
fi 