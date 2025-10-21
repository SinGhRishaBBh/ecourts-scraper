"""
Case Manager Module
Handles case search, listing checks, and result processing
"""

from ecourts_scraper import CaseSearchScraper, CauseListScraper
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class CaseManager:
    """Manages case search and listing operations"""
    
    def __init__(self):
        self.case_scraper = None
        self.cause_list_scraper = None
    
    def search_case(self, search_type: str, **kwargs) -> Optional[Dict]:
        """
        Search for a case
        
        Args:
            search_type: 'cnr' or 'details'
            **kwargs: 
                For CNR: cnr
                For details: case_type, case_number, year
        
        Returns:
            Dictionary with case information and listing status
        """
        try:
            with CaseSearchScraper() as scraper:
                if search_type == 'cnr':
                    cnr = kwargs.get('cnr')
                    if not cnr:
                        logger.error("CNR not provided")
                        return None
                    result = scraper.search_case_by_cnr(cnr)
                
                elif search_type == 'details':
                    case_type = kwargs.get('case_type')
                    case_number = kwargs.get('case_number')
                    year = kwargs.get('year')
                    
                    if not all([case_type, case_number, year]):
                        logger.error("Missing case details")
                        return None
                    
                    result = scraper.search_case_by_details(case_type, case_number, year)
                
                else:
                    logger.error(f"Unknown search type: {search_type}")
                    return None
                
                if result:
                    result['search_timestamp'] = datetime.now().isoformat()
                    result['search_type'] = search_type
                
                return result
        
        except Exception as e:
            logger.error(f"Error searching case: {e}")
            return None
    
    def check_listing_status(self, case_info: Dict) -> Dict:
        """
        Check if case is listed today or tomorrow
        
        Args:
            case_info: Case information dictionary
        
        Returns:
            Dictionary with listing status details
        """
        status = {
            'is_listed': False,
            'listed_date': None,
            'days_until_listing': None,
            'status_message': 'Case not listed today or tomorrow'
        }
        
        try:
            if case_info.get('listed_today'):
                status['is_listed'] = True
                status['listed_date'] = datetime.now().date().isoformat()
                status['days_until_listing'] = 0
                status['status_message'] = 'Case is listed TODAY'
            
            elif case_info.get('listed_tomorrow'):
                status['is_listed'] = True
                tomorrow = datetime.now().date() + timedelta(days=1)
                status['listed_date'] = tomorrow.isoformat()
                status['days_until_listing'] = 1
                status['status_message'] = 'Case is listed TOMORROW'
            
            # Add additional details if available
            if case_info.get('serial_number'):
                status['serial_number'] = case_info['serial_number']
            
            if case_info.get('court_name'):
                status['court_name'] = case_info['court_name']
            
            if case_info.get('hearing_date'):
                status['hearing_date'] = case_info['hearing_date']
        
        except Exception as e:
            logger.error(f"Error checking listing status: {e}")
        
        return status
    
    def get_case_summary(self, case_info: Dict) -> Dict:
        """
        Generate a summary of case information
        
        Args:
            case_info: Case information dictionary
        
        Returns:
            Dictionary with formatted case summary
        """
        summary = {
            'case_details': case_info.get('case_info', {}),
            'listing_status': self.check_listing_status(case_info),
            'search_timestamp': case_info.get('search_timestamp'),
            'search_type': case_info.get('search_type')
        }
        
        return summary
    
    def get_cause_list_info(self) -> Dict:
        """
        Get information about available cause lists
        
        Returns:
            Dictionary with states, districts, and courts
        """
        try:
            with CauseListScraper() as scraper:
                states = scraper.get_states()
                
                cause_list_info = {
                    'states': states,
                    'total_states': len(states),
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.info(f"Retrieved cause list info for {len(states)} states")
                return cause_list_info
        
        except Exception as e:
            logger.error(f"Error getting cause list info: {e}")
            return {}
    
    def get_districts_for_state(self, state: str) -> List[str]:
        """Get districts for a specific state"""
        try:
            with CauseListScraper() as scraper:
                districts = scraper.get_districts(state)
                logger.info(f"Retrieved {len(districts)} districts for {state}")
                return districts
        except Exception as e:
            logger.error(f"Error getting districts: {e}")
            return []
    
    def get_courts_for_complex(self, state: str, district: str, complex_name: str) -> List[str]:
        """Get courts for a specific complex"""
        try:
            with CauseListScraper() as scraper:
                courts = scraper.get_courts(state, district, complex_name)
                logger.info(f"Retrieved {len(courts)} courts")
                return courts
        except Exception as e:
            logger.error(f"Error getting courts: {e}")
            return []


class CaseListingChecker:
    """Checks if cases are listed in cause lists"""
    
    def __init__(self):
        self.case_manager = CaseManager()
    
    def check_multiple_cases(self, cases: List[Dict]) -> List[Dict]:
        """
        Check listing status for multiple cases
        
        Args:
            cases: List of case dictionaries with search parameters
        
        Returns:
            List of case results with listing status
        """
        results = []
        
        for case in cases:
            search_type = case.get('search_type', 'cnr')
            
            if search_type == 'cnr':
                case_info = self.case_manager.search_case('cnr', cnr=case.get('cnr'))
            else:
                case_info = self.case_manager.search_case(
                    'details',
                    case_type=case.get('case_type'),
                    case_number=case.get('case_number'),
                    year=case.get('year')
                )
            
            if case_info:
                summary = self.case_manager.get_case_summary(case_info)
                results.append(summary)
            else:
                results.append({
                    'error': 'Failed to retrieve case information',
                    'search_params': case
                })
        
        return results
    
    def generate_report(self, results: List[Dict]) -> Dict:
        """
        Generate a report from case checking results
        
        Args:
            results: List of case results
        
        Returns:
            Dictionary with report summary
        """
        report = {
            'total_cases_checked': len(results),
            'cases_listed_today': 0,
            'cases_listed_tomorrow': 0,
            'cases_not_listed': 0,
            'errors': 0,
            'cases': results,
            'generated_at': datetime.now().isoformat()
        }
        
        for result in results:
            if 'error' in result:
                report['errors'] += 1
            else:
                listing_status = result.get('listing_status', {})
                if listing_status.get('days_until_listing') == 0:
                    report['cases_listed_today'] += 1
                elif listing_status.get('days_until_listing') == 1:
                    report['cases_listed_tomorrow'] += 1
                else:
                    report['cases_not_listed'] += 1
        
        return report
