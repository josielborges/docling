import requests
from xml.etree import ElementTree as ET
import re

def parse_sitemap(sitemap_url):
    """
    Takes a sitemap.xml URL and returns a list of all URLs contained in it.
    
    Args:
        sitemap_url (str): URL of the sitemap.xml file
        
    Returns:
        list: List of URLs extracted from the sitemap
    """
    try:
        # Make HTTP request to the sitemap
        response = requests.get(sitemap_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Extract XML content
        xml_content = response.text
        
        return _parse_regular_sitemap(xml_content)
    
    except requests.exceptions.RequestException as e:
        print(f"Error accessing sitemap: {e}")
        return []
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return []

def _parse_regular_sitemap(xml_content):
    """
    Parses a regular sitemap and extracts URLs.
    """
    urls = []
    root = ET.fromstring(xml_content)
    
    # Define default namespace (if any)
    namespace = ''
    match = re.search(r'xmlns="([^"]+)"', xml_content)
    if match:
        namespace = '{' + match.group(1) + '}'
    
    # Look for <url><loc>...</loc></url> tags
    for url_elem in root.findall(f'.//{namespace}url'):
        loc_elem = url_elem.find(f'{namespace}loc')
        if loc_elem is not None and loc_elem.text:
            urls.append(loc_elem.text.strip())
    
    return urls