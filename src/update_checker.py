"""
Update checker - checks for new versions on GitHub.
"""

import urllib.request
import urllib.error
import json
import os
import time
from typing import Optional, Dict
from dataclasses import dataclass

from version import __version__


@dataclass
class UpdateInfo:
    """Information about an available update."""
    current_version: str
    latest_version: str
    download_url: str
    release_notes: str
    release_page_url: str
    
    def is_newer(self) -> bool:
        """Check if latest version is newer than current."""
        return self._compare_versions(self.latest_version, self.current_version) > 0
    
    @staticmethod
    def _compare_versions(v1: str, v2: str) -> int:
        """
        Compare two version strings (e.g., "1.2.0" vs "1.1.0").
        Returns: 1 if v1 > v2, -1 if v1 < v2, 0 if equal
        """
        def parse_version(v):
            return [int(x) for x in v.split('.')]
        
        try:
            parts1 = parse_version(v1)
            parts2 = parse_version(v2)
            
            # Pad to same length
            max_len = max(len(parts1), len(parts2))
            parts1.extend([0] * (max_len - len(parts1)))
            parts2.extend([0] * (max_len - len(parts2)))
            
            # Compare
            for p1, p2 in zip(parts1, parts2):
                if p1 > p2:
                    return 1
                elif p1 < p2:
                    return -1
            return 0
        except:
            return 0
    
    def format_notification(self) -> str:
        """Format a notification message for display."""
        msg = f"Update available: v{self.current_version} → v{self.latest_version}\n\n"
        if self.release_notes:
            # Truncate release notes if too long
            notes = self.release_notes[:200]
            if len(self.release_notes) > 200:
                notes += "..."
            msg += f"{notes}\n\n"
        msg += "Click to download"
        return msg


class UpdateChecker:
    """Checks for application updates on GitHub."""
    
    GITHUB_USER = "oslo-c"
    GITHUB_REPO = "norsk_lookup"
    
    API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
    FALLBACK_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/version.json"
    
    CHECK_INTERVAL_HOURS = 24  # Check once per day
    
    def __init__(self, cache_file: Optional[str] = None):
        """
        Initialize the update checker.
        
        Args:
            cache_file: Path to cache file for storing last check time
        """
        if cache_file is None:
            # Store in temp directory
            cache_dir = os.path.join(os.environ.get('TEMP', os.environ.get('TMP', '.')), 'NorwegianDict')
            os.makedirs(cache_dir, exist_ok=True)
            cache_file = os.path.join(cache_dir, 'update_check.json')
        
        self.cache_file = cache_file
        self.current_version = __version__
    
    def should_check(self) -> bool:
        """Check if enough time has passed since last check."""
        try:
            if not os.path.exists(self.cache_file):
                return True
            
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
            
            last_check = data.get('last_check', 0)
            hours_since_check = (time.time() - last_check) / 3600
            
            return hours_since_check >= self.CHECK_INTERVAL_HOURS
        except:
            return True
    
    def mark_checked(self):
        """Mark that we've checked for updates."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump({'last_check': time.time()}, f)
        except:
            pass
    
    def check_for_updates(self, force: bool = False) -> Optional[UpdateInfo]:
        """
        Check for updates.
        
        Args:
            force: If True, check even if recently checked
            
        Returns:
            UpdateInfo if update is available, None otherwise
        """
        if not force and not self.should_check():
            return None
        
        # Try GitHub API first
        update_info = self._check_github_api()
        
        # Fallback to version.json if API fails
        if update_info is None:
            update_info = self._check_version_file()
        
        # Mark that we checked
        self.mark_checked()
        
        # Only return if there's actually an update
        if update_info and update_info.is_newer():
            return update_info
        
        return None
    
    def _check_github_api(self) -> Optional[UpdateInfo]:
        """Check for updates using GitHub Releases API."""
        try:
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'NorwegianDictionary-UpdateChecker'
            }
            
            req = urllib.request.Request(self.API_URL, headers=headers)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            # Extract version (remove 'v' prefix if present)
            tag_name = data.get('tag_name', '')
            latest_version = tag_name.lstrip('v')
            
            # Get release notes
            release_notes = data.get('body', '').strip()
            
            # Get download URL for the installer
            download_url = None
            assets = data.get('assets', [])
            for asset in assets:
                if asset.get('name', '').endswith('.exe'):
                    download_url = asset.get('browser_download_url')
                    break
            
            # Fallback to releases page if no exe found
            if not download_url:
                download_url = data.get('html_url', '')
            
            release_page_url = data.get('html_url', '')
            
            return UpdateInfo(
                current_version=self.current_version,
                latest_version=latest_version,
                download_url=download_url,
                release_notes=release_notes,
                release_page_url=release_page_url
            )
            
        except Exception as e:
            print(f"DEBUG: GitHub API check failed: {e}")
            return None
    
    def _check_version_file(self) -> Optional[UpdateInfo]:
        """Check for updates using version.json fallback."""
        try:
            req = urllib.request.Request(self.FALLBACK_URL)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            latest_version = data.get('version', '').lstrip('v')
            download_url = data.get('download_url', '')
            release_notes = data.get('release_notes', '')
            
            # Construct release page URL
            release_page_url = f"https://github.com/{self.GITHUB_USER}/{self.GITHUB_REPO}/releases"
            
            return UpdateInfo(
                current_version=self.current_version,
                latest_version=latest_version,
                download_url=download_url,
                release_notes=release_notes,
                release_page_url=release_page_url
            )
            
        except Exception as e:
            print(f"DEBUG: Version file check failed: {e}")
            return None