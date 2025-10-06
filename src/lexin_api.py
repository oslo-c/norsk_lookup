"""
Lexin API module - queries the Lexin Bokmål-English dictionary.
"""

import urllib.request
import urllib.parse
import json
from typing import Optional, List, Dict
from dataclasses import dataclass


@dataclass
class Translation:
    """Represents a single translation result."""
    norwegian: str
    english: str
    part_of_speech: str
    definition: str = ""
    
    def format_short(self) -> str:
        """Format as a concise single line."""
        pos = f" ({self.part_of_speech})" if self.part_of_speech else ""
        return f"{self.norwegian}{pos} → {self.english}"
    
    def format_full(self) -> str:
        """Format with definition if available."""
        lines = [self.format_short()]
        if self.definition:
            lines.append(f"  {self.definition}")
        return "\n".join(lines)


class LexinAPI:
    """Interface to the Lexin Bokmål-English dictionary API."""
    
    BASE_URL = "https://editorportal.oslomet.no/api/v1/findwords"
    
    def __init__(self, timeout: int = 5):
        """
        Initialize the API client.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
    
    def lookup(self, word: str, max_results: int = 5) -> List[Translation]:
        """
        Look up a Norwegian word in the dictionary.
        
        Args:
            word: Norwegian word to look up
            max_results: Maximum number of results to return
            
        Returns:
            List of Translation objects
        """
        try:
            # Build request URL
            params = {
                'searchWord': word,
                'lang': 'bokmål-english',
                'page': '1',
                'selectLang': 'bokmål-english',
                'includeEngLang': '0'
            }
            
            url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
            
            # Create request with headers
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0',
                'Origin': 'https://lexin.oslomet.no',
                'Referer': 'https://lexin.oslomet.no/'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            # Make request
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            # Parse results
            translations = self._parse_results(data)
            
            # Return up to max_results
            return translations[:max_results]
            
        except Exception as e:
            # Silent failure - return empty list
            return []
    
    def _parse_results(self, data: Dict) -> List[Translation]:
        """Parse API response into Translation objects."""
        translations = []
        
        if 'result' not in data or not data['result']:
            return translations
        
        # The result is a list of lists, we want the first list
        entries = data['result'][0] if data['result'] else []
        
        # Group entries by ID to process each word entry
        entries_by_id = {}
        for entry in entries:
            entry_id = entry.get('id')
            if entry_id not in entries_by_id:
                entries_by_id[entry_id] = []
            entries_by_id[entry_id].append(entry)
        
        # Process each word entry
        for entry_id, entry_list in entries_by_id.items():
            norwegian = ""
            english = ""
            part_of_speech = ""
            definition = ""
            
            # Extract data from entries
            for entry in entry_list:
                entry_type = entry.get('type', '')
                text = entry.get('text', '')
                
                if entry_type == 'E-lem':  # Norwegian headword
                    norwegian = text
                elif entry_type == 'B-lem':  # English headword
                    english = text
                elif entry_type == 'B-kat':  # English part of speech
                    part_of_speech = text
                elif entry_type == 'B-def':  # English definition
                    definition = text
            
            # Only add if we have both Norwegian and English
            if norwegian and english:
                translations.append(Translation(
                    norwegian=norwegian,
                    english=english,
                    part_of_speech=part_of_speech,
                    definition=definition
                ))
        
        return translations
    
    def format_results(self, translations: List[Translation], include_definitions: bool = False) -> str:
        """
        Format translation results for display.
        
        Args:
            translations: List of Translation objects
            include_definitions: Whether to include definitions
            
        Returns:
            Formatted string
        """
        if not translations:
            return "No results found"
        
        if include_definitions:
            return "\n\n".join(t.format_full() for t in translations)
        else:
            return "\n".join(t.format_short() for t in translations)