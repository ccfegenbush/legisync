"""
Texas Legislature Data Collector
Collects bills from the current 2025 session using Texas Legislature Online API
"""
import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import os
from dataclasses import dataclass

@dataclass
class TexasBill:
    bill_number: str
    title: str
    summary: str
    full_text: str
    status: str
    introduced_date: str
    authors: List[str]
    subjects: List[str]
    session: str
    bill_type: str  # HB, SB, HR, SR, etc.

class TexasLegislatureAPI:
    """
    Texas Legislature Online API Client
    Base URL: https://capitol.texas.gov/tlodocs/89R/billtext/
    """
    
    def __init__(self):
        self.base_url = "https://capitol.texas.gov"
        self.session = "89R"  # 89th Regular Session (2025)
        self.headers = {
            'User-Agent': 'LegiSync Data Collector v1.0',
            'Accept': 'application/json'
        }
    
    def get_bill_list(self, bill_type: str = "HB", limit: int = 100) -> List[Dict]:
        """
        Get list of bills for the current session
        bill_type: HB (House Bill), SB (Senate Bill), etc.
        """
        # This is a placeholder - actual API endpoints would need to be researched
        # Texas Legislature may have different API structure
        pass
    
    def get_bill_details(self, bill_number: str) -> Optional[TexasBill]:
        """
        Get detailed information for a specific bill
        """
        pass
    
    def collect_all_bills(self, categories: List[str] = None) -> List[TexasBill]:
        """
        Collect all bills, optionally filtered by categories
        categories: ['education', 'healthcare', 'taxation', etc.]
        """
        pass

class OpenStatesAPI:
    """
    Alternative data source using OpenStates.org API
    More standardized and reliable than direct legislature APIs
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://v3.openstates.org"
        self.headers = {
            'X-API-KEY': api_key,
            'Accept': 'application/json'
        }
    
    def get_texas_bills(self, session: str = "891", limit: int = 1000) -> List[Dict]:
        """
        Get Texas bills from OpenStates API
        session: '891' for 89th Legislature, 1st session (2025)
        """
        url = f"{self.base_url}/bills"
        params = {
            'jurisdiction': 'tx',
            'session': session,
            'per_page': min(limit, 20),  # ✅ API max is 20, not 100
            'include': ['abstracts', 'other_titles', 'other_identifiers', 'sponsorships']  # ✅ Removed 'subjects' - not valid
        }
        
        bills = []
        page = 1
        
        while len(bills) < limit:
            params['page'] = page
            print(f"Fetching page {page} with params: {params}")  # Debug
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
                break
            
            data = response.json()
            page_bills = data.get('results', [])
            print(f"Got {len(page_bills)} bills from page {page}")  # Debug
            
            if not page_bills:
                break
            
            bills.extend(page_bills)
            page += 1
            time.sleep(0.1)  # Rate limiting
            
            # Safety check to avoid infinite loops
            if page > 50:  # Max 1000 bills with 20 per page
                break
        
        return bills[:limit]
    
    def format_bill(self, raw_bill: Dict) -> TexasBill:
        """
        Convert OpenStates bill format to our TexasBill format
        """
        return TexasBill(
            bill_number=raw_bill.get('identifier', ''),
            title=raw_bill.get('title', ''),
            summary=raw_bill.get('abstracts', [{}])[0].get('abstract', '') if raw_bill.get('abstracts') else '',
            full_text='',  # Would need separate API call
            status=raw_bill.get('status', ''),
            introduced_date=raw_bill.get('first_action_date', ''),
            authors=[s.get('name', '') for s in raw_bill.get('sponsorships', [])],
            subjects=raw_bill.get('subjects', []),
            session=raw_bill.get('session', ''),
            bill_type=raw_bill.get('classification', [''])[0]
        )

def main():
    """
    Example usage
    """
    # Option 1: OpenStates (recommended - more reliable)
    api_key = os.getenv("OPENSTATES_API_KEY")  # Get free API key from openstates.org
    if api_key:
        collector = OpenStatesAPI(api_key)
        bills = collector.get_texas_bills(limit=500)
        print(f"Collected {len(bills)} bills from OpenStates")
    
    # Option 2: Direct Texas Legislature API (would need implementation)
    # tx_collector = TexasLegislatureAPI()
    # bills = tx_collector.collect_all_bills()

if __name__ == "__main__":
    main()
