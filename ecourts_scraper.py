"""
eCourts Web Scraper Module
Handles all web scraping operations for the eCourts website
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ECOURTS_URL = "https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/"
CASE_SEARCH_URL = "https://services.ecourts.gov.in/ecourtindia_v6/?p=case_status"


class ECourtsDriver:
    """Manages Selenium WebDriver for eCourts interactions"""
    
    def __init__(self):
        self.driver = None
    
    def initialize(self):
        """Initialize Chrome WebDriver with appropriate options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        logger.info("WebDriver initialized successfully")
    
    def quit(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")
    
    def get(self, url: str):
        """Navigate to a URL"""
        self.driver.get(url)
        logger.info(f"Navigated to {url}")
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """Wait for an element to be present"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def wait_for_elements(self, by: By, value: str, timeout: int = 10):
        """Wait for elements to be present"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )


class ECourtsScraperBase:
    """Base class for eCourts scraping operations"""
    
    def __init__(self):
        self.driver_manager = ECourtsDriver()
    
    def __enter__(self):
        self.driver_manager.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver_manager.quit()
    
    @property
    def driver(self):
        return self.driver_manager.driver


class CauseListScraper(ECourtsScraperBase):
    """Scrapes cause lists from eCourts"""
    
    def get_states(self) -> List[str]:
        """Fetch list of states"""
        try:
            self.driver_manager.get(ECOURTS_URL)
            self.driver_manager.wait_for_elements(By.TAG_NAME, "select")
            
            state_select = Select(self.driver.find_element(By.ID, "state_code"))
            states = [option.text for option in state_select.options if option.text != "---Select---"]
            logger.info(f"Fetched {len(states)} states")
            return states
        except Exception as e:
            logger.error(f"Error fetching states: {e}")
            return []
    
    def get_districts(self, state: str) -> List[str]:
        """Fetch districts for a given state"""
        try:
            self.driver_manager.get(ECOURTS_URL)
            self.driver_manager.wait_for_elements(By.TAG_NAME, "select")
            
            state_select = Select(self.driver.find_element(By.ID, "state_code"))
            state_select.select_by_visible_text(state)
            time.sleep(2)
            
            district_select = Select(self.driver.find_element(By.ID, "district_code"))
            districts = [option.text for option in district_select.options if option.text != "---Select---"]
            logger.info(f"Fetched {len(districts)} districts for {state}")
            return districts
        except Exception as e:
            logger.error(f"Error fetching districts: {e}")
            return []
    
    def get_court_complexes(self, state: str, district: str) -> List[str]:
        """Fetch court complexes for a given state and district"""
        try:
            self.driver_manager.get(ECOURTS_URL)
            self.driver_manager.wait_for_elements(By.TAG_NAME, "select")
            
            state_select = Select(self.driver.find_element(By.ID, "state_code"))
            state_select.select_by_visible_text(state)
            time.sleep(1)
            
            district_select = Select(self.driver.find_element(By.ID, "district_code"))
            district_select.select_by_visible_text(district)
            time.sleep(2)
            
            complex_select = Select(self.driver.find_element(By.ID, "court_complex_code"))
            complexes = [option.text for option in complex_select.options if option.text != "---Select---"]
            logger.info(f"Fetched {len(complexes)} court complexes")
            return complexes
        except Exception as e:
            logger.error(f"Error fetching court complexes: {e}")
            return []
    
    def get_courts(self, state: str, district: str, complex_name: str) -> List[str]:
        """Fetch court names for a given complex"""
        try:
            self.driver_manager.get(ECOURTS_URL)
            self.driver_manager.wait_for_elements(By.TAG_NAME, "select")
            
            state_select = Select(self.driver.find_element(By.ID, "state_code"))
            state_select.select_by_visible_text(state)
            time.sleep(1)
            
            district_select = Select(self.driver.find_element(By.ID, "district_code"))
            district_select.select_by_visible_text(district)
            time.sleep(1)
            
            complex_select = Select(self.driver.find_element(By.ID, "court_complex_code"))
            complex_select.select_by_visible_text(complex_name)
            time.sleep(2)
            
            court_select = Select(self.driver.find_element(By.ID, "court_name_code"))
            courts = [option.text for option in court_select.options if option.text != "---Select---"]
            logger.info(f"Fetched {len(courts)} courts")
            return courts
        except Exception as e:
            logger.error(f"Error fetching courts: {e}")
            return []
    
    def get_captcha(self) -> Optional[str]:
        """Fetch captcha image as base64"""
        try:
            self.driver_manager.get(ECOURTS_URL)
            self.driver_manager.wait_for_element(By.ID, "captcha_image")
            
            captcha_img = self.driver.find_element(By.ID, "captcha_image")
            captcha_src = captcha_img.get_attribute('src')
            
            if captcha_src.startswith('data:'):
                return captcha_src
            else:
                response = requests.get(captcha_src)
                return f"data:image/png;base64,{base64.b64encode(response.content).decode()}"
        except Exception as e:
            logger.error(f"Error fetching captcha: {e}")
            return None


class CaseSearchScraper(ECourtsScraperBase):
    """Scrapes case information from eCourts"""
    
    def search_case_by_cnr(self, cnr: str) -> Optional[Dict]:
        """Search for a case using CNR (Case Number Reference)"""
        try:
            self.driver_manager.get(CASE_SEARCH_URL)
            self.driver_manager.wait_for_element(By.ID, "cnr_number")
            
            cnr_input = self.driver.find_element(By.ID, "cnr_number")
            cnr_input.clear()
            cnr_input.send_keys(cnr)
            
            # Submit form
            submit_btn = self.driver.find_element(By.ID, "submit_btn")
            submit_btn.click()
            
            time.sleep(3)
            
            # Parse results
            result = self._parse_case_results()
            logger.info(f"Case search completed for CNR: {cnr}")
            return result
        except Exception as e:
            logger.error(f"Error searching case by CNR: {e}")
            return None
    
    def search_case_by_details(self, case_type: str, case_number: str, year: str) -> Optional[Dict]:
        """Search for a case using case type, number, and year"""
        try:
            self.driver_manager.get(CASE_SEARCH_URL)
            self.driver_manager.wait_for_elements(By.TAG_NAME, "select")
            
            # Select case type
            case_type_select = Select(self.driver.find_element(By.ID, "case_type"))
            case_type_select.select_by_visible_text(case_type)
            time.sleep(1)
            
            # Enter case number
            case_num_input = self.driver.find_element(By.ID, "case_number")
            case_num_input.clear()
            case_num_input.send_keys(case_number)
            
            # Enter year
            year_input = self.driver.find_element(By.ID, "case_year")
            year_input.clear()
            year_input.send_keys(year)
            
            # Submit form
            submit_btn = self.driver.find_element(By.ID, "submit_btn")
            submit_btn.click()
            
            time.sleep(3)
            
            # Parse results
            result = self._parse_case_results()
            logger.info(f"Case search completed for {case_type} {case_number}/{year}")
            return result
        except Exception as e:
            logger.error(f"Error searching case by details: {e}")
            return None
    
    def _parse_case_results(self) -> Dict:
        """Parse case search results from the page"""
        try:
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            result = {
                'case_info': {},
                'listed_today': False,
                'listed_tomorrow': False,
                'serial_number': None,
                'court_name': None,
                'hearing_date': None
            }
            
            # Extract case information
            case_info_table = soup.find('table', {'class': 'case_info'})
            if case_info_table:
                rows = case_info_table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        key = cols[0].text.strip()
                        value = cols[1].text.strip()
                        result['case_info'][key] = value
            
            # Check if case is listed today or tomorrow
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            
            hearing_info = soup.find('div', {'class': 'hearing_info'})
            if hearing_info:
                hearing_date_text = hearing_info.find('span', {'class': 'hearing_date'})
                if hearing_date_text:
                    hearing_date_str = hearing_date_text.text.strip()
                    try:
                        hearing_date = datetime.strptime(hearing_date_str, '%d-%m-%Y').date()
                        result['hearing_date'] = hearing_date_str
                        
                        if hearing_date == today:
                            result['listed_today'] = True
                        elif hearing_date == tomorrow:
                            result['listed_tomorrow'] = True
                    except ValueError:
                        pass
                
                # Extract serial number and court name
                serial_elem = hearing_info.find('span', {'class': 'serial_number'})
                if serial_elem:
                    result['serial_number'] = serial_elem.text.strip()
                
                court_elem = hearing_info.find('span', {'class': 'court_name'})
                if court_elem:
                    result['court_name'] = court_elem.text.strip()
            
            return result
        except Exception as e:
            logger.error(f"Error parsing case results: {e}")
            return {}


class CauseListDownloader(ECourtsScraperBase):
    """Downloads cause lists from eCourts"""
    
    def download_cause_list(self, state: str, district: str, complex_name: str, 
                           court_name: str, date: str, captcha: str) -> Optional[bytes]:
        """Download cause list PDF for a specific court"""
        try:
            self.driver_manager.get(ECOURTS_URL)
            self.driver_manager.wait_for_elements(By.TAG_NAME, "select")
            
            # Select state
            state_select = Select(self.driver.find_element(By.ID, "state_code"))
            state_select.select_by_visible_text(state)
            time.sleep(1)
            
            # Select district
            district_select = Select(self.driver.find_element(By.ID, "district_code"))
            district_select.select_by_visible_text(district)
            time.sleep(1)
            
            # Select complex
            complex_select = Select(self.driver.find_element(By.ID, "court_complex_code"))
            complex_select.select_by_visible_text(complex_name)
            time.sleep(1)
            
            # Select court
            court_select = Select(self.driver.find_element(By.ID, "court_name_code"))
            court_select.select_by_visible_text(court_name)
            time.sleep(1)
            
            # Enter date
            date_input = self.driver.find_element(By.ID, "cause_list_date")
            date_input.clear()
            date_input.send_keys(date)
            
            # Enter captcha
            captcha_input = self.driver.find_element(By.ID, "captcha_code")
            captcha_input.send_keys(captcha)
            
            # Submit form
            submit_btn = self.driver.find_element(By.ID, "submit_btn")
            submit_btn.click()
            
            time.sleep(3)
            
            # Get PDF from iframe
            pdf_url = self.driver.execute_script("""
                var iframe = document.querySelector('iframe');
                if (iframe) {
                    return iframe.src;
                }
                return null;
            """)
            
            if pdf_url:
                response = requests.get(pdf_url)
                logger.info(f"Downloaded cause list for {court_name} on {date}")
                return response.content
            
            logger.warning(f"PDF not found for {court_name}")
            return None
        except Exception as e:
            logger.error(f"Error downloading cause list: {e}")
            return None
