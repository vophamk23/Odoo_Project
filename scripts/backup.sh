#!/bin/bash
set -e  # Dừng script nếu có lỗi

# === CẤU HÌNH ===
DB_NAME="vopc_cmcts"
DB_USER="odoo"
CONTAINER="vopc_db"
BACKUP_DIR="./backup"
DATE=$(date +%Y%m%d_%H%M)
FILENAME="backup_${DATE}.sql.gz"
FILEPATH="${BACKUP_DIR}/${FILENAME}"

# === THỰC HIỆN ===
echo "🔄 Đang backup database ${DB_NAME}..."

# Tạo thư mục backup nếu chưa có
mkdir -p "$BACKUP_DIR"

# Dump database và nén
docker exec "$CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$FILEPATH"

# Kiểm tra file tạo thành công
if [ -f "$FILEPATH" ]; then
    SIZE=$(du -sh "$FILEPATH" | cut -f1)
    echo "✅ Đã tạo file backup: $FILEPATH (${SIZE})"
else
    echo "❌ Lỗi: Không tạo được file backup!"
    exit 1
fi

# === PUSH LÊN GITHUB ===
# echo "🚀 Đang push lên GitHub..."
# git add "$FILEPATH"
# git commit -m "backup: ${FILENAME}"
# git push origin develop

echo "✅ Backup hoàn tất (Tạm thời không push tự động lên GitHub)!"
echo "📁 File: $FILEPATH"
