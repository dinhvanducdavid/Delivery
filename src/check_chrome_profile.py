#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Helper script to find and list available Chrome profiles
Run this to identify which profile you should use in main.py
"""

import json
from pathlib import Path


def find_chrome_profiles():
    """Find all available Chrome profiles"""
    
    # Common Chrome profile locations
    possible_paths = [
        Path.home() / ".config" / "google-chrome",
        Path.home() / ".config" / "chromium",
        Path.home() / "snap" / "chromium" / "common" / "chromium",
        Path.home() / ".var" / "app" / "com.google.Chrome" / "config" / "google-chrome",  # Flatpak
    ]
    
    print("=" * 60)
    print("Chrome Profile Finder")
    print("=" * 60)
    
    found_profiles = False
    
    for base_path in possible_paths:
        if not base_path.exists():
            continue
            
        print(f"\n📁 Found Chrome data directory: {base_path}")
        found_profiles = True
        
        # Look for profile directories
        profiles = []
        
        # Check for Default profile
        default_profile = base_path / "Default"
        if default_profile.exists():
            # Try to read display name for Default profile
            prefs_file = default_profile / "Preferences"
            display_name = "Default"
            if prefs_file.exists():
                try:
                    with open(prefs_file, 'r', encoding='utf-8') as f:
                        prefs = json.load(f)
                    profile_display = prefs.get('profile', {}).get('name', '')
                    if profile_display:
                        display_name = f"Default ({profile_display})"
                except Exception:
                    pass
            profiles.append((display_name, default_profile))

        # Check for numbered profiles
        for i in range(1, 20):
            profile_path = base_path / f"Profile {i}"
            if profile_path.exists():
                # Try to read display name for numbered profile
                prefs_file = profile_path / "Preferences"
                display_name = f"Profile {i}"
                if prefs_file.exists():
                    try:
                        with open(prefs_file, 'r', encoding='utf-8') as f:
                            prefs = json.load(f)
                        profile_display = prefs.get('profile', {}).get('name', '')
                        if profile_display:
                            display_name = f"Profile {i} ({profile_display})"
                    except Exception:
                        pass
                profiles.append((display_name, profile_path))

        if not profiles:
            print("   ⚠️  No profiles found in this directory")
            continue
        
        print(f"\n   Found {len(profiles)} profile(s):")
        
        for profile_name, profile_path in profiles:
            # Try to read profile info
            prefs_file = profile_path / "Preferences"
            profile_info = ""
            
            if prefs_file.exists():
                try:
                    with open(prefs_file, 'r', encoding='utf-8') as f:
                        prefs = json.load(f)
                        
                    # Get profile name
                    account_info = prefs.get('account_info', [])
                    if account_info:
                        email = account_info[0].get('email', 'N/A')
                        profile_info = f" (Email: {email})"
                    
                    # Get profile display name
                    profile_display = prefs.get('profile', {}).get('name', '')
                    if profile_display:
                        profile_info = f" ({profile_display})"
                        
                except (json.JSONDecodeError, KeyError, IndexError):
                    profile_info = " (Could not read profile info)"
            
            print(f"   ✅ {profile_name}{profile_info}")
            print(f"      Path: {profile_path}")
    
    if not found_profiles:
        print("\n❌ No Chrome data directories found!")
        print("\nTroubleshooting:")
        print("1. Make sure Chrome is installed")
        print("2. Run Chrome at least once to create a profile")
        print("3. Check chrome://version/ in Chrome to see your Profile Path")
        print("4. Update the script with your custom path if needed")
    else:
        print("\n" + "=" * 60)
        print("How to use this information:")
        print("=" * 60)
        print("1. Choose the profile you're logged into JIRA with")
        print("2. Run main.py and enter the profile name when prompted")
        print("3. The script will copy your profile data automatically")
        print("\n✅ You can keep using Chrome normally while the script runs!")
        print("   The script creates a separate profile copy to avoid conflicts.")


if __name__ == '__main__':
    find_chrome_profiles()
