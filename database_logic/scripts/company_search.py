import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import json

async def search_companies(query: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Set to False for debugging
        page = await browser.new_page()
        
        await page.goto(f"https://www.merinfo.se/search?q={query}&l=")
        
        # Handle privacy consent popup
        try:
            consent_button = page.locator('button:has-text("GODKÄNN")')
            await consent_button.click(timeout=5000)
            print("Privacy consent accepted.")
        except Exception as e:
            print(f"Privacy consent handling error: {e}")
        
        # Wait for and click toggles
        await page.wait_for_selector('.toggle-options', state='visible', timeout=10000)
        toggles = await page.query_selector_all('.vue-js-switch')
        for toggle in toggles[:2]:
            try:
                await toggle.click(force=True, timeout=5000)
                await page.wait_for_load_state('networkidle')
            except Exception as e:
                print(f"Failed to click toggle: {e}")
        
        # Click the "Visa" (Show) button to apply filters
        try:
            show_button = page.locator('button:has-text("Visa")')
            await show_button.click(timeout=5000)
            await page.wait_for_load_state('networkidle')
            print("Filters applied.")
        except Exception as e:
            print(f"Failed to apply filters: {e}")
        
        companies = []
        page_num = 1
        
        while True:
            await page.wait_for_selector('.result-list', state='visible', timeout=10000)
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            results = soup.find_all('div', class_='result-list')
            
            for result in results:
                company_divs = result.find_all('div', recursive=False)
                for company_div in company_divs:
                    company = {}
                    
                    # Name
                    name_elem = company_div.find('h2')
                    if name_elem:
                        company['name'] = name_elem.text.strip()
                    
                    # Org number
                    org_number_elem = company_div.find('p', class_='mi-flex mi-justify-start')
                    if org_number_elem:
                        company['org_number'] = org_number_elem.text.strip()
                    
                    # Address and Postal locality
                    address_elem = company_div.find('address')
                    if address_elem:
                        address_parts = address_elem.find_all('span')
                        if len(address_parts) >= 2:
                            company['address'] = address_parts[0].text.strip()
                            company['postal_locality'] = address_parts[1].text.strip()
                    
                    # Registration status
                    status_elem = company_div.find('p', class_='mi-mb-3')
                    if status_elem:
                        company['status'] = status_elem.text.strip()
                    
                    # Phone number
                    phone_elem = company_div.find('a', class_='button md:button-lg button-primary-nd mi-font-semibold !mi-text-base')
                    if phone_elem:
                        company['phone'] = phone_elem.text.strip()
                    
                    # Additional information
                    info_div = company_div.find('div', class_='mi-w-full mi-flex mi-flex-wrap')
                    if info_div:
                        info_items = info_div.find_all('div', class_='mi-w-1/2 md:mi-w-auto mi-text-left')
                        for item in info_items:
                            key = item.text.split(':')[0].strip()
                            value = item.find('b').text.strip() if item.find('b') else ''
                            if key == 'Reg.år':
                                company['registration_year'] = value
                            elif key == 'Ant.anst':
                                company['employees'] = value
                            elif key == 'F-Skatt':
                                company['f_tax'] = value
                            elif key == 'Momsreg':
                                company['vat_registered'] = value
                    
                    companies.append(company)
                    
                    if limit and len(companies) >= limit:
                        break
                
                if limit and len(companies) >= limit:
                    break
            
            if limit and len(companies) >= limit:
                break
            
            # Check if there's a next page
            next_page = soup.find('a', class_='next')
            if not next_page:
                break
            
            # Go to the next page
            page_num += 1
            await page.goto(f"https://www.merinfo.se/search?q={query}&l=&page={page_num}")
        
        await browser.close()
        
        print(f"Found {len(companies)} companies.")
        return companies[:limit] if limit else companies

async def main():
    query = "Telenor"  # Example search query
    limit = 30  # Set to None to get all companies
    companies = await search_companies(query, limit)
    
    for company in companies:
        print(json.dumps(company, indent=4))

if __name__ == "__main__":
    asyncio.run(main())