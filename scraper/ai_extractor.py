import re
from typing import List, Tuple
import requests
from bs4 import BeautifulSoup

class AIEmailExtractor:
    def __init__(self):
        self.common_domains = ['gmail.com', 'yahoo.com', 'outlook.com']
        self.business_keywords = ['contact', 'support', 'sales', 'info', 'hello']

    def extract_emails(self, text: str) -> List[str]:
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_regex, text)

    def filter_business_emails(self, emails: List[str], source_text: str) -> List[Tuple[str, float]]:
        results = []
        for email in emails:
            score = 0.0
            
            # Domain analysis
            domain = email.split('@')[-1]
            if domain not in self.common_domains:
                score += 0.4
            
            # Context analysis
            for keyword in self.business_keywords:
                if keyword in source_text.lower():
                    score += 0.2
            
            # Position analysis (emails in contact/support sections score higher)
            if 'contact' in source_text.lower() or 'support' in source_text.lower():
                score += 0.4
            
            if score >= 0.5:  # Only include emails with confidence > 50%
                results.append((email, min(score, 1.0)))
        
        return sorted(results, key=lambda x: x[1], reverse=True)
