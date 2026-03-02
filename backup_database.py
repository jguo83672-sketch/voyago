"""
数据库备份脚本
用于在部署前备份数据库
"""
import os
import shutil
from datetime import datetime
from pathlib import Path

def backup_database():
    """备份 SQLite 数据库"""

    # 数据库路径
    db_path = Path("instance/voyago.db")

    # 备份目录
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)

    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return False

    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"voyago_backup_{timestamp}.db"
    backup_path = backup_dir / backup_filename

    try:
        # 复制数据库文件
        shutil.copy2(db_path, backup_path)

        # 获取文件大小
        file_size = backup_path.stat().st_size / 1024  # KB

        print(f"✅ 数据库备份成功!")
        print(f"   备份文件: {backup_path}")
        print(f"   文件大小: {file_size:.2f} KB")

        # 显示最近的备份
        print("\n📁 最近的备份文件:")
        backups = sorted(backup_dir.glob("voyago_backup_*.db"), reverse=True)[:5]
        for backup in backups:
            size = backup.stat().st_size / 1024
            print(f"   - {backup.name} ({size:.2f} KB)")

        return True

    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return False


def backup_uploads():
    """备份上传文件"""

    uploads_dir = Path("static/uploads")
    backup_dir = Path("backups/uploads_backup")
    backup_dir.mkdir(parents=True, exist_ok=True)

    if not uploads_dir.exists():
        print(f"⚠️  上传目录不存在: {uploads_dir}")
        return False

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"uploads_{timestamp}"

    try:
        if backup_path.exists():
            shutil.rmtree(backup_path)

        shutil.copytree(uploads_dir, backup_path)

        # 计算文件数量和总大小
        file_count = sum(1 for _ in backup_path.rglob("*") if _.is_file())
        total_size = sum(f.stat().st_size for f in backup_path.rglob("*") if f.is_file()) / 1024 / 1024  # MB

        print(f"✅ 上传文件备份成功!")
        print(f"   备份目录: {backup_path}")
        print(f"   文件数量: {file_count}")
        print(f"   总大小: {total_size:.2f} MB")

        return True

    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return False


def main():
    print("=" * 50)
    print("Voyago 数据库备份工具")
    print("=" * 50)
    print()

    # 备份数据库
    print("📦 正在备份数据库...")
    backup_database()
    print()

    # 备份上传文件
    print("📁 正在备份上传文件...")
    backup_uploads()
    print()

    print("=" * 50)
    print("备份完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()
