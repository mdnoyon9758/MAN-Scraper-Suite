"""
Exporters package for OmniScraper
Handles data export to various formats and destinations
"""

from .data_exporter import DataExporter

# Optional exports with external dependencies
try:
    from .cloud_uploader import CloudUploader
except ImportError:
    CloudUploader = None
    
try:
    from .database_exporter import DatabaseExporter
except ImportError:
    DatabaseExporter = None

try:
    from .google_sheets import GoogleSheetsExporter, upload_to_google_sheets
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

__all__ = ["DataExporter", "CloudUploader", "DatabaseExporter"]

if GOOGLE_SHEETS_AVAILABLE:
    __all__.extend(['GoogleSheetsExporter', 'upload_to_google_sheets'])
