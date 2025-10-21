"""
Output Manager Module
Handles saving results to JSON and text files
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OutputManager:
    """Manages output to files in various formats"""
    
    def __init__(self, output_dir: str = 'results'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"Output directory: {self.output_dir}")
    
    def save_result(self, data: Dict[str, Any], filename: str, format: str = 'json') -> Optional[str]:
        """
        Save result to file
        
        Args:
            data: Data to save
            filename: Base filename (without extension)
            format: Output format ('json' or 'text')
        
        Returns:
            Path to saved file or None if failed
        """
        try:
            if format == 'json':
                return self._save_json(data, filename)
            elif format == 'text':
                return self._save_text(data, filename)
            else:
                logger.error(f"Unknown format: {format}")
                return None
        
        except Exception as e:
            logger.error(f"Error saving result: {e}")
            return None
    
    def _save_json(self, data: Dict[str, Any], filename: str) -> str:
        """Save data as JSON file"""
        filepath = self.output_dir / f"{filename}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved JSON: {filepath}")
        print(f"[+] Results saved to: {filepath}")
        return str(filepath)
    
    def _save_text(self, data: Dict[str, Any], filename: str) -> str:
        """Save data as text file"""
        filepath = self.output_dir / f"{filename}.txt"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self._format_text(data))
        
        logger.info(f"Saved text: {filepath}")
        print(f"[+] Results saved to: {filepath}")
        return str(filepath)
    
    def _format_text(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Format dictionary as readable text"""
        lines = []
        prefix = "  " * indent
        
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self._format_text(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(self._format_text(item, indent + 1))
                    else:
                        lines.append(f"{prefix}  - {item}")
            else:
                lines.append(f"{prefix}{key}: {value}")
        
        return "\n".join(lines)
    
    def save_case_report(self, cases: list, filename: str = 'case_report') -> Optional[str]:
        """
        Save a report of multiple cases
        
        Args:
            cases: List of case results
            filename: Base filename
        
        Returns:
            Path to saved file
        """
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'total_cases': len(cases),
                'cases_listed_today': sum(1 for c in cases if c.get('listing_status', {}).get('days_until_listing') == 0),
                'cases_listed_tomorrow': sum(1 for c in cases if c.get('listing_status', {}).get('days_until_listing') == 1),
                'cases': cases
            }
            
            # Save as JSON
            json_path = self._save_json(report, filename)
            
            # Also save as text
            text_path = self._save_text(report, f"{filename}_text")
            
            return json_path
        
        except Exception as e:
            logger.error(f"Error saving case report: {e}")
            return None
    
    def save_download_report(self, results: Dict[str, Any], filename: str = 'download_report') -> Optional[str]:
        """
        Save a report of download results
        
        Args:
            results: Download results dictionary
            filename: Base filename
        
        Returns:
            Path to saved file
        """
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'total_downloads': results.get('total', 0),
                'successful': results.get('successful', 0),
                'failed': results.get('failed', 0),
                'success_rate': f"{(results.get('successful', 0) / max(results.get('total', 1), 1) * 100):.1f}%",
                'files': results.get('files', []),
                'errors': results.get('errors', []),
                'archive': results.get('archive')
            }
            
            # Save as JSON
            json_path = self._save_json(report, filename)
            
            # Also save as text
            text_path = self._save_text(report, f"{filename}_text")
            
            return json_path
        
        except Exception as e:
            logger.error(f"Error saving download report: {e}")
            return None
    
    def export_to_csv(self, cases: list, filename: str = 'cases_export') -> Optional[str]:
        """
        Export cases to CSV format
        
        Args:
            cases: List of case results
            filename: Base filename
        
        Returns:
            Path to saved file
        """
        try:
            import csv
            
            filepath = self.output_dir / f"{filename}.csv"
            
            if not cases:
                logger.warning("No cases to export")
                return None
            
            # Extract headers from first case
            headers = set()
            for case in cases:
                if 'case_details' in case:
                    headers.update(case['case_details'].keys())
                if 'listing_status' in case:
                    headers.update(case['listing_status'].keys())
            
            headers = sorted(list(headers))
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                
                for case in cases:
                    row = {}
                    if 'case_details' in case:
                        row.update(case['case_details'])
                    if 'listing_status' in case:
                        row.update(case['listing_status'])
                    writer.writerow(row)
            
            logger.info(f"Exported to CSV: {filepath}")
            print(f"[+] Results exported to: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return None
    
    def get_output_files(self) -> list:
        """Get list of all output files"""
        try:
            files = []
            for file_path in self.output_dir.glob('*'):
                if file_path.is_file():
                    files.append({
                        'filename': file_path.name,
                        'path': str(file_path),
                        'size_bytes': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
            
            return sorted(files, key=lambda x: x['modified'], reverse=True)
        
        except Exception as e:
            logger.error(f"Error getting output files: {e}")
            return []
    
    def cleanup_old_results(self, days: int = 30) -> Dict[str, Any]:
        """
        Remove result files older than specified days
        
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
            
            for file_path in self.output_dir.glob('*'):
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    if file_time < cutoff_time:
                        freed_space += file_path.stat().st_size
                        file_path.unlink()
                        removed_count += 1
                        logger.info(f"Removed old result: {file_path.name}")
            
            return {
                'files_removed': removed_count,
                'space_freed_bytes': freed_space,
                'space_freed_mb': round(freed_space / (1024 * 1024), 2)
            }
        
        except Exception as e:
            logger.error(f"Error cleaning up old results: {e}")
            return {'error': str(e)}
