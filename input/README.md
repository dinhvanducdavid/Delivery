# Input Folder

This folder contains Excel files for the JIRA Issue Downloader.

## Files

- **template.xlsx**: Template file for creating your JIRA issue lists (tracked in git)
- **Your data files** (e.g., `Dec_2025.xlsx`): Your actual JIRA issue lists (ignored by git)

## How to Use

1. **Copy the template:**
   ```bash
   cp input/template.xlsx input/YourProjectName.xlsx
   ```

2. **Edit your file:**
   - Open the copied file in Excel or LibreOffice
   - Fill in Column A with JIRA issue IDs (e.g., `HSE-11094`)
   - Fill in Column B with custom folder names (optional)
   - Keep the header row intact

3. **Run the script:**
   ```bash
   python src/main.py
   ```
   - When prompted for the Excel file name, enter just the filename (e.g., `YourProjectName.xlsx`)
   - **Note**: Make sure you're logged into JIRA in Chrome first. The script will copy your Chrome profile and login session automatically. You can continue using Chrome normally while the script runs!

## Excel File Format

| Column A (JIRA ID) | Column B (Folder Name) |
|-------------------|----------------------|
| HSE-11094         | X5P                  |
| HSE-11095         | X6P                  |
| PROJ-123          | Feature_ABC          |

- **Column A**: JIRA issue ID (required)
- **Column B**: Custom folder name (optional, defaults to JIRA ID)

## Note

All Excel files in this folder (except `template.xlsx`) are ignored by git to keep your data private.

