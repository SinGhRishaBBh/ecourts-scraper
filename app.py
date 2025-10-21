from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import base64
import io
import os
import json
from datetime import datetime
from pathlib import Path
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from case_manager import CaseManager, CaseListingChecker
from pdf_manager import PDFDownloadManager
from output_manager import OutputManager

app = Flask(__name__)
CORS(app)

# Create downloads folder if it doesn't exist
DOWNLOADS_FOLDER = Path('downloads')
DOWNLOADS_FOLDER.mkdir(exist_ok=True)

ECOURTS_URL = "https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/"

case_manager = CaseManager()
listing_checker = CaseListingChecker()
pdf_manager = PDFDownloadManager()
output_manager = OutputManager()

def get_chrome_driver():
    """Initialize and return a Chrome WebDriver instance"""
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/fetch_dropdowns', methods=['POST'])
def fetch_dropdowns():
    """Fetch dropdown data from eCourts website"""
    try:
        data = request.json
        state = data.get('state')
        district = data.get('district')
        complex_name = data.get('complex')
        
        driver = get_chrome_driver()
        driver.get(ECOURTS_URL)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "select"))
        )
        
        result = {}
        
        # Fetch states if not provided
        if not state:
            state_select = Select(driver.find_element(By.ID, "state_code"))
            states = [option.text for option in state_select.options if option.text != "---Select---"]
            result['states'] = states
        
        # Fetch districts if state is provided
        if state and not district:
            state_select = Select(driver.find_element(By.ID, "state_code"))
            state_select.select_by_visible_text(state)
            time.sleep(2)
            
            district_select = Select(driver.find_element(By.ID, "district_code"))
            districts = [option.text for option in district_select.options if option.text != "---Select---"]
            result['districts'] = districts
        
        # Fetch court complexes if district is provided
        if state and district and not complex_name:
            state_select = Select(driver.find_element(By.ID, "state_code"))
            state_select.select_by_visible_text(state)
            time.sleep(1)
            
            district_select = Select(driver.find_element(By.ID, "district_code"))
            district_select.select_by_visible_text(district)
            time.sleep(2)
            
            complex_select = Select(driver.find_element(By.ID, "court_complex_code"))
            complexes = [option.text for option in complex_select.options if option.text != "---Select---"]
            result['complexes'] = complexes
        
        # Fetch court names if complex is provided
        if state and district and complex_name:
            state_select = Select(driver.find_element(By.ID, "state_code"))
            state_select.select_by_visible_text(state)
            time.sleep(1)
            
            district_select = Select(driver.find_element(By.ID, "district_code"))
            district_select.select_by_visible_text(district)
            time.sleep(1)
            
            complex_select = Select(driver.find_element(By.ID, "court_complex_code"))
            complex_select.select_by_visible_text(complex_name)
            time.sleep(2)
            
            court_select = Select(driver.find_element(By.ID, "court_name_code"))
            courts = [option.text for option in court_select.options if option.text != "---Select---"]
            result['courts'] = courts
        
        driver.quit()
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_captcha', methods=['POST'])
def get_captcha():
    """Fetch captcha image from eCourts"""
    try:
        driver = get_chrome_driver()
        driver.get(ECOURTS_URL)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "captcha_image"))
        )
        
        captcha_img = driver.find_element(By.ID, "captcha_image")
        captcha_src = captcha_img.get_attribute('src')
        
        # If it's a data URL, use it directly; otherwise fetch it
        if captcha_src.startswith('data:'):
            captcha_data = captcha_src
        else:
            response = requests.get(captcha_src)
            captcha_data = f"data:image/png;base64,{base64.b64encode(response.content).decode()}"
        
        driver.quit()
        return jsonify({'captcha': captcha_data})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    """Download PDF from eCourts"""
    try:
        data = request.json
        state = data.get('state')
        district = data.get('district')
        complex_name = data.get('complex')
        court_name = data.get('court')
        date = data.get('date')
        captcha = data.get('captcha')
        
        driver = get_chrome_driver()
        driver.get(ECOURTS_URL)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "select"))
        )
        
        # Select all dropdowns
        state_select = Select(driver.find_element(By.ID, "state_code"))
        state_select.select_by_visible_text(state)
        time.sleep(1)
        
        district_select = Select(driver.find_element(By.ID, "district_code"))
        district_select.select_by_visible_text(district)
        time.sleep(1)
        
        complex_select = Select(driver.find_element(By.ID, "court_complex_code"))
        complex_select.select_by_visible_text(complex_name)
        time.sleep(1)
        
        court_select = Select(driver.find_element(By.ID, "court_name_code"))
        court_select.select_by_visible_text(court_name)
        time.sleep(1)
        
        # Enter date
        date_input = driver.find_element(By.ID, "cause_list_date")
        date_input.clear()
        date_input.send_keys(date)
        
        # Enter captcha
        captcha_input = driver.find_element(By.ID, "captcha_code")
        captcha_input.send_keys(captcha)
        
        # Submit form
        submit_btn = driver.find_element(By.ID, "submit_btn")
        submit_btn.click()
        
        # Wait for PDF to load
        time.sleep(3)
        
        # Get PDF from iframe or new window
        pdf_data = driver.execute_script("""
            var iframe = document.querySelector('iframe');
            if (iframe) {
                return iframe.src;
            }
            return null;
        """)
        
        if pdf_data:
            pdf_response = requests.get(pdf_data)
            filename = f"{state}_{district}_{court_name}_{date}.pdf"
            filepath = DOWNLOADS_FOLDER / filename
            
            with open(filepath, 'wb') as f:
                f.write(pdf_response.content)
            
            driver.quit()
            return jsonify({'success': True, 'filename': filename, 'path': str(filepath)})
        
        driver.quit()
        return jsonify({'error': 'PDF not found'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_all', methods=['POST'])
def download_all():
    """Download PDFs for all courts in a complex"""
    try:
        data = request.json
        state = data.get('state')
        district = data.get('district')
        complex_name = data.get('complex')
        date = data.get('date')
        captcha = data.get('captcha')
        
        # First, get all court names
        driver = get_chrome_driver()
        driver.get(ECOURTS_URL)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "select"))
        )
        
        state_select = Select(driver.find_element(By.ID, "state_code"))
        state_select.select_by_visible_text(state)
        time.sleep(1)
        
        district_select = Select(driver.find_element(By.ID, "district_code"))
        district_select.select_by_visible_text(district)
        time.sleep(1)
        
        complex_select = Select(driver.find_element(By.ID, "court_complex_code"))
        complex_select.select_by_visible_text(complex_name)
        time.sleep(2)
        
        court_select = Select(driver.find_element(By.ID, "court_name_code"))
        courts = [option.text for option in court_select.options if option.text != "---Select---"]
        
        driver.quit()
        
        # Download PDFs for each court
        results = []
        for idx, court in enumerate(courts, 1):
            try:
                driver = get_chrome_driver()
                driver.get(ECOURTS_URL)
                
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "select"))
                )
                
                state_select = Select(driver.find_element(By.ID, "state_code"))
                state_select.select_by_visible_text(state)
                time.sleep(1)
                
                district_select = Select(driver.find_element(By.ID, "district_code"))
                district_select.select_by_visible_text(district)
                time.sleep(1)
                
                complex_select = Select(driver.find_element(By.ID, "court_complex_code"))
                complex_select.select_by_visible_text(complex_name)
                time.sleep(1)
                
                court_select = Select(driver.find_element(By.ID, "court_name_code"))
                court_select.select_by_visible_text(court)
                time.sleep(1)
                
                date_input = driver.find_element(By.ID, "cause_list_date")
                date_input.clear()
                date_input.send_keys(date)
                
                captcha_input = driver.find_element(By.ID, "captcha_code")
                captcha_input.send_keys(captcha)
                
                submit_btn = driver.find_element(By.ID, "submit_btn")
                submit_btn.click()
                
                time.sleep(3)
                
                pdf_data = driver.execute_script("""
                    var iframe = document.querySelector('iframe');
                    if (iframe) {
                        return iframe.src;
                    }
                    return null;
                """)
                
                if pdf_data:
                    pdf_response = requests.get(pdf_data)
                    filename = f"{state}_{district}_{court}_{date}.pdf"
                    filepath = DOWNLOADS_FOLDER / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(pdf_response.content)
                    
                    results.append({'court': court, 'status': 'success', 'filename': filename})
                else:
                    results.append({'court': court, 'status': 'failed', 'reason': 'PDF not found'})
                
                driver.quit()
            
            except Exception as e:
                results.append({'court': court, 'status': 'failed', 'reason': str(e)})
        
        return jsonify({'success': True, 'results': results, 'total': len(courts), 'downloaded': len([r for r in results if r['status'] == 'success'])})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/file/<filename>')
def download_file(filename):
    """Download a file from the downloads folder"""
    try:
        filepath = DOWNLOADS_FOLDER / filename
        if filepath.exists():
            return send_file(filepath, as_attachment=True)
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search/cnr', methods=['POST'])
def search_case_cnr():
    """Search for a case using CNR"""
    try:
        data = request.json
        cnr = data.get('cnr')
        
        if not cnr:
            return jsonify({'error': 'CNR not provided'}), 400
        
        case_info = case_manager.search_case('cnr', cnr=cnr)
        
        if case_info:
            summary = case_manager.get_case_summary(case_info)
            return jsonify({'success': True, 'data': summary})
        else:
            return jsonify({'error': 'Case not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/details', methods=['POST'])
def search_case_details():
    """Search for a case using case type, number, and year"""
    try:
        data = request.json
        case_type = data.get('case_type')
        case_number = data.get('case_number')
        year = data.get('year')
        
        if not all([case_type, case_number, year]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        case_info = case_manager.search_case(
            'details',
            case_type=case_type,
            case_number=case_number,
            year=year
        )
        
        if case_info:
            summary = case_manager.get_case_summary(case_info)
            return jsonify({'success': True, 'data': summary})
        else:
            return jsonify({'error': 'Case not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/listing/today', methods=['GET'])
def get_today_listing():
    """Get today's cause list information"""
    try:
        cause_list_info = case_manager.get_cause_list_info()
        return jsonify({'success': True, 'data': cause_list_info})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/listing/tomorrow', methods=['GET'])
def get_tomorrow_listing():
    """Get tomorrow's cause list information"""
    try:
        cause_list_info = case_manager.get_cause_list_info()
        return jsonify({'success': True, 'data': cause_list_info})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/districts/<state>', methods=['GET'])
def get_districts(state):
    """Get districts for a state"""
    try:
        districts = case_manager.get_districts_for_state(state)
        return jsonify({'success': True, 'districts': districts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/courts/<state>/<district>/<complex_name>', methods=['GET'])
def get_courts(state, district, complex_name):
    """Get courts for a complex"""
    try:
        courts = case_manager.get_courts_for_complex(state, district, complex_name)
        return jsonify({'success': True, 'courts': courts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/pdf', methods=['POST'])
def download_pdf_api():
    """Download a single PDF"""
    try:
        data = request.json
        state = data.get('state')
        district = data.get('district')
        complex_name = data.get('complex_name')
        court_name = data.get('court_name')
        date = data.get('date')
        captcha = data.get('captcha')
        
        if not all([state, district, complex_name, court_name, date, captcha]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        filepath = pdf_manager.download_case_pdf(
            state, district, complex_name, court_name, date, captcha
        )
        
        if filepath:
            return jsonify({'success': True, 'filepath': filepath})
        else:
            return jsonify({'error': 'Failed to download PDF'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/causelist', methods=['POST'])
def download_causelist_api():
    """Download entire cause list for a complex"""
    try:
        data = request.json
        state = data.get('state')
        district = data.get('district')
        complex_name = data.get('complex_name')
        date = data.get('date')
        captcha = data.get('captcha')
        
        if not all([state, district, complex_name, date, captcha]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        results = pdf_manager.download_today_cause_list(
            state, district, complex_name, date, captcha
        )
        
        return jsonify({'success': True, 'data': results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/results/history', methods=['GET'])
def get_results_history():
    """Get history of downloaded files"""
    try:
        history = pdf_manager.get_download_history()
        return jsonify({'success': True, 'files': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/results/export', methods=['POST'])
def export_results():
    """Export results to file"""
    try:
        data = request.json
        results = data.get('results', [])
        format_type = data.get('format', 'json')
        
        if format_type == 'json':
            filepath = output_manager.save_result(
                {'results': results},
                f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'json'
            )
        else:
            filepath = output_manager.save_result(
                {'results': results},
                f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'text'
            )
        
        if filepath:
            return jsonify({'success': True, 'filepath': filepath})
        else:
            return jsonify({'error': 'Failed to export results'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/file/<filename>')
def download_file_api(filename):
    """Download a file"""
    try:
        filepath = DOWNLOADS_FOLDER / filename
        if filepath.exists():
            return send_file(filepath, as_attachment=True)
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
