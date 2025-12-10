# JIRA Issue Downloader - Python 3 Version

A modernized Python 3 application for downloading JIRA issues and associated Gerrit patches using Firefox WebDriver.

## What Changed from the Original Version

### 1. **Python 3 Migration**
- ✅ Replaced `raw_input()` with `input()`
- ✅ Updated `print` statements to function calls
- ✅ Replaced deprecated `commands` module with `subprocess`
- ✅ Replaced `xlrd` with `openpyxl` for Excel handling
- ✅ Added proper UTF-8 encoding support
- ✅ Used f-strings for modern string formatting

### 2. **Browser Driver Update**
- ✅ Switched from **Chrome WebDriver** to **Firefox WebDriver**
- ✅ Removed Chrome profile dependencies
- ✅ Added Firefox-specific download preferences
- ✅ **Automatic GeckoDriver setup using `webdriver-manager`**
- ✅ **Firefox profile reuse for automatic JIRA login** (no re-login required!)
- ✅ Modern Selenium 4+ syntax with `By.XPATH` instead of deprecated methods

### 3. **Code Restructuring (OOP)**
The code has been reorganized into clean, maintainable classes:

#### **JiraConfig**
- Centralized configuration for JIRA and Gerrit URLs
- Easy to modify settings without touching core logic

#### **FileManager**
- Handles all file and directory operations
- Static methods for creating directories and renaming files
- Uses modern `pathlib` instead of `os.path`

#### **GerritManager**
- Manages all Gerrit-related operations
- SSH queries to Gerrit servers
- Date parsing and ID deduplication
- Better error handling with timeouts

#### **JiraDownloader**
- Main orchestrator class
- Handles browser setup, logging, and download workflow
- Processes Excel files and coordinates downloads
- Clean separation of concerns

### 4. **Modern Python Features**
- ✅ Type hints for better code documentation
- ✅ `pathlib.Path` for modern file handling
- ✅ Context managers and proper resource cleanup
- ✅ Better exception handling
- ✅ Structured logging with both file and console handlers

### 5. **Improved Error Handling**
- Try-except blocks for all critical operations
- Timeout protection for SSH commands (30s)
- Graceful fallbacks (e.g., using current date if ticket date not found)
- Better error messages with logging

## Installation

### Prerequisites
- Python 3.7 or higher
- Firefox browser installed

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install selenium openpyxl beautifulsoup4 webdriver-manager
```

### GeckoDriver Setup

**No manual GeckoDriver installation required!**

The script will automatically download and manage the correct version of GeckoDriver using [`webdriver-manager`](https://github.com/SergeyPirogov/webdriver_manager).

### Automatic JIRA Login (Firefox Profile Reuse)

The script automatically uses your existing Firefox profile to reuse your JIRA login session:
- **No Re-login Required**: If you're already logged into JIRA in Firefox, the script will use that session
- **Profile Detection**: The script finds your default Firefox profile automatically
- **No Interference**: You must close all Firefox windows before running the script to avoid profile conflicts

**How It Works:**
- The script locates your default Firefox profile and launches Firefox with it
- Your JIRA login session is reused for automation

**Troubleshooting Profile Issues:**
- If login doesn't work, make sure you're logged into JIRA in your default Firefox profile first
- Close all Firefox windows before running the script

## Excel File Format

### Using the Template

A template Excel file is provided in the `input/` folder. To use it:

1. Copy `input/template.xlsx` to a new file (e.g., `input/Dec_2025.xlsx`)
2. Fill in your JIRA issues following the format below
3. Save the file in the `input/` folder

**Template Structure:**

| Column A (JIRA ID) | Column B (Folder Name) |
|-------------------|----------------------|
| HSE-11094         | X5P                  |
| HSE-11095         | X6P                  |
| PROJ-123          | Feature_ABC          |

**Field Descriptions:**
- **Row 1**: Header row (will be skipped during processing)
- **Column A**: JIRA issue ID (required)
- **Column B**: Custom folder name (optional, uses JIRA ID if empty)

**Creating Your Own Excel File:**

If you don't want to use the template, create an Excel file (`.xlsx`) with:
- First row as headers: `JIRA ID` and `Folder Name`
- Each subsequent row containing a JIRA issue ID and optional folder name
- Save the file in the `input/` folder

## Usage

Run the script:
```bash
python src/main.py
```

You'll be prompted for:

1. **Project name**: Creates subfolder with this name in the output directory
2. **Excel file name**: Name of the Excel file in the `input/` folder (e.g., `Dec_2025.xlsx`)
3. **Gerrit username**: Your Gerrit SSH username (default: `lx19060027`)
4. **Sharp name**: Sharp account name (default: `lx19060027`)
5. **FIH name**: FIH account name (default: `lx19060027`)

**Example Session:**
```
============================================================
JIRA Issue Downloader - Firefox Edition
============================================================

ℹ️  This script will use your default Firefox profile to reuse sessions.
Please close all Firefox windows before running.

Enter project name: Dec_25
Enter Excel file name (e.g., issues.xlsx): Dec_2025.xlsx
Enter Gerrit username (default: lx19060027):
Enter Sharp name (default: lx19060027):
Enter FIH name (default: lx19060027):

Starting download process...
Download path: /home/duc/PycharmProjects/Delivery/output/Dec_25
Excel file: /home/duc/PycharmProjects/Delivery/input/Dec_2025.xlsx

Processing: HSE-11094 -> X5P
...
```

## Directory Structure

The script creates an `output` folder at the project root level (same level as `src` and `input`). For each JIRA issue, the following structure is created:

```
Delivery/
├── src/
│   └── main.py
├── input/
│   ├── template.xlsx          # Excel template (tracked in git)
│   └── Dec_2025.xlsx          # Your data files (ignored by git)
├── output/
│   └── <project_name>/
│       ├── logs/
│       │   └── <project_name>.log
│       └── <folder_name>/
│           ├── Investigation/     # JIRA documents (.doc)
│           ├── Source/           # Gerrit patch files (*.zip)
│           └── TestResult/       # (empty, for manual use)
└── README.md
```

**Example:**
```
Delivery/
├── src/
│   └── main.py
├── input/
│   ├── template.xlsx
│   └── Dec_2025.xlsx
├── output/
│   └── Dec_25/
│       ├── logs/
│       │   └── Dec_25.log
│       ├── X5P/
│       │   ├── Investigation/
│       │   ├── Source/
│       │   └── TestResult/
│       └── X6P/
│           ├── Investigation/
│           ├── Source/
│           └── TestResult/
```

## Features

### JIRA Integration
- ✅ Automatic JIRA document download (.doc format)
- ✅ Extracts Gerrit links from JIRA issues
- ✅ Supports multiple JIRA issue processing from Excel

### Gerrit Integration
- ✅ Supports 3 Gerrit servers:
  - `10.24.71.180` - Sharp Android Review
  - `10.24.71.91` - Sharp Internal
  - `10.230.1.88` - EP2 Server
- ✅ Automatic patch download in ZIP format
- ✅ Date filtering (only downloads patches before ticket creation)
- ✅ Automatic deduplication of Gerrit IDs
- ✅ Standardized naming: `<JIRA_ID>-01.zip`, `<JIRA_ID>-02.zip`, etc.

### Logging
- ✅ Detailed logs in `logs/<project_name>.log`
- ✅ Console output for warnings and errors
- ✅ Timestamps for all operations

## Configuration

Edit `JiraConfig` class in `main.py` to modify:

```python
class JiraConfig:
    JIRA_URL = "https://your-jira-instance.com/"
    DOWNLOAD_GERRIT_ZIP = True  # Set to False to skip Gerrit downloads
    # ... other settings
```

## Troubleshooting

### GeckoDriver Issues
```
Error: GeckoDriver not found
```
**Solution**: Ensure Firefox is installed. The script will automatically download and manage GeckoDriver. If you encounter issues, try:
```bash
pip install --upgrade webdriver-manager
```
Or specify the GeckoDriver path manually if needed.

### SSH Connection Issues
```
Timeout querying Gerrit
```
**Solution**: Ensure SSH keys are set up for Gerrit servers:
```bash
ssh-keygen -t rsa
# Add public key to Gerrit settings
```

### Excel File Not Found
```
Error: Excel file not found at /path/to/file.xlsx
```
**Solution**: Ensure the Excel file is in the specified download path.

### Permission Denied
```
Permission denied: '/home/user/Downloads'
```
**Solution**: Ensure you have write permissions to the download directory.

## Dependencies

- **selenium**: Web automation and browser control
- **openpyxl**: Excel file reading (.xlsx format)
- **beautifulsoup4**: HTML parsing (optional, included for future enhancements)
- **webdriver-manager**: Automatic GeckoDriver download and management

## License

This is an internal tool. Use according to your organization's policies.

## Notes

- The script uses Firefox in normal mode (not headless) to allow authentication if needed
- **GeckoDriver is managed automatically; no manual installation required**
- SSH access to Gerrit servers must be pre-configured
- Large downloads may take time; monitor the console output
- Logs are created for each run and can be used for debugging

> **Note:** The file `src/JSW_download_all_jira_V2.py` is provided for reference purposes only. Please do not run this script directly.