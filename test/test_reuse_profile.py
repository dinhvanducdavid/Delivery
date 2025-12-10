import time
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import glob
from selenium.webdriver.common.by import By

import configparser

def find_default_firefox_profile() -> str:
    """
    Finds the default Firefox profile path by reading profiles.ini.
    This is the most reliable way to get the profile used for general browsing.
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
            # The path in the Install section is usually relative
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

# --- Constants for Login ---
# URL for the Gerrit login page
GERRIT_LOGIN_URL = "https://secure.jp.sharp/android_review/gerrit/login/"
# Your Gerrit credentials
GERRIT_USERNAME = "lx24060097"
GERRIT_PASSWORD = "3KDRixOE"


def gerrit_login(driver, username, password):
    """
    Logs into a Gerrit instance using a username/password form.
    """
    try:
        print(f"\nAttempting to log into Gerrit at: {GERRIT_LOGIN_URL}")
        driver.get(GERRIT_LOGIN_URL)
        time.sleep(3)  # Wait for the login page to load

        # Find and fill the username field
        username_field = driver.find_element(By.NAME, "username")
        username_field.clear()
        username_field.send_keys(username)
        print("   - Entered username.")

        # Find and fill the password field
        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys(password)
        print("   - Entered password.")

        # Find the login button and click it
        # Assuming the login button is an input of type 'submit' or a button element
        try:
            login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
        except:
            login_button = driver.find_element(By.NAME, "login")

        login_button.click()
        print("   - Clicked login button.")

        time.sleep(5)  # Wait for login to process
        print("\n✅ Login attempt finished.")
        return driver.get_cookies()

    except Exception as e:
        print(f"\n⚠️  Could not complete automatic login: {e}")
        print("   - The script will continue, relying on the reused profile session.")
        return None

def test_firefox_profile_reuse():
    """
    This test demonstrates how to reuse an existing Firefox profile
    to maintain cookies, sessions, and login status.
    """
    # --- Configuration ---
    # 1. Find your Firefox Profile:
    #    - Go to about:profiles in your Firefox browser.
    #    - Find the profile you want to use (it's often named "default-release").
    #    - The "Root Directory" is the path you need.

    try:
        # Find the default Firefox profile automatically by reading profiles.ini
        profile_path = find_default_firefox_profile()

        if not profile_path:
            print("❌ ERROR: Could not find the default Firefox profile.")
            print(f"   Please ensure Firefox is installed and has been run at least once.")
            print(f"   Looked in: {Path.home() / '.mozilla' / 'firefox'}")
            return

        print("="*80)
        print("Firefox Profile Reuse Test")
        print("="*80)
        print(f"Found Profile Path: {profile_path}")
        print("\n⚠️  IMPORTANT: For this to work, you MUST close ALL running Firefox windows first.")
        input("Press Enter to continue after closing all Firefox windows...")

        options = Options()

        # Add the arguments to use the existing profile
        options.add_argument("-profile")
        options.add_argument(profile_path)

        # --- Enhanced Anti-Detection Options for Firefox ---
        # Use a consistent, common User-Agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
        options.set_preference("general.useragent.override", user_agent)

        # Hide the webdriver flag
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference('useAutomationExtension', False)

        # Initialize WebDriver
        print("\n🚀 Launching Firefox with your profile...")
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)

        # --- Login to Gerrit ---
        # If reusing the profile works, this login is not strictly necessary,
        # but it demonstrates how to handle a login if needed.
        if GERRIT_USERNAME != "your_username":
            gerrit_login(driver, GERRIT_USERNAME, GERRIT_PASSWORD)
        else:
            print("\nℹ️  Skipping automatic login. Relying on saved session from profile.")
            print("   (To enable login, set GERRIT_USERNAME and GERRIT_PASSWORD at the top of the script)")

        print("\n✅ Firefox launched successfully.")

        # --- Human-like Browsing Pattern ---
        print("Navigating with a human-like pattern...")

        # 1. Start at a neutral, high-traffic site
        print("   Step 1: Visiting Google.com (to establish a natural starting point)")
        driver.get("https://www.google.com")
        time.sleep(2) # Pause to mimic reading/thinking

        # 2. Navigate to the target site
        print("   Step 2: Navigating to Gerrit to check login status")
        driver.get("https://secure.jp.sharp/android_review/gerrit/#/c/448462/")

        # Keep the browser open for a few seconds to observe
        print("\n🔎 Check the browser window. Can you see the Gerrit page correctly?")
        print("If so, the profile, cookies, and session were successfully reused!")
        print("The browser will close automatically in 20 seconds.")
        time.sleep(20)

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("\nTroubleshooting Tips:")
        print("1. Did you close ALL Firefox windows before running?")
        print("2. Is a valid Firefox profile available in ~/.mozilla/firefox/?")

    finally:
        if 'driver' in locals() and driver:
            driver.quit()
            print("\n✅ Browser closed. Test finished.")

if __name__ == '__main__':
    test_firefox_profile_reuse()
