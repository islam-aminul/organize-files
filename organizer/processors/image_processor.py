import shutil
from pathlib import Path
import logging
from datetime import datetime
from PIL import Image, ExifTags
from .base_processor import BaseProcessor

class ImageProcessor(BaseProcessor):
    def __init__(self, output_dir, dedup_data, stats):
        super().__init__(output_dir, dedup_data, stats)
        self.images_dir = self.output_dir / 'Images'

    def _extract_image_metadata(self, image_path):
        """Extract EXIF metadata from image."""
        try:
            with Image.open(image_path) as img:
                if not hasattr(img, 'getexif') or img.getexif() is None:
                    return self._get_fallback_metadata(image_path)
                
                exif = {
                    ExifTags.TAGS[k]: v
                    for k, v in img.getexif().items()
                    if k in ExifTags.TAGS
                }
                
                datetime_str = exif.get('DateTime')
                make = exif.get('Make', '').strip()
                model = exif.get('Model', '').strip()
                
                if datetime_str:
                    try:
                        # Try both datetime formats
                        try:
                            dt = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
                        except ValueError:
                            dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
                        
                        dt = self._localize_datetime(dt)
                        return {
                            'datetime': dt,
                            'make': make,
                            'model': model,
                            'no_exif': False
                        }
                    except ValueError:
                        pass
                
                return self._get_fallback_metadata(image_path)
                
        except Exception as e:
            logging.error(f"Error extracting EXIF from {image_path}: {str(e)}")
            return self._get_fallback_metadata(image_path)

    def _get_fallback_metadata(self, file_path):
        """Get metadata using file creation time as fallback."""
        creation_time = datetime.fromtimestamp(file_path.stat().st_ctime)
        creation_time = self._localize_datetime(creation_time)
        return {
            'datetime': creation_time,
            'make': '',
            'model': '',
            'no_exif': True
        }

    def _export_processed_image(self, file_path, metadata):
        """Export processed image with resizing."""
        try:
            with Image.open(file_path) as img:
                # Construct filename
                dt = metadata['datetime']
                filename_parts = [
                    f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}",
                    f"{dt.hour:02d}-{dt.minute:02d}-{dt.second:02d}",
                    metadata['make'],
                    metadata['model'],
                    file_path.stem
                ]
                year_dir = f"{dt.year:04d}" if not metadata.get('no_exif') else "0000"
                
                export_filename = '--'.join(filter(None, filename_parts)) + '.jpg'
                export_dir = self.images_dir / 'Export' / year_dir
                export_dir.mkdir(parents=True, exist_ok=True)
                
                export_path = self._get_unique_path(export_dir / export_filename)
                
                # Convert to RGB, resize, and save with optimization
                width, height = img.size
                if width > 3840 or height > 2160:
                    ratio = min(3840/width, 2160/height)
                    new_size = (int(width * ratio), int(height * ratio))
                
                img.convert('RGB').resize(new_size).save(export_path, 'JPEG', exif=img.getexif(), optimize=True)
                self.stats['images']['exported'] += 1
                
        except Exception as e:
            logging.error(f"Error exporting image {file_path}: {str(e)}")
            self.stats['images']['errors'] += 1

    def process(self, file_path):
        """Process image files."""
        try:
            self.stats['images']['total'] += 1
            file_hash = self._get_file_hash(file_path)
            
            if file_hash in self.dedup_data['images']:
                self.stats['images']['duplicates'] += 1
                return
            
            # Extract metadata
            metadata = self._extract_image_metadata(file_path)
            
            # Determine target directory
            if metadata['no_exif']:
                target_dir = self.images_dir / 'Collections'
            else:
                make_model_dir = " - ".join(x for x in [metadata['make'], metadata['model']] if x)
                date_dir = f"{metadata['datetime'].year:04d}"
                target_dir = self.images_dir / 'Originals' / make_model_dir / date_dir

            # Copy original
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = self._get_unique_path(target_dir / file_path.name)
            
            shutil.copy2(file_path, target_path)
            self.dedup_data['images'][file_hash] = str(target_path)
            self.stats['images']['copied'] += 1
            
            # Export processed version
            self._export_processed_image(file_path, metadata)
            
        except Exception as e:
            logging.error(f"Error processing image {file_path}: {str(e)}")
            self.stats['images']['errors'] += 1
            self.stats['images']['skipped'] += 1
