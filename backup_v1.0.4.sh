#!/bin/bash

# MatchWise AI v1.0.4 Backup Script
# Backup Date: $(date)

echo "🚀 Creating MatchWise AI v1.0.4 Backup..."
echo "📅 Backup Date: $(date)"
echo "="*60

# Create backup filename with timestamp
BACKUP_NAME="v1.0.4_MatchWise_AI_Backup_$(date +%Y%m%d_%H%M%S).tar.gz"

# Create backup
echo "📦 Creating backup archive: $BACKUP_NAME"
tar -czf "$BACKUP_NAME" \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    --exclude='*.log' \
    --exclude='*.tmp' \
    --exclude='V0_resume-matcher_Backup' \
    --exclude='v1.0.0_MatchWise_AI_Backup_*.tar.gz' \
    --exclude='v1.0.1_MatchWise_AI_Backup_*.tar.gz' \
    --exclude='v1.0.2_MatchWise_AI_Backup_*.tar.gz' \
    --exclude='v1.0.3_MatchWise_AI_Backup_*.tar.gz' \
    --exclude='v1.0.4_MatchWise_AI_Backup_*.tar.gz' \
    --exclude='backup_*.sh' \
    --exclude='save-project.sh' \
    .

# Check if backup was created successfully
if [ $? -eq 0 ]; then
    echo "✅ Backup created successfully!"
    echo "📁 Backup file: $BACKUP_NAME"
    echo "📊 File size: $(du -h "$BACKUP_NAME" | cut -f1)"
else
    echo "❌ Backup failed!"
    exit 1
fi

echo ""
echo "📋 v1.0.4 Update Summary:"
echo "• All recent bug fixes and deployment issues resolved"
echo "• react-markdown依赖问题彻底修复"
echo "• Vercel Root Directory配置与多目录项目兼容"
echo "• 前后端所有最新手动更改已保存"
echo "• 项目结构与依赖已完全同步"
echo "• 线上部署与本地一致"

echo ""
echo "🎯 System Features:"
echo "• OpenAI GPT-3.5-turbo integration"
echo "• xAI Grok-3 integration"
echo "• Enhanced local mock AI with Markdown tables"
echo "• Professional job requirement analysis"
echo "• Detailed resume-job matching with scoring"
echo "• Visitor counter functionality"
echo "• Admin dashboard"
echo "• Three-tier AI fallback system"

echo ""
echo "🔧 To restore this backup:"
echo "tar -xzf $BACKUP_NAME"

echo ""
echo "🎉 MatchWise AI v1.0.4 backup completed!" 