import logging
import shutil
import json
import subprocess
from datetime import datetime
from pathlib import Path
from .base_processor import BaseProcessor

class VideoProcessor(BaseProcessor):
    def __init__(self, output_dir, dedup_data, stats):
        super().__init__(output_dir, dedup_data, stats)
        self.videos_dir = self.output_dir / 'Videos'

    def _extract_video_metadata(self, video_path):
        """Extract metadata from video using ffprobe."""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(video_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"ffprobe failed: {result.stderr}")
            
            probe_data = json.loads(result.stdout)
            format_tags = probe_data.get('format', {}).get('tags', {})
            
            # Try to get creation date from various metadata fields
            date_fields = ['creation_time', 'creationdate', 'date']
            datetime_str = None
            for field in date_fields:
                if field in format_tags:
                    datetime_str = format_tags[field]
                    break
            
            if datetime_str:
                try:
                    # Try different date formats
                    for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%d %H:%M:%S', '%Y:%m:%d %H:%M:%S']:
                        try:
                            dt = datetime.strptime(datetime_str[:19], fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        raise ValueError(f"Could not parse date: {datetime_str}")
                except Exception:
                    dt = datetime.fromtimestamp(video_path.stat().st_ctime)
            else:
                dt = datetime.fromtimestamp(video_path.stat().st_ctime)
            
            # Add timezone info
            dt = self._localize_datetime(dt)
            
            # Get make and model
            make = format_tags.get('make', '').strip()
            model = format_tags.get('model', '').strip()
            
            # Get duration
            duration = float(probe_data['format'].get('duration', 0))
            
            return {
                'datetime': dt,
                'make': make,
                'model': model,
                'duration': duration,
                'no_metadata': not bool(datetime_str and (make or model))
            }
        except Exception as e:
            logging.error(f"Error extracting metadata from video {video_path}: {str(e)}")
            # Use file creation time as fallback
            creation_time = datetime.fromtimestamp(video_path.stat().st_ctime)
            creation_time = self._localize_datetime(creation_time)
            return {
                'datetime': creation_time,
                'make': '',
                'model': '',
                'duration': 0,
                'no_metadata': True
            }

    def process(self, file_path):
        """Process video files."""
        try:
            self.stats['videos']['total'] += 1
            file_hash = self._get_file_hash(file_path)
            
            if file_hash in self.dedup_data['videos']:
                self.stats['videos']['duplicates'] += 1
                return
            
            # Extract video metadata
            metadata = self._extract_video_metadata(file_path)
            
            # Check if this is a motion photo (duration less than 5 seconds)
            is_motion_photo = metadata['duration'] > 0 and metadata['duration'] < 5.0
            
            if is_motion_photo:
                target_dir = self.videos_dir / 'MotionPhotos'
            else:
                # Use year from metadata or 0000 for unknown/invalid years
                year = str(metadata['datetime'].year)
                if metadata['no_metadata'] or year < '1970' or year > str(datetime.now().year):
                    year = '0000'
                
                target_dir = self.videos_dir / year
            
            # Construct filename with metadata
            dt = metadata['datetime']
            filename_parts = [
                f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}",
                f"{dt.hour:02d}-{dt.minute:02d}-{dt.second:02d}",
                metadata['make'],
                metadata['model']
            ]
            
            # Add duration if available
            if metadata['duration'] > 0:
                duration_str = f"{int(metadata['duration'])}s"
                filename_parts.append(duration_str)
            
            # Add original filename
            filename_parts.append(file_path.stem)
            
            # Create new filename
            new_filename = '--'.join(filter(None, filename_parts)) + file_path.suffix.lower()
            
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = self._get_unique_path(target_dir / new_filename)
            shutil.copy2(file_path, target_path)
            self.dedup_data['videos'][file_hash] = str(target_path)
            self.stats['videos']['copied'] += 1
            
        except Exception as e:
            logging.error(f"Error processing video {file_path}: {str(e)}")
            self.stats['videos']['errors'] += 1
            self.stats['videos']['skipped'] += 1
