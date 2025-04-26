import logging
import shutil
from datetime import datetime

from .base_processor import BaseProcessor


def _get_document_type(file_path):
    """Determine document type based on extension."""
    ext = file_path.suffix.lower()

    doc_types = {
        '.pdf': 'Pdf',
        '.doc': 'Word',
        '.docx': 'Word',
        '.xls': 'Excel',
        '.xlsx': 'Excel',
        '.ppt': 'Powerpoint',
        '.pptx': 'Powerpoint',
        '.txt': 'Text',
        '.rtf': 'Text',
        '.epub': 'Ebook',
        '.mobi': 'Ebook'
    }

    return doc_types.get(ext, 'others')


class DocumentProcessor(BaseProcessor):
    def __init__(self, output_dir, dedup_data, stats):
        super().__init__(output_dir, dedup_data, stats)
        self.documents_dir = self.output_dir / 'Documents'

    def process(self, file_path):
        """Process document files."""
        try:
            self.stats['documents']['total'] += 1
            file_hash = self._get_file_hash(file_path)
            
            if file_hash in self.dedup_data['documents']:
                self.stats['documents']['duplicates'] += 1
                return
            
            # Get document type
            doc_type = _get_document_type(file_path)
            target_dir = self.documents_dir / doc_type
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Get file creation/modification time
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            file_time = self._localize_datetime(file_time)
            
            # Create filename with datetime
            new_filename = f"{file_time.strftime('%Y-%m-%d--%H-%M-%S')}--{file_path.name}"
            target_path = self._get_unique_path(target_dir / new_filename)
            
            shutil.copy2(file_path, target_path)
            self.dedup_data['documents'][file_hash] = str(target_path)
            self.stats['documents']['copied'] += 1
            
        except Exception as e:
            logging.error(f"Error processing document {file_path}: {str(e)}")
            self.stats['documents']['errors'] += 1
            self.stats['documents']['skipped'] += 1
