#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
JIRA Issue Downloader - Modernized Python 3 Version
Downloads JIRA issues and associated Gerrit patches using Chrome WebDriver
"""

import configparser
import logging
import re
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import openpyxl
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService

from webdriver_manager.firefox import GeckoDriverManager


def find_default_firefox_profile() -> str:
    """
    Finds the default Firefox profile path by reading profiles.ini.
    It checks standard, Snap, and Flatpak installation paths.
    """
    possible_base_paths = [
        Path.home() / ".mozilla" / "firefox",  # Standard path
        Path.home() / "snap" / "firefox" / "common" / ".mozilla" / "firefox",  # Snap path
        Path.home() / ".var" / "app" / "org.mozilla.firefox" / ".mozilla" / "firefox",  # Flatpak path
    ]

    firefox_base_path = None
    for path in possible_base_paths:
        if path.exists():
            firefox_base_path = path
            print(f"Found Firefox configuration at: {firefox_base_path}")
            break

    if not firefox_base_path:
        print("❌ ERROR: Could not find Firefox configuration directory.")
        print("   Searched in:")
        for path in possible_base_paths:
            print(f"     - {path}")
        return ""

    profiles_ini_path = firefox_base_path / "profiles.ini"

    if not profiles_ini_path.exists():
        print(f"Warning: '{profiles_ini_path}' not found.")
        # Fallback to searching for a directory if profiles.ini is missing
        for path in firefox_base_path.iterdir():
            if path.is_dir() and (path.name.endswith(".default") or path.name.endswith(".default-release")):
                print(f"Found a likely profile directory: {path.name}")
                return str(path)
        return ""

    config = configparser.ConfigParser()
    config.read(profiles_ini_path)

    # Find the profile marked as "Default=1"
    for section in config.sections():
        if section.startswith("Profile") and 'Default' in config[section] and config[section]['Default'] == '1':
            path = config[section]['Path']
            is_relative = int(config[section].get('IsRelative', 1))
            if is_relative:
                return str(firefox_base_path / path)
            else:
                return path

    # If no profile is explicitly marked as default, try to find the one associated with the installation
    for section in config.sections():
        if section.startswith("Install") and 'Default' in config[section]:
            profile_path_str = config[section]['Default']
            return str(firefox_base_path / profile_path_str)

    # As a last resort, return the first profile listed
    for section in config.sections():
        if section.startswith("Profile"):
            path = config[section]['Path']
            is_relative = int(config[section].get('IsRelative', 1))
            print(f"Warning: No default profile found. Falling back to the first profile listed: {path}")
            if is_relative:
                return str(firefox_base_path / path)
            else:
                return path

    return ""


class JiraConfig:
    """Configuration for JIRA and Gerrit connections"""

    JIRA_URL = "https://sharp-smart-mobile-comm.atlassian.net/"
    JIRA_ISSUE_BASE_URL = "https://sharp-smart-mobile-comm.atlassian.net/browse/"
    JIRA_DOC_BASE_URL = "https://sharp-smart-mobile-comm.atlassian.net/si/jira.issueviews:issue-word/"

    GERRIT_LOGIN_URL = "https://secure.jp.sharp/android_review/gerrit/login/"
    GERRIT_ADDRESSES = {
        '10.24.71.180': 'https://secure.jp.sharp/android_review/gerrit',
        '10.24.71.91': 'http://10.24.71.91/gerrit',
        '10.230.1.88': 'http://10.230.1.88'
    }

    DOWNLOAD_GERRIT_ZIP = True


class FileManager:
    """Handles file and directory operations"""

    @staticmethod
    def create_directory(path: str) -> None:
        """Create directory if it doesn't exist"""
        path_obj = Path(path)
        if not path_obj.exists():
            path_obj.mkdir(parents=True, exist_ok=True)
            print(f"{path} created successfully")
        else:
            print(f"{path} directory exists")

    @staticmethod
    def rename_downloaded_file(source_dir: str, download_dir: str,
                               jira_id: str, num: int, log_callback) -> None:
        """Waits for a new zip file to appear and renames it."""
        download_path = Path(download_dir)
        new_name = f"{jira_id.strip()}-{str(num).zfill(2)}.zip"
        target_path = Path(source_dir) / new_name

        # Wait for the download to start by looking for a .part file
        time.sleep(1) # Give browser a moment to start download

        # Wait for the .zip file to appear
        downloaded_file = None
        for _ in range(30):  # Wait up to 30 seconds
            # Find the most recently modified zip file that isn't a temp file
            zip_files = [f for f in download_path.glob("*.zip") if not f.name.endswith('.part')]
            if zip_files:
                latest_file = max(zip_files, key=lambda f: f.stat().st_mtime)
                # A simple check to see if it's a new file
                if time.time() - latest_file.stat().st_mtime < 10:
                    downloaded_file = latest_file
                    break
            time.sleep(1)

        if downloaded_file:
            if target_path.exists():
                log_callback(f"Target file {new_name} already exists. Deleting downloaded file.")
                downloaded_file.unlink()
            else:
                shutil.move(str(downloaded_file), str(target_path))
                log_callback(f'Moved and renamed to {target_path.name}')
        else:
            log_callback(f"Error: No new zip file found for {jira_id}-{num} in {download_dir}")

        time.sleep(1) # Brief pause before next action

    @staticmethod
    def convert_and_move_doc_to_pdf(download_dir: str, investigation_dir: str, jira_id: str, log_callback) -> None:
        """Convert .doc to .pdf and move to Investigation folder."""
        download_path = Path(download_dir)
        doc_file_path = None
        for file_path in download_path.glob(f"{jira_id}.doc"):
            if file_path.is_file():
                doc_file_path = file_path
                break

        if not doc_file_path:
            log_callback(f"Warning: {jira_id}.doc not found in {download_dir}")
            return

        investigation_path = Path(investigation_dir)
        pdf_target_path = investigation_path / f"{jira_id}.pdf"

        # Check if libreoffice is available
        if shutil.which("libreoffice"):
            log_callback(f"Converting {doc_file_path.name} to PDF...")
            try:
                subprocess.run(
                    [
                        "libreoffice",
                        "--headless",
                        "--convert-to",
                        "pdf",
                        str(doc_file_path),
                        "--outdir",
                        str(download_path),
                    ],
                    check=True,
                    timeout=60,
                )

                converted_pdf_path = download_path / f"{jira_id}.pdf"

                if converted_pdf_path.exists():
                    shutil.move(str(converted_pdf_path), str(pdf_target_path))
                    log_callback(f"Moved {converted_pdf_path.name} to {pdf_target_path}")
                    doc_file_path.unlink() # remove original .doc file
                else:
                    log_callback(f"Error: PDF conversion failed for {doc_file_path.name}. Moving the .doc file instead.")
                    shutil.move(str(doc_file_path), investigation_path / doc_file_path.name)

            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                log_callback(f"Error during PDF conversion: {e}. Moving the .doc file instead.")
                shutil.move(str(doc_file_path), investigation_path / doc_file_path.name)
        else:
            log_callback("Warning: 'libreoffice' is not installed. Moving the .doc file without conversion.")
            shutil.move(str(doc_file_path), investigation_path / doc_file_path.name)

        time.sleep(2)


class GerritManager:
    """Manages Gerrit operations including querying and downloading patches"""

    def __init__(self, username: str):
        self.username = username

    def query_gerrit(self, gerrit_id: str, gerrit_address: str,
                     query_field: str = "revision") -> str:
        """Query Gerrit for specific information"""
        if query_field == "revision":
            cmd = (f"ssh -p 29418 {self.username}@{gerrit_address} "
                   f"gerrit query status:merged --format=TEXT "
                   f"--current-patch-set --files change:{gerrit_id} "
                   f"| grep 'revision:' | awk '{{print $2}}'")
        elif query_field == "lastupdated":
            cmd = (f"ssh -p 29418 {self.username}@{gerrit_address} "
                   f"gerrit query status:merged --current-patch-set "
                   f"--files change:{gerrit_id} "
                   f"| grep -i lastupdated | awk '{{print $2}}'")
        elif query_field == "project":
            cmd = (f"ssh -p 29418 {self.username}@{gerrit_address} "
                   f"gerrit query status:merged --current-patch-set "
                   f"--files change:{gerrit_id} "
                   f"| grep -i project | awk '{{print $2}}'")
        else:
            return ""

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True,
                                    text=True, timeout=30)
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            print(f"Timeout querying Gerrit for {gerrit_id}")
            return ""
        except Exception as e:
            print(f"Error querying Gerrit: {e}")
            return ""

    def get_commit_date(self, gerrit_id: str, gerrit_address: str) -> int:
        """Get commit date for a Gerrit change"""
        date_str = self.query_gerrit(gerrit_id, gerrit_address, "lastupdated")
        date_matches = re.findall(r'\d{4}-\d{2}-\d{2}', date_str)

        if date_matches:
            try:
                return int(date_matches[0].replace('-', ''))
            except (ValueError, IndexError):
                print(f"Cannot parse date for {gerrit_id}")
                return int(datetime.now().strftime("%Y%m%d"))
        return int(datetime.now().strftime("%Y%m%d"))

    @staticmethod
    def deduplicate_gerrit_ids(id_list: List[str]) -> List[str]:
        """Remove duplicate Gerrit IDs"""
        return list(set(id_list))


class JiraDownloader:
    """Main class for downloading JIRA issues and Gerrit patches"""

    def __init__(self, download_path: str):
        self.download_path = Path(download_path)
        self.browser = None
        self.logger = None
        self.gerrit_manager = None

    def setup_firefox_driver(self) -> webdriver.Firefox:
        """Configure and initialize Firefox WebDriver."""
        profile_path = find_default_firefox_profile()
        if not profile_path:
            raise FileNotFoundError("Could not find default Firefox profile.")

        options = FirefoxOptions()
        options.add_argument("-profile")
        options.add_argument(profile_path)

        # Anti-detection settings
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
        options.set_preference("general.useragent.override", user_agent)
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference('useAutomationExtension', False)

        # Set download preferences
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", str(self.download_path))
        options.set_preference("browser.download.useDownloadDir", True)
        options.set_preference('browser.download.manager.showWhenStarting', False)
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip, application/pdf, application/octet-stream")


        try:
            print("Checking and installing GeckoDriver...")
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)

            browser_version = driver.capabilities.get('browserVersion', 'Unknown')
            print(f"Firefox browser version: {browser_version}")
            if self.logger:
                self.logger.info(f"Firefox: {browser_version}")

            return driver

        except Exception as e:
            error_msg = f"Error setting up GeckoDriver: {e}"
            print(error_msg)
            if self.logger:
                self.logger.error(error_msg)
            raise

    def gerrit_login(self, username, password):
        """
        Logs into a Gerrit instance using a username/password form.
        """
        try:
            self.logger.info(f"Attempting to log into Gerrit at: {JiraConfig.GERRIT_LOGIN_URL}")
            self.browser.get(JiraConfig.GERRIT_LOGIN_URL)
            time.sleep(3)

            username_field = self.browser.find_element(By.NAME, "username")
            username_field.clear()
            username_field.send_keys(username)
            self.logger.info("Entered username.")

            password_field = self.browser.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)
            self.logger.info("Entered password.")

            try:
                login_button = self.browser.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
            except:
                login_button = self.browser.find_element(By.NAME, "login")

            login_button.click()
            self.logger.info("Clicked login button.")

            time.sleep(5)
            self.logger.info("Login attempt finished.")
            return self.browser.get_cookies()

        except Exception as e:
            self.logger.error(f"Could not complete automatic Gerrit login: {e}")
            return None

    def setup_logger(self, project_name: str) -> logging.Logger:
        """Configure logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        log_dir = self.download_path / 'logs'
        FileManager.create_directory(str(log_dir))

        log_file = log_dir / f'{project_name}.log'
        file_handler = logging.FileHandler(log_file, 'w', encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def find_gerrit_links(self) -> Tuple[List[str], List[str], List[str]]:
        """Extract Gerrit links from the current page"""
        gerrit_list_p = []
        gerrit_list_q = []
        gerrit_list_ep2 = []

        try:
            links = self.browser.find_elements(By.XPATH, "//*[@href]")

            for link in links:
                gerrit_str = link.get_attribute('href')
                if not gerrit_str:
                    continue

                # Find different Gerrit link patterns
                if '/#/c/' in gerrit_str and 'gerrit' not in gerrit_str:
                    self.logger.info(f"Found EP2 link: {gerrit_str}")
                    ids = re.findall(r'\d+', gerrit_str)
                    gerrit_list_ep2.extend([i for i in ids if 4 < len(i) < 10])

                elif 'gerrit/#/c/' in gerrit_str:
                    self.logger.info(f"Found P link: {gerrit_str}")
                    ids = re.findall(r'\d+', gerrit_str)
                    if ids and 4 < len(ids[0]) < 10:
                        gerrit_list_p.append(ids[0])

                elif 'gerrit/' in gerrit_str:
                    self.logger.info(f"Found Q link: {gerrit_str}")
                    ids = re.findall(r'\d+', gerrit_str)
                    gerrit_list_q.extend([i for i in ids if 5 < len(i) < 10])

        except Exception as e:
            self.logger.error(f"Error finding Gerrit links: {e}")

        return gerrit_list_p, gerrit_list_q, gerrit_list_ep2

    def find_ticket_date(self) -> int:
        """Extract ticket creation date from the page"""
        try:
            links = self.browser.find_elements(By.XPATH, "//*[@href]")
            date_list = []

            for link in links:
                date_str = link.get_attribute('href')
                if date_str and 'from' in date_str:
                    link_dates = re.findall(r'\d{4}-\d{2}-\d{2}', date_str)
                    if link_dates:
                        date_int = int(date_str.split('=')[-1].replace('-', ''))
                        date_list.append(date_int)

            if date_list:
                date_list.sort()
                return date_list[0]

        except Exception as e:
            self.logger.warning(f"Cannot find ticket date: {e}")

        # Return current date as fallback
        return int(datetime.now().strftime("%Y%m%d"))

    def download_gerrit_patches(self, jira_id: str, gerrit_list: List[str],
                                source_dir: str, gerrit_address: str) -> None:
        """Download Gerrit patches as zip files"""
        if not JiraConfig.DOWNLOAD_GERRIT_ZIP:
            return

        # ticket_date = self.find_ticket_date()
        # self.logger.info(f"Ticket date: {ticket_date}")
        # print(f"Ticket date: {ticket_date}")

        num = 0
        for gerrit_id in gerrit_list:
            try:
                # Get revision ID
                revision_id = self.gerrit_manager.query_gerrit(
                    gerrit_id, gerrit_address, "revision"
                )

                if not revision_id:
                    continue

                self.logger.info(f"Revision ID: {revision_id}")

                # # Get commit date
                # commit_date = self.gerrit_manager.get_commit_date(
                #     gerrit_id, gerrit_address
                # )
                # print(f"Commit date: {commit_date}")
                # self.logger.info(f"Commit date: {commit_date}")

                # # Only download if commit is before or on ticket date
                # if commit_date <= ticket_date:
                # Build download URL based on Gerrit server
                if gerrit_address == '10.24.71.180':
                    download_url = (f"https://secure.jp.sharp/android_review"
                                    f"/gerrit/changes/{gerrit_id}/revisions"
                                    f"/{revision_id}/patch?zip")
                else:  # 10.24.71.91
                    download_url = (f"http://10.24.71.91/gerrit/changes/{gerrit_id}"
                                    f"/revisions/{revision_id}/patch?zip")

                # Open download in new window
                js = f"window.open('{download_url}')"
                print(f"Downloading: {download_url}")
                self.browser.execute_script(js)

                num += 1
                time.sleep(2)

                # Rename the downloaded file
                FileManager.rename_downloaded_file(
                    source_dir, str(self.download_path), jira_id, num, self.logger.info
                )

            except Exception as e:
                self.logger.error(f"Error downloading Gerrit {gerrit_id}: {e}")
                continue

    def download_jira_issue(self, jira_id: str, folder_name: str) -> None:
        """Download JIRA issue document and associated Gerrit patches"""
        # Create directory structure
        base_dir = self.download_path / folder_name
        doc_dir = base_dir / "Investigation"
        source_dir = base_dir / "Source"
        test_dir = base_dir / "TestResult"

        for directory in [doc_dir, source_dir, test_dir]:
            FileManager.create_directory(str(directory))

        jira_url = JiraConfig.JIRA_ISSUE_BASE_URL + jira_id

        try:
            # Navigate to JIRA issue
            self.browser.get(jira_url)
            time.sleep(2)

            # Download JIRA document
            doc_url = (f"{JiraConfig.JIRA_DOC_BASE_URL}{jira_id}/"
                       f"{jira_id}.doc")
            js = f"window.open('{doc_url}')"
            self.browser.execute_script(js)
            time.sleep(2)

            # Convert and move downloaded .doc file to Investigation folder
            FileManager.convert_and_move_doc_to_pdf(str(self.download_path), str(doc_dir), jira_id, self.logger.info)

            # Find and download Gerrit patches
            gerrit_list_p, gerrit_list_q, gerrit_list_ep2 = self.find_gerrit_links()

            if gerrit_list_p:
                unique_list = GerritManager.deduplicate_gerrit_ids(gerrit_list_p)
                self.download_gerrit_patches(
                    jira_id, unique_list, str(source_dir), '10.24.71.180'
                )

            if gerrit_list_q:
                unique_list = GerritManager.deduplicate_gerrit_ids(gerrit_list_q)
                self.download_gerrit_patches(
                    jira_id, unique_list, str(source_dir), '10.24.71.91'
                )

            if gerrit_list_ep2:
                unique_list = GerritManager.deduplicate_gerrit_ids(gerrit_list_ep2)
                self.download_gerrit_patches(
                    jira_id, unique_list, str(source_dir), '10.230.1.88'
                )

        except Exception as e:
            self.logger.error(f"Error downloading JIRA {jira_id}: {e}")
            time.sleep(3)

    def process_excel_file(self, excel_path: str, gerrit_username: str, gerrit_password: str) -> None:
        """Process Excel file and download all JIRA issues"""
        try:
            # Setup
            self.browser = self.setup_firefox_driver()
            self.gerrit_manager = GerritManager(gerrit_username)

            # Perform Gerrit login
            self.gerrit_login(gerrit_username, gerrit_password)

            # Load Excel file
            workbook = openpyxl.load_workbook(excel_path)
            sheet = workbook.active

            # Process each row (skip header)
            for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                if not row[0]:  # Skip empty rows
                    continue

                jira_id = str(row[0]).strip()
                folder_name = str(row[1]).strip() if len(row) > 1 else jira_id

                # Handle list format in cell
                if '[' in jira_id and ']' in jira_id:
                    try:
                        import ast
                        parsed = ast.literal_eval(jira_id)
                        if isinstance(parsed, list) and len(parsed) > 0:
                            jira_id = str(parsed[0]).strip()
                    except:
                        pass

                print(f"\nProcessing: {jira_id} -> {folder_name}")
                self.logger.info(f"Processing: {jira_id} -> {folder_name}")

                self.download_jira_issue(jira_id, folder_name)

            workbook.close()

        finally:
            if self.browser:
                self.browser.quit()


def main():
    """Main entry point"""
    # Get the directory of the current script (main.py)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Load configuration
    config = configparser.ConfigParser()
    config.read(project_root / 'config.ini')
    settings = config['settings']

    project_name = settings.get('project_name', '').strip()
    excel_file_name = settings.get('excel_file', '').strip()
    gerrit_username = settings.get('gerrit_username', 'lx24060097').strip()
    gerrit_password = settings.get('gerrit_password', '').strip()
    name_sharp = settings.get('sharp_name', 'lx24060097').strip()
    name_fih = settings.get('fih_name', 'lx24060097').strip()

    print("=" * 60)
    print("JIRA Issue Downloader - Firefox Edition")
    print("=" * 60)
    print(f"Project: {project_name}")
    print(f"Excel File: {excel_file_name}")
    print(f"Gerrit User: {gerrit_username}")
    print("\nℹ️  This script will use your default Firefox profile to reuse sessions.")
    print("Please close all Firefox windows before running.\n")
    input("Press Enter to continue...")

    if not project_name:
        project_name = input('Enter project name: ').strip()
        if not project_name:
            print("Project name is required!")
            return

    input_dir = project_root / "input"

    if not excel_file_name:
        excel_file_name = input('Enter Excel file name (e.g., issues.xlsx): ').strip()
        if not excel_file_name:
            print('Excel file name is required.')
            return

    # If the user provides an absolute path, use it; otherwise, use the input directory
    excel_file_path = Path(excel_file_name)
    if not excel_file_path.is_absolute():
        excel_file_path = project_root / excel_file_path

    if not excel_file_path.exists():
        print(f'Error: Excel file not found at {excel_file_path}')
        return

    if not gerrit_password:
        # It's recommended to use a more secure method like environment variables or a config file for passwords
        gerrit_password = input('Enter Gerrit password: ').strip()
        if not gerrit_password:
            print("Gerrit password is required for login.")
            return


    # Build paths - create output folder at project root (same level as src)
    project_root = script_dir.parent  # Go up one level from src to project root
    output_base = project_root / "output"
    base_download_path = str(output_base / project_name)

    # Create downloader instance
    downloader = JiraDownloader(base_download_path)

    # Setup logging
    downloader.logger = downloader.setup_logger(project_name)
    downloader.logger.info("[START] JIRA Download Process")

    print(f"\nStarting download process...")
    print(f"Download path: {base_download_path}")
    print(f"Excel file: {excel_file_path}")

    try:
        downloader.process_excel_file(
            str(excel_file_path), gerrit_username, gerrit_password
        )
        print("\n" + "=" * 60)
        print("Download process completed successfully!")
        print("=" * 60)
        downloader.logger.info("[END] JIRA Download Process - Success")

    except Exception as e:
        print(f"\nError during download process: {e}")
        if downloader.logger:
            downloader.logger.error(f"[END] JIRA Download Process - Error: {e}")
        raise


if __name__ == '__main__':
    main()
