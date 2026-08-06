#!/usr/bin/env python3
"""Backup database to S3."""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import boto3


def backup_postgresql(db_url: str, backup_dir: Path) -> Path:
    """Create PostgreSQL backup."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"backup_{timestamp}.sql"
    
    # Extract connection params from URL
    # postgresql://user:pass@host:port/db
    parts = db_url.replace("postgresql://", "").split("@")
    creds = parts[0]
    host_db = parts[1].split("/")
    
    user, password = creds.split(":")
    host_port = host_db[0].split(":")
    db = host_db[1]
    host = host_port[0]
    port = host_port[1] if len(host_port) > 1 else "5432"
    
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    
    cmd = [
        "pg_dump",
        "-h", host,
        "-p", port,
        "-U", user,
        "-d", db,
        "-F", "p",  # Plain text format
        "-f", str(backup_file)
    ]
    
    print(f"Creating backup: {backup_file}")
    subprocess.run(cmd, env=env, check=True)
    
    return backup_file


def upload_to_s3(file_path: Path, bucket: str, s3_key: str):
    """Upload file to S3."""
    s3 = boto3.client("s3")
    
    print(f"Uploading {file_path} to s3://{bucket}/{s3_key}")
    s3.upload_file(str(file_path), bucket, s3_key)
    print("Upload completed")


def cleanup_old_backups(backup_dir: Path, retention_days: int = 30):
    """Remove old backups."""
    now = datetime.now()
    
    for backup in backup_dir.glob("backup_*.sql"):
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        age = now - mtime
        
        if age.days > retention_days:
            print(f"Removing old backup: {backup} ({age.days} days)")
            backup.unlink()


def main():
    """Run backup."""
    backup_dir = Path("/tmp/shopping_backups")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    db_url = os.getenv("DATABASE_URL")
    s3_bucket = os.getenv("S3_BUCKET")
    retention_days = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
    
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        return 1
    
    if not s3_bucket:
        print("ERROR: S3_BUCKET not set")
        return 1
    
    try:
        # Create backup
        backup_file = backup_postgresql(db_url, backup_dir)
        
        # Upload to S3
        s3_key = f"backups/{backup_file.name}"
        upload_to_s3(backup_file, s3_bucket, s3_key)
        
        # Cleanup local
        backup_file.unlink()
        
        # Cleanup old backups in S3
        # (implement with boto3 if needed)
        
        print("✅ Backup completed successfully")
        return 0
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
