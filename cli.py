"""
Command Line Interface for eCourts Scraper
Provides CLI options for case search, listing checks, and PDF downloads
"""

import argparse
import sys
import logging
from datetime import datetime
from typing import Optional
from case_manager import CaseManager, CaseListingChecker
from pdf_manager import PDFDownloadManager
from output_manager import OutputManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ECourtsCliApp:
    """Main CLI application for eCourts scraper"""
    
    def __init__(self):
        self.case_manager = CaseManager()
        self.listing_checker = CaseListingChecker()
        self.pdf_manager = PDFDownloadManager()
        self.output_manager = OutputManager()
    
    def search_case_by_cnr(self, cnr: str, output_format: str = 'console') -> bool:
        """Search for a case using CNR"""
        try:
            print(f"\n[*] Searching for case: {cnr}")
            case_info = self.case_manager.search_case('cnr', cnr=cnr)
            
            if case_info:
                summary = self.case_manager.get_case_summary(case_info)
                self._display_case_summary(summary)
                
                if output_format != 'console':
                    self.output_manager.save_result(summary, f"case_{cnr}", output_format)
                
                return True
            else:
                print("[!] Failed to retrieve case information")
                return False
        
        except Exception as e:
            logger.error(f"Error searching case: {e}")
            print(f"[!] Error: {e}")
            return False
    
    def search_case_by_details(self, case_type: str, case_number: str, year: str,
                              output_format: str = 'console') -> bool:
        """Search for a case using case type, number, and year"""
        try:
            print(f"\n[*] Searching for case: {case_type} {case_number}/{year}")
            case_info = self.case_manager.search_case(
                'details',
                case_type=case_type,
                case_number=case_number,
                year=year
            )
            
            if case_info:
                summary = self.case_manager.get_case_summary(case_info)
                self._display_case_summary(summary)
                
                if output_format != 'console':
                    filename = f"case_{case_type}_{case_number}_{year}"
                    self.output_manager.save_result(summary, filename, output_format)
                
                return True
            else:
                print("[!] Failed to retrieve case information")
                return False
        
        except Exception as e:
            logger.error(f"Error searching case: {e}")
            print(f"[!] Error: {e}")
            return False
    
    def check_today_listing(self, output_format: str = 'console') -> bool:
        """Check cause list for today"""
        try:
            print("\n[*] Fetching today's cause list information...")
            
            today = datetime.now().strftime('%d-%m-%Y')
            cause_list_info = self.case_manager.get_cause_list_info()
            
            print(f"[+] Available states: {cause_list_info.get('total_states', 0)}")
            print(f"[+] Timestamp: {cause_list_info.get('timestamp')}")
            
            if output_format != 'console':
                self.output_manager.save_result(cause_list_info, f"cause_list_{today}", output_format)
            
            return True
        
        except Exception as e:
            logger.error(f"Error checking today's listing: {e}")
            print(f"[!] Error: {e}")
            return False
    
    def check_tomorrow_listing(self, output_format: str = 'console') -> bool:
        """Check cause list for tomorrow"""
        try:
            print("\n[*] Fetching tomorrow's cause list information...")
            
            tomorrow = datetime.now().strftime('%d-%m-%Y')
            cause_list_info = self.case_manager.get_cause_list_info()
            
            print(f"[+] Available states: {cause_list_info.get('total_states', 0)}")
            print(f"[+] Timestamp: {cause_list_info.get('timestamp')}")
            
            if output_format != 'console':
                self.output_manager.save_result(cause_list_info, f"cause_list_tomorrow_{tomorrow}", output_format)
            
            return True
        
        except Exception as e:
            logger.error(f"Error checking tomorrow's listing: {e}")
            print(f"[!] Error: {e}")
            return False
    
    def download_cause_list(self, state: str, district: str, complex_name: str,
                           date: str, captcha: str, output_format: str = 'console') -> bool:
        """Download cause list for a specific court complex"""
        try:
            print(f"\n[*] Downloading cause list for {complex_name}, {district}, {state}")
            print(f"[*] Date: {date}")
            
            results = self.pdf_manager.download_today_cause_list(
                state, district, complex_name, date, captcha
            )
            
            if 'error' in results:
                print(f"[!] Error: {results['error']}")
                return False
            
            print(f"[+] Downloaded: {results['successful']} PDFs")
            print(f"[!] Failed: {results['failed']} PDFs")
            
            if results.get('archive'):
                print(f"[+] Archive created: {results['archive']}")
            
            if output_format != 'console':
                filename = f"download_results_{state}_{district}_{date.replace('-', '_')}"
                self.output_manager.save_result(results, filename, output_format)
            
            return True
        
        except Exception as e:
            logger.error(f"Error downloading cause list: {e}")
            print(f"[!] Error: {e}")
            return False
    
    def _display_case_summary(self, summary: dict):
        """Display case summary in console"""
        print("\n" + "="*60)
        print("CASE INFORMATION")
        print("="*60)
        
        case_details = summary.get('case_details', {})
        for key, value in case_details.items():
            print(f"{key}: {value}")
        
        print("\n" + "-"*60)
        print("LISTING STATUS")
        print("-"*60)
        
        listing_status = summary.get('listing_status', {})
        print(f"Status: {listing_status.get('status_message')}")
        
        if listing_status.get('serial_number'):
            print(f"Serial Number: {listing_status['serial_number']}")
        
        if listing_status.get('court_name'):
            print(f"Court Name: {listing_status['court_name']}")
        
        if listing_status.get('hearing_date'):
            print(f"Hearing Date: {listing_status['hearing_date']}")
        
        print("="*60 + "\n")


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description='eCourts Real-Time Cause List Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search case by CNR
  python cli.py --cnr "ABCD0123456789012345"
  
  # Search case by details
  python cli.py --case-type "Civil" --case-number "123" --year "2023"
  
  # Check today's cause list
  python cli.py --today
  
  # Check tomorrow's cause list
  python cli.py --tomorrow
  
  # Download cause list
  python cli.py --causelist --state "Delhi" --district "New Delhi" --complex "High Court" --date "01-01-2024" --captcha "ABC123"
  
  # Save output as JSON
  python cli.py --cnr "ABCD0123456789012345" --output json
        """
    )
    
    # Search options
    search_group = parser.add_argument_group('Search Options')
    search_group.add_argument('--cnr', type=str, help='Search by Case Number Reference (CNR)')
    search_group.add_argument('--case-type', type=str, help='Case type (e.g., Civil, Criminal)')
    search_group.add_argument('--case-number', type=str, help='Case number')
    search_group.add_argument('--year', type=str, help='Case year')
    
    # Listing options
    listing_group = parser.add_argument_group('Listing Options')
    listing_group.add_argument('--today', action='store_true', help='Check today\'s cause list')
    listing_group.add_argument('--tomorrow', action='store_true', help='Check tomorrow\'s cause list')
    
    # Download options
    download_group = parser.add_argument_group('Download Options')
    download_group.add_argument('--causelist', action='store_true', help='Download cause list')
    download_group.add_argument('--state', type=str, help='State name')
    download_group.add_argument('--district', type=str, help='District name')
    download_group.add_argument('--complex', type=str, help='Court complex name')
    download_group.add_argument('--date', type=str, help='Date in DD-MM-YYYY format')
    download_group.add_argument('--captcha', type=str, help='Captcha code')
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument('--output', type=str, choices=['console', 'json', 'text'],
                             default='console', help='Output format (default: console)')
    
    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    app = ECourtsCliApp()
    success = False
    
    try:
        # Handle search by CNR
        if args.cnr:
            success = app.search_case_by_cnr(args.cnr, args.output)
        
        # Handle search by case details
        elif args.case_type and args.case_number and args.year:
            success = app.search_case_by_details(
                args.case_type, args.case_number, args.year, args.output
            )
        
        # Handle today's listing
        elif args.today:
            success = app.check_today_listing(args.output)
        
        # Handle tomorrow's listing
        elif args.tomorrow:
            success = app.check_tomorrow_listing(args.output)
        
        # Handle cause list download
        elif args.causelist:
            if not all([args.state, args.district, args.complex, args.date, args.captcha]):
                print("[!] Error: --causelist requires --state, --district, --complex, --date, and --captcha")
                sys.exit(1)
            
            success = app.download_cause_list(
                args.state, args.district, args.complex, args.date, args.captcha, args.output
            )
        
        else:
            parser.print_help()
            sys.exit(0)
        
        sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"[!] Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
