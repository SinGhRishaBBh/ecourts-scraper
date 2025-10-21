"""
PDF Manager Module
Handles PDF downloads and file management
"""

from ecourts_scraper import CauseListDownloader
from pathlib import Path
from typing import Optional, List, Dict
import logging
from datetime import datetime
import zipfile
import os

logger = logging.getLogger(__name__)


class PDFDownloadManager:
    """Manages PDF downloads from eCourts"""
    
    def __init__(self, download_dir: str = 'downloads'):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        logger.info(f"PDF download directory: {self.download_dir}")
    
    def download_case_pdf(self, state: str, district: str, complex_name: str,
                         court_name: str, date: str, captcha: str) -> Optional[str]:
        """
        Download a case PDF
        
        Args:
            state: State name
            district: District name
            complex_name: Court complex name
            court_name: Court name
            date: Date in DD-MM-YYYY format
            captcha: Captcha code
        
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            with CauseListDownloader() as downloader:
                pdf_content = downloader.download_cause_list(
                    state, district, complex_name, court_name, date, captcha
                )
                
                if pdf_content:
                    # Create filename
                    filename = f"{state}_{district}_{court_name}_{date}.pdf"
                    filepath = self.download_dir / filename
                    
                    # Save PDF
                    with open(filepath, 'wb') as f:
                        f.write(pdf_content)
                    
                    logger.info(f"Downloaded PDF: {filepath}")
                    return str(filepath)
                else:
                    logger.warning(f"Failed to download PDF for {court_name}")
                    return None
        
        except Exception as e:
            logger.error(f"Error downloading PDF: {e}")
            return None
    
    def download_multiple_pdfs(self, downloads: List[Dict]) -> Dict:
        """
        Download multiple PDFs
        
        Args:
            downloads: List of download dictionaries with court info
        
        Returns:
            Dictionary with download results
        """
        results = {
            'total': len(downloads),
            'successful': 0,
            'failed': 0,
            'files': [],
            'errors': []
        }
        
        for idx, download_info in enumerate(downloads, 1):
            try:
                logger.info(f"Downloading {idx}/{len(downloads)}: {download_info.get('court_name')}")
                
                filepath = self.download_case_pdf(
                    download_info.get('state'),
                    download_info.get('district'),
                    download_info.get('complex_name'),
                    download_info.get('court_name'),
                    download_info.get('date'),
                    download_info.get('captcha')
                )
                
                if filepath:
                    results['successful'] += 1
                    results['files'].append({
                        'court': download_info.get('court_name'),
                        'path': filepath,
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'court': download_info.get('court_name'),
                        'reason': 'PDF download failed'
                    })
            
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'court': download_info.get('court_name'),
                    'reason': str(e)
                })
        
        logger.info(f"Download complete: {results['successful']} successful, {results['failed']} failed")
        return results
    
    def create_zip_archive(self, files: List[str], archive_name: str = 'ecourts_documents') -> Optional[str]:
        """
        Create a ZIP archive of downloaded files
        
        Args:
            files: List of file paths to include
            archive_name: Name of the ZIP archive (without .zip)
        
        Returns:
            Path to created ZIP file or None if failed
        """
        try:
            archive_path = self.download_dir / f"{archive_name}.zip"
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files:
                    if os.path.exists(file_path):
                        arcname = os.path.basename(file_path)
                        zipf.write(file_path, arcname=arcname)
                        logger.info(f"Added to archive: {arcname}")
            
            logger.info(f"Created ZIP archive: {archive_path}")
            return str(archive_path)
        
        except Exception as e:
            logger.error(f"Error creating ZIP archive: {e}")
            return None
    
    def download_today_cause_list(self, state: str, district: str, complex_name: str,
                                  date: str, captcha: str) -> Dict:
        """
        Download cause list for all courts in a complex for today
        
        Args:
            state: State name
            district: District name
            complex_name: Court complex name
            date: Date in DD-MM-YYYY format
            captcha: Captcha code
        
        Returns:
            Dictionary with download results
        """
        try:
            from ecourts_scraper import CauseListScraper
            
            with CauseListScraper() as scraper:
                courts = scraper.get_courts(state, district, complex_name)
            
            if not courts:
                logger.warning("No courts found")
                return {'error': 'No courts found'}
            
            # Prepare download list
            downloads = [
                {
                    'state': state,
                    'district': district,
                    'complex_name': complex_name,
                    'court_name': court,
                    'date': date,
                    'captcha': captcha
                }
                for court in courts
            ]
            
            # Download all PDFs
            results = self.download_multiple_pdfs(downloads)
            
            # Create ZIP archive if downloads were successful
            if results['files']:
                file_paths = [f['path'] for f in results['files']]
                archive_path = self.create_zip_archive(
                    file_paths,
                    f"cause_list_{state}_{district}_{date.replace('-', '_')}"
                )
                results['archive'] = archive_path
            
            return results
        
        except Exception as e:
            logger.error(f"Error downloading today's cause list: {e}")
            return {'error': str(e)}
    
    def get_download_history(self) -> List[Dict]:
        """
        Get list of all downloaded files
        
        Returns:
            List of downloaded files with metadata
        """
        try:
            files = []
            for file_path in self.download_dir.glob('*.pdf'):
                files.append({
                    'filename': file_path.name,
                    'path': str(file_path),
                    'size_bytes': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
            
            logger.info(f"Found {len(files)} downloaded files")
            return sorted(files, key=lambda x: x['modified'], reverse=True)
        
        except Exception as e:
            logger.error(f"Error getting download history: {e}")
            return []
    
    def cleanup_old_files(self, days: int = 30) -> Dict:
        """
        Remove files older than specified days
        
        Args:
            days: Number of days to keep files
        
        Returns:
            Dictionary with cleanup results
        """
        try:
            from datetime import timedelta
            
            cutoff_time = datetime.now() - timedelta(days=days)
            removed_count = 0
            freed_space = 0
            
            for file_path in self.download_dir.glob('*.pdf'):
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                if file_time < cutoff_time:
                    freed_space += file_path.stat().st_size
                    file_path.unlink()
                    removed_count += 1
                    logger.info(f"Removed old file: {file_path.name}")
            
            return {
                'files_removed': removed_count,
                'space_freed_bytes': freed_space,
                'space_freed_mb': round(freed_space / (1024 * 1024), 2)
            }
        
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")
            return {'error': str(e)}
