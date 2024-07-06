import asyncio
from playwright.async_api import async_playwright

async def check_company_existence(org_number):
    org = org_number.replace("-", "")
    uri = f"https://www.allabolag.se/{org}"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(uri)

        # Check for 404 error
        if "404" in await page.title():
            await browser.close()
            return None

        # Extract company name from dataLayer
        try:
            company_info_script = """
                (function() {
                    const companyInfo = window.dataLayer.find(layer => layer.companyInfo);
                    return companyInfo ? companyInfo.companyInfo.companyName : null;
                })();
            """
            company_name = await page.evaluate(company_info_script)
        except Exception as e:
            print(f"Error evaluating script: {e}")
            await browser.close()
            return None
        
        await browser.close()
        if company_name:
            return company_name.replace(" ", "-").lower()
        else:
            return None
"""
if __name__ == "__main__":
    org_nummer = "556421-0309"  # Example organization number
    company_name = asyncio.run(check_company_existence(org_nummer))
    if company_name:
        print(f"Company exists: {company_name}")
    else:
        print("Company does not exist")
"""