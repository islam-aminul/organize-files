import os
import sys

# Add the project root to PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import filedialog, messagebox
from organizer import FileOrganizer

def select_directory(title):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    directory = filedialog.askdirectory(title=title)
    return directory if directory else None

def print_stats(stats):
    """Print processing statistics."""
    print("\nProcessing Statistics:")
    print(f"Total Files Processed: {stats['total_files']}")
    print(f"Total Errors: {stats['errors']}")
    print(f"Unknown Files: {stats['unknown']['total']} (skipped: {stats['unknown']['skipped']})")
    
    categories = ['images', 'videos', 'audios', 'documents']
    for category in categories:
        print(f"\n{category.capitalize()}:")
        print(f"  Total: {stats[category]['total']}")
        print(f"  Copied: {stats[category]['copied']}")
        if category == 'images':
            print(f"  Exported: {stats[category]['exported']}")
            print(f"  No EXIF: {stats[category]['no_exif']}")
        print(f"  Duplicates: {stats[category]['duplicates']}")
        print(f"  Skipped: {stats[category]['skipped']}")
        print(f"  Errors: {stats[category]['errors']}")

def main():
    # Set console window title
    os.system(f"title FileOrganizer-{os.getenv('OS','OSUnknown')[:3]}-{os.getenv('PROCESSOR_ARCHITECTURE','').lower()}")
    # Get input directory
    input_dir = select_directory('Select Input Directory')
    if not input_dir:
        print('No input directory selected. Exiting...')
        return
    
    # Get output directory
    output_dir = select_directory('Select Output Directory')
    if not output_dir:
        print('No output directory selected. Exiting...')
        return
    
    # Create organizer and process files
    try:
        organizer = FileOrganizer(input_dir, output_dir)
        stats = organizer.organize()
        print_stats(stats)
        
        # Show completion message
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo('Complete', 'File organization completed.')
        input("Press Enter to exit...")
        
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror('Error', f'An error occurred: {str(e)}')
        input("Press Enter to exit...")

if __name__ == '__main__':
    main()
