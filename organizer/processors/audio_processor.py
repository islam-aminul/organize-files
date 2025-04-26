import logging
import shutil
from datetime import datetime
from pathlib import Path
from .base_processor import BaseProcessor

class AudioProcessor(BaseProcessor):
    def __init__(self, output_dir, dedup_data, stats):
        super().__init__(output_dir, dedup_data, stats)
        self.audios_dir = self.output_dir / 'Audios'

    def process(self, file_path):
        """Process audio files."""
        try:
            self.stats['audios']['total'] += 1
            file_hash = self._get_file_hash(file_path)
            
            if file_hash in self.dedup_data['audios']:
                self.stats['audios']['duplicates'] += 1
                return
            
            # Get file creation/modification time
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            file_time = self._localize_datetime(file_time)
            year = str(file_time.year)
            
            # Use 0000 folder for unknown years
            if year < '1970' or year > str(datetime.now().year):
                year = '0000'
            
            target_dir = self.audios_dir / year
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Create filename with datetime
            new_filename = f"{file_time.strftime('%Y-%m-%d--%H-%M-%S')}--{file_path.name}"
            target_path = self._get_unique_path(target_dir / new_filename)
            
            shutil.copy2(file_path, target_path)
            self.dedup_data['audios'][file_hash] = str(target_path)
            self.stats['audios']['copied'] += 1
            
        except Exception as e:
            logging.error(f"Error processing audio {file_path}: {str(e)}")
            self.stats['audios']['errors'] += 1
            self.stats['audios']['skipped'] += 1
