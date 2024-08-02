from hashlib import sha1
import time
from .helpers import *
from ckan.plugins.core import SingletonPlugin, implements
from ckanext.harvest.interfaces import IHarvester
from hashlib import sha1
import os
import logging
from ckan import model
from ckan.model import Session, Package
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from ckanext.harvest.model import HarvestJob, HarvestObject, HarvestGatherError, \
                                    HarvestObjectError
import shutil
from selenium.common.exceptions import TimeoutException
from .databaseConnection import get_tender_ids_bieter_portal_db
 
def download_tender_files_bieter(tender_id, download_dir):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument('start-maximized')
        chrome_options.add_argument('disable-infobars')
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument('--disable-dev-shm-usage')
        prefs = {
            "download.default_directory": download_dir,
            "savefile.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(options=chrome_options)

        file_path = None
        try:
            url = f'https://bieterportal.noncd.db.de/evergabe.bieter/eva/supplierportal/portal/subproject/{tender_id}/details'
            driver.get(url)
            wait = WebDriverWait(driver, 10)
            download_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Herunterladen']]")))
            download_button.click()
            wait_until_download_finishes()
            file_path = move_zip_file_to_public(download_dir)
            unzip_file(file_path,download_dir)
            return True
        except TimeoutException:
              print("Nothing to download")
              return False
        finally:
            driver.quit()
    
def gather_stage_bieter(harvest_job):
        tender_ids = get_tender_ids_bieter_portal_db()
        return process_multiple_tenders_giving_publisher(tender_ids,harvest_job,download_tender_files_bieter,"bieter_portal")
