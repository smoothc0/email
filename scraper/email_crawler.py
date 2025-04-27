import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Tuple

def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def extract_emails(text: str) -> List[str]:
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_regex, text)

def scrape_emails(base_url: str, keyword: str = '', max_emails: int = 50) -> List[Tuple[str, str]]:
    if not is_valid_url(base_url):
        raise ValueError("Invalid URL provided")
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    try:
        response = session.get(base_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch URL: {str(e)}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    emails_found = set()
    results = []
    
    # Check current page first
    page_text = soup.get_text()
    if keyword.lower() in page_text.lower():
        for email in extract_emails(page_text):
            if len(results) >= max_emails:
                break
            if email not in emails_found:
                emails_found.add(email)
                results.append((email, base_url))
    
    # Then check other pages
    for link in soup.find_all('a', href=True):
        if len(results) >= max_emails:
            break
            
        href = link['href']
        absolute_url = urljoin(base_url, href)
        
        if not is_valid_url(absolute_url) or not absolute_url.startswith(base_url):
            continue
            
        try:
            page_response = session.get(absolute_url, timeout=5)
            page_response.raise_for_status()
            page_soup = BeautifulSoup(page_response.text, 'html.parser')
            page_text = page_soup.get_text()
            
            if keyword.lower() in page_text.lower():
                for email in extract_emails(page_text):
                    if len(results) >= max_emails:
                        break
                    if email not in emails_found:
                        emails_found.add(email)
                        results.append((email, absolute_url))
        except:
            continue
    
    return results
