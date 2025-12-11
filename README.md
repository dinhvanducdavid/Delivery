# JIRA Issue Downloader - Python 3 Version

A modernized Python 3 application for downloading JIRA issues and associated Gerrit patches using Firefox WebDriver. Available in both **GUI** and **Command-Line** modes.

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

### 6. **Configuration (`config.ini`)**
- ✅ All user inputs (project name, Excel file, usernames) are now managed in `config.ini`.
- ✅ No more repetitive command-line inputs.
- ✅ Easy to switch between different projects by modifying the config file.
- ✅ Passwords can be stored in the config file (though for security, consider environment variables for production use).

An example `config.ini` looks like this:

```ini
[settings]
project_name = Dec_2025
excel_file = input/Dec_2025.xlsx
gerrit_username = your_gerrit_username
gerrit_password = your_gerrit_password
sharp_name = your_sharp_name
fih_name = your_fih_name
```

### 7. **GUI Application** 🎉
- ✅ **User-friendly graphical interface** for easy configuration and execution
- ✅ **Edit and save `config.ini`** directly from the GUI
- ✅ **File browser** for selecting Excel files
- ✅ **Password visibility toggle** for secure password entry
- ✅ **Real-time output** display showing download progress
- ✅ **Requirements status checker** with one-click package installation (development mode)
- ✅ **Build executable** feature to create standalone applications
- ✅ **Automatic DOC to PDF conversion** using LibreOffice
- ✅ **Completion dialog** with option to open output folder
- ✅ Cross-platform support (Linux, Windows, macOS)

## Setup and Usage

### 1. Prerequisites
- Python 3.7 or higher
- Firefox browser installed
- LibreOffice (optional, for DOC to PDF conversion)
- `tkinter` (Linux users: `sudo apt-get install python3-tk`)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install selenium openpyxl beautifulsoup4 webdriver-manager pyinstaller
```

### 3. Configure `config.ini`

Before running, open the `config.ini` file and fill in your project details:

```ini
[settings]
project_name = Dec_2025
excel_file = input/Dec_2025.xlsx
gerrit_username = your_gerrit_username
gerrit_password = your_gerrit_password
```

### 4. Run the Application

#### Option A: GUI Mode (Recommended) 🎨

Launch the graphical interface:

```bash
python src/gui.py
```

**GUI Features:**
- **Configuration Editor**: Edit all settings directly in the GUI
- **File Browser**: Browse and select your Excel file
- **Password Toggle**: Show/hide password for easy verification
- **Requirements Status**: See which packages are installed (development mode only)
- **One-Click Install**: Install missing packages directly from the GUI
- **Real-Time Output**: Watch the download progress in the output window
- **Build Executable**: Create standalone applications for distribution

**Using the GUI:**
1. Fill in your configuration (project name, Excel file, credentials)
2. Click "Save Config" to persist your settings
3. Click "Run Downloader" to start the download process
4. Monitor progress in the output window
5. When complete, choose to open the output folder

#### Option B: Command-Line Mode 💻

Run the script from the terminal:

```bash
python src/main.py
```

This mode reads from `config.ini` and runs in the terminal with text output.

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

## Building Standalone Executables 📦

You can package the GUI application into a standalone executable that doesn't require Python to be installed on the target system.

### Using the GUI (Easiest Method)

1. Launch the GUI: `python src/gui.py`
2. Ensure all requirements show as "Installed" (including `pyinstaller`)
3. Click the **"Build Executable"** button
4. Wait for the build process to complete (check the output window)
5. Find your executable in the `dist/` folder

### Using the Command Line

**Important:** Build on the same platform as your target:
- Build on **Linux** for Linux executables
- Build on **Windows** for Windows executables (.exe)

```bash
cd /path/to/Delivery
pyinstaller --onefile --windowed --name "JiraDownloader" --add-data "config.ini:." --add-data "requirements.txt:." --add-data "src/main.py:src" src/gui.py
```

**Command Breakdown:**
- `--onefile`: Creates a single executable file
- `--windowed`: No console window (GUI only)
- `--name "JiraDownloader"`: Name of the executable
- `--add-data`: Bundles necessary data files
- `src/gui.py`: Entry point of the application

### Distributing the Executable

After building, you'll find the executable in the `dist/` folder:
- **Linux**: `dist/JiraDownloader`
- **Windows**: `dist/JiraDownloader.exe`

**To distribute:**
1. Copy the executable to your desired location
2. Place `config.ini` in the same directory as the executable (it will be created on first save if missing)
3. Ensure Firefox is installed on the target system
4. Run the executable

**Note:** The standalone executable:
- Does NOT require Python to be installed
- Does NOT show the "Requirements Status" section (packages are bundled)
- DOES require Firefox to be installed (for web automation)
- Creates `config.ini` automatically in its directory if not present

## Features in Detail

### DOC to PDF Conversion

The application automatically converts downloaded `.doc` files to `.pdf` format before moving them to the Investigation folder.

**Requirements:**
- LibreOffice must be installed and accessible from the command line
- On Linux: `sudo apt-get install libreoffice`
- On Windows: Install LibreOffice from [libreoffice.org](https://www.libreoffice.org/)

**Behavior:**
- If LibreOffice is available: Converts `.doc` → `.pdf` and moves PDF to Investigation folder
- If conversion fails: Falls back to moving the original `.doc` file
- Progress is logged in real-time to the GUI output window

### Smart File Handling

**Improved Zip Download Logic:**
- Waits for each download to complete before processing
- Identifies the newest file to avoid conflicts
- Handles multiple simultaneous downloads correctly
- Renames files with standardized naming: `JIRA-ID-01.zip`, `JIRA-ID-02.zip`, etc.

**Directory Structure:**
```
output/
  └── ProjectName/
      ├── logs/
      │   └── ProjectName.log
      └── FolderName/
          ├── Investigation/
          │   └── JIRA-ID.pdf
          ├── Source/
          │   ├── JIRA-ID-01.zip
          │   ├── JIRA-ID-02.zip
          │   └── JIRA-ID-03.zip
          └── TestResult/
```

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
- Save the file in the `input/` folder or anywhere and use the file browser in the GUI

## Troubleshooting

### Common Issues

**"Could not find Firefox profile"**
- Ensure Firefox is installed
- Run Firefox at least once to create a profile
- The script checks standard, Snap, and Flatpak installation paths

**"Requirements not installed" in bundled app**
- This is normal and can be ignored in standalone executables
- All dependencies are bundled with the executable
- The "Requirements Status" section is hidden in the bundled app

**"Verify it's you" prompt in Chrome**
- This issue has been resolved by switching to Firefox
- Firefox profile reuse prevents repeated authentication prompts

**Downloads not being renamed/moved**
- Ensure you have write permissions in the output directory
- Check the output log for specific error messages
- Verify that Firefox's download settings haven't been manually changed

**PDF conversion not working**
- Install LibreOffice: `sudo apt-get install libreoffice` (Linux) or download from libreoffice.org
- Ensure the `libreoffice` command is in your system's PATH
- If conversion fails, the original `.doc` file will be moved instead

**GUI doesn't open (Linux)**
- Install tkinter: `sudo apt-get install python3-tk`
- Restart your terminal after installation

## Project Structure

```
Delivery/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── config.ini               # Configuration file
├── input/                   # Input Excel files
│   ├── template.xlsx
│   └── Dec_2025.xlsx
├── output/                  # Downloaded files (created automatically)
│   └── ProjectName/
│       ├── logs/
│       └── FolderName/
│           ├── Investigation/
│           ├── Source/
│           └── TestResult/
├── src/                     # Source code
│   ├── main.py             # CLI downloader script
│   ├── gui.py              # GUI application
│   └── __pycache__/
├── test/                    # Test scripts
│   └── test_reuse_profile.py
└── dist/                    # Built executables (created by PyInstaller)
    └── JiraDownloader
```

## Development

### Running Tests

```bash
python test/test_reuse_profile.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for internal use. Please ensure you have proper authorization before using it to access JIRA and Gerrit systems.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review the output logs in `output/ProjectName/logs/`
3. Ensure all prerequisites are installed
4. Verify your `config.ini` is properly configured

---

**Version:** 3.0 with GUI  
**Last Updated:** December 2025  
**Python Version:** 3.7+  
**Supported Platforms:** Linux, Windows, macOS

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