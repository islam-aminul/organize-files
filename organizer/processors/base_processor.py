import hashlib
from datetime import timezone
from pathlib import Path

import pytz


class BaseProcessor:
    def __init__(self, output_dir, dedup_data, stats):
        self.output_dir = Path(output_dir)
        self.dedup_data = dedup_data
        self.stats = stats

    def _get_file_hash(self, file_path):
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _get_unique_path(self, path):
        """Get unique path by appending number if file exists."""
        if not path.exists():
            return path
        
        base = path.stem
        extension = path.suffix
        counter = 1
        
        while True:
            new_path = path.with_name(f"{base}_{counter}{extension}")
            if not new_path.exists():
                return new_path
            counter += 1

    def _localize_datetime(self, dt):
        """Convert datetime to local timezone."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        local_tz = pytz.timezone('Asia/Kolkata')
        return dt.astimezone(local_tz)

    def process(self, file_path):
        """Process a file. Must be implemented by subclasses."""
        raise NotImplementedError
