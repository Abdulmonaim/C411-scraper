import json
import asyncio
import random
import aiohttp
from fake_useragent import UserAgent
from typing import Optional, Dict


def write_json(cty: str, postal_codes: Dict, jpath: str, zipcodes: Optional[list] = None, modify: bool = True) -> None:
    if modify:
        postal_codes.update({cty: zipcodes})
    else:
        del postal_codes[cty]
    with open(jpath, "w") as file:
        json.dump(postal_codes, file)


def read_json(jpath: str) -> Dict:
    with open(jpath) as f:
        data: Dict = json.load(f)
    return data


async def fetch(session: aiohttp.ClientSession, url: str, old: Optional[bool] = False) -> Optional[str]:
    """
    Fetches content from the specified URL using an asynchronous HTTP GET request.

    Parameters:
    - session (aiohttp.ClientSession): The aiohttp client session.
    - url (str): The URL to fetch.
    - old (Optional[bool]): If True, use a predefined user agent; otherwise, use a random user agent.

    Returns:
    - Optional[str]: The content fetched from the URL, or None if an error occurs.
    """
    try:
        USER_AGENTS_OLD = [
            "Mozilla/5.0 (X11; Linux x86_64) " "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "CriOS/114.0.5735.99 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 10) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.5735.57 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.5735.57 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 10; LM-Q720) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.5735.57 Mobile Safari/537.36",
        ]

        HEADERS = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.ca/",
            "User-Agent": random.choice(USER_AGENTS_OLD) if old else UserAgent().random,
        }

        async with asyncio.timeout(15):
            async with session.get(url, headers=HEADERS) as response:
                return await response.text()

    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        print(f"Error fetching {url}: {e}")
        return None
