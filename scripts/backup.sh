#!/bin/bash
set -e  # Dừng script nếu có lỗi
export MSYS_NO_PATHCONV=1  # Ngăn Git Bash tự động đổi đường dẫn trên Windows

# === CẤU HÌNH ===
DB_NAME="vopc_cmcts"
DB_USER="odoo"
DB_CONTAINER="vopc_db"
ODOO_CONTAINER="vopc_odoo"
BACKUP_DIR="./backup"
DATE=$(date +%Y%m%d_%H%M)
DB_FILENAME="db_${DB_NAME}_${DATE}.sql.gz"
FILESTORE_FILENAME="filestore_${DB_NAME}_${DATE}.tar.gz"

# === THỰC HIỆN ===
echo "Dang tao thu muc backup..."
mkdir -p "$BACKUP_DIR"

echo "1. Dang backup database ${DB_NAME}..."
docker exec -T "$DB_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "${BACKUP_DIR}/${DB_FILENAME}"

echo "2. Dang backup Filestore (Hinh anh, tai lieu)..."
docker exec -T "$ODOO_CONTAINER" tar -czf - -C /var/lib/odoo/.local/share/Odoo/filestore "$DB_NAME" > "${BACKUP_DIR}/${FILESTORE_FILENAME}" || true

# Kiểm tra file tạo thành công
if [ -f "${BACKUP_DIR}/${DB_FILENAME}" ] && [ -f "${BACKUP_DIR}/${FILESTORE_FILENAME}" ]; then
    DB_SIZE=$(du -sh "${BACKUP_DIR}/${DB_FILENAME}" | cut -f1)
    FS_SIZE=$(du -sh "${BACKUP_DIR}/${FILESTORE_FILENAME}" | cut -f1)
    echo "Hoan tat backup!"
    echo "- Database: ${DB_FILENAME} (${DB_SIZE})"
    echo "- Filestore: ${FILESTORE_FILENAME} (${FS_SIZE})"
else
    echo "Loi: Khong tao duoc file backup!"
    exit 1
fi
