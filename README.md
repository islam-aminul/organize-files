# File Organizer

A Python application that organizes image, video, audio, and document files from a source directory into a well-structured output directory. It uses advanced metadata extraction for better organization and supports various media types.

## Features

- Recursively processes files from input directory
- Organizes files by type (Images, Videos, Audios, Documents)
- Advanced metadata extraction:
  - Image EXIF data with timezone support
  - Video metadata using ffmpeg
  - Multiple date format support
- Smart file organization:
  - Exports resized images while maintaining aspect ratio
  - Detects motion photos based on duration (<5s)
  - Timezone-aware date handling
  - Intelligent fallback to file creation dates
- Robust error handling and deduplication
- Detailed processing statistics
- Modern GUI interface

## Requirements

- Python 3.8 or higher
- FFmpeg (for video metadata extraction)
- Required Python packages (installed automatically):
  - Pillow (for image processing)
  - tqdm (for progress bars)
  - pyinstaller (for creating executable)

## Setup and Installation

There are two ways to use this application:

### 1. Using the Executable (Recommended for Windows Users)

1. Install FFmpeg:
   - Download from https://ffmpeg.org/download.html
   - Add to system PATH

2. Run the setup:
   ```bash
   setup.bat
   ```
   This will:
   - Create a virtual environment
   - Install requirements
   - Build the executable

3. Find `FileOrganizer-{OS}-{ARCH}.exe` in the `dist` folder

### 2. Using Python (For Developers)

1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Project Structure

```
organize-files/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── setup.bat              # Windows setup script
├── file_organizer.spec    # PyInstaller config
├── organizer/             # Main package
│   ├── __init__.py
│   ├── file_organizer.py  # Core organizer class
│   └── processors/        # Media processors
│       ├── __init__.py
│       ├── base_processor.py
│       ├── image_processor.py
│       ├── video_processor.py
│       ├── audio_processor.py
│       └── document_processor.py
```

## Output Directory Structure

```
output_directory/
├── Images/
│   ├── Originals/        # Original images by year
│   │   └── yyyy/
│   ├── Export/           # Processed images by year
│   │   └── yyyy/
│   └── Collections/      # Special collections
├── Videos/
│   ├── yyyy/            # Videos by year
│   ├── 0000/            # Videos with unknown dates
│   └── MotionPhotos/    # Videos under 5 seconds
├── Audios/              # Audio files by year
│   └── yyyy/
├── Documents/           # Documents by type
│   ├── word/
│   ├── excel/
│   ├── pdf/
│   └── others/
├── dedup_dataset.json   # Deduplication database
└── organize_files.log   # Processing log
```

## Features in Detail

### Images
- Timezone-aware EXIF metadata extraction
- Multiple date format support
- Exports optimized copies:
  - RGB conversion
  - Smart resizing (max 3840x2160)
  - JPEG optimization
  - EXIF preservation
- Filename format: yyyy-mm-dd--HH-mm-ss--make--model--originalname

### Videos
- FFmpeg-based metadata extraction
- Smart motion photo detection (<5s duration)
- Multiple date format support
- Filename includes duration
- Format: yyyy-mm-dd--HH-mm-ss--make--model--duration--originalname

### Audio Files
- Year-based organization
- Creation date preservation
- Filename format: yyyy-mm-dd--HH-mm-ss--originalname

### Documents
- Type-based categorization (word, excel, pdf, etc.)
- Creation date preservation
- Filename format: yyyy-mm-dd--HH-mm-ss--originalname

## Processing Features

### Statistics
Detailed statistics for each media type:
- Total files processed
- Successfully processed files
- Files with missing metadata
- Duplicate files
- Errors and skipped files

### Error Handling
- Comprehensive error logging
- Graceful fallback strategies:
  - File creation dates when metadata missing
  - '0000' folder for unknown dates
  - Default categories for unknown types
- Continuous processing despite errors
- Detailed error reporting in GUI

### Deduplication
- SHA-256 based file hashing
- Persistent JSON deduplication database
- Cross-session duplicate detection
- Smart conflict resolution:
  - Numeric suffixes (001, 002, etc.)
  - Preserves original extensions
  - Maintains metadata

### Performance
- Asynchronous file processing
- Progress tracking with tqdm
- Memory-efficient file handling
- Optimized metadata extraction

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
