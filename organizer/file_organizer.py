import json
import logging
import mimetypes
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

try:
    # When running as part of the package
    from .processors import (
        ImageProcessor,
        VideoProcessor,
        AudioProcessor,
        DocumentProcessor
    )
except ImportError:
    # When running directly
    from processors import (
        ImageProcessor,
        VideoProcessor,
        AudioProcessor,
        DocumentProcessor
    )


def _get_file_type(file_path):
    """Determine file type using mimetypes."""
    try:
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            return mime_type.split('/')[0]
        return None
    except Exception as e:
        logging.error(f"Error determining file type for {file_path}: {str(e)}")
        return None


class FileOrganizer:
    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.stats = {
            'total_files': 0,
            'errors': 0,
            'images': {'total': 0, 'copied': 0, 'exported': 0, 'no_exif': 0, 'duplicates': 0, 'skipped': 0,
                       'errors': 0},
            'videos': {'total': 0, 'copied': 0, 'duplicates': 0, 'skipped': 0, 'errors': 0},
            'audios': {'total': 0, 'copied': 0, 'duplicates': 0, 'skipped': 0, 'errors': 0},
            'documents': {'total': 0, 'copied': 0, 'duplicates': 0, 'skipped': 0, 'errors': 0},
            'unknown': {'total': 0, 'skipped': 0}
        }

        # Create necessary directories
        self._create_directory_structure()

        # Initialize deduplication dataset
        self.dedup_file = self.output_dir / 'dedup_dataset.json'
        self.dedup_data = self._load_dedup_dataset()

        # Initialize processors
        self.processors = {
            'image': ImageProcessor(output_dir, self.dedup_data, self.stats),
            'video': VideoProcessor(output_dir, self.dedup_data, self.stats),
            'audio': AudioProcessor(output_dir, self.dedup_data, self.stats),
            'application': DocumentProcessor(output_dir, self.dedup_data, self.stats)
        }

        # Setup logging with timestamp in filename
        log_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = self.output_dir / f'organize_files_{log_timestamp}.log'
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )

    def _create_directory_structure(self):
        """Create the required directory structure in the output directory."""
        dirs = [
            'Images/Originals', 'Images/Export', 'Images/Collections',
            'Videos', 'Videos/MotionPhotos', 'Videos/0000',
            'Audios', 'Documents'
        ]
        for dir_path in dirs:
            (self.output_dir / dir_path).mkdir(parents=True, exist_ok=True)

    def _load_dedup_dataset(self):
        """Load or create deduplication dataset."""
        if self.dedup_file.exists():
            try:
                with open(self.dedup_file, 'r') as f:
                    return json.load(f)
            except:
                return {'images': {}, 'videos': {}, 'audios': {}, 'documents': {}}
        return {'images': {}, 'videos': {}, 'audios': {}, 'documents': {}}

    def _save_dedup_dataset(self):
        """Save deduplication dataset."""
        with open(self.dedup_file, 'w') as f:
            json.dump(self.dedup_data, f, indent=4)

    def organize(self):
        """Main function to organize files."""
        try:
            for file_path in tqdm(list(self.input_dir.rglob('*'))):
                try:
                    if not file_path.is_file() or file_path.name.startswith('.'):
                        continue

                    self.stats['total_files'] += 1
                    file_type = _get_file_type(file_path)

                    if file_type in self.processors:
                        self.processors[file_type].process(file_path)
                    else:
                        self.stats['unknown']['total'] += 1
                        self.stats['unknown']['skipped'] += 1
                        logging.info(f"Unknown file: {file_path} (type: {file_type})")
                except Exception as e:
                    logging.error(f"Error processing file {file_path}: {str(e)}")
                    self.stats['errors'] += 1

            self._save_dedup_dataset()

        except Exception as e:
            logging.error(f"Error in organize: {str(e)}")

        return self.stats
