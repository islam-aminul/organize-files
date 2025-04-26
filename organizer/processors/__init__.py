try:
    # When running as part of the package
    from .image_processor import ImageProcessor
    from .video_processor import VideoProcessor
    from .audio_processor import AudioProcessor
    from .document_processor import DocumentProcessor
except ImportError:
    # When running directly
    from image_processor import ImageProcessor
    from video_processor import VideoProcessor
    from audio_processor import AudioProcessor
    from document_processor import DocumentProcessor
