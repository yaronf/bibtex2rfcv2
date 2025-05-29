import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BibTeXError(Exception):
    """Base exception for BibTeX-related errors."""
    pass

class InvalidInputError(BibTeXError):
    """Raised when input data is invalid."""
    pass

class FileNotFoundError(BibTeXError):
    """Raised when a required file is not found."""
    pass

class ConversionError(BibTeXError):
    """Raised when conversion from BibTeX to RFC XML fails."""
    pass 