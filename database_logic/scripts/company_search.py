import asyncio
from playwright.async_api import async_playwright


async def search_companies(query):
    uri  = f"https://www.allabolag.se/what/{query}"
    