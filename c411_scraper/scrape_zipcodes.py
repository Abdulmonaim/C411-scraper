import asyncio
import random
from bs4 import BeautifulSoup
import re
from typing import Optional, List, Any


async def get_streets(response):
    try:
        soup = BeautifulSoup(response, "html.parser")
        streets = soup.find_all("a", attrs={"href": re.compile("^street")})
        postal_codes = []
        for street in streets:
            postal_codes.append(street["href"])
        return postal_codes
    except (AttributeError, TypeError) as e:
        print(f"Error parsing streets: {e}")
        return []


async def get_zipcodes(response, street):
    try:
        soup = BeautifulSoup(response, "html.parser")
        links_list = soup.find_all("a", attrs={"href": re.compile(f"-{street}-")})
        zip_codes = set()
        for link in links_list:
            code = link.find("b").text
            zip_codes.add(code)
        zip_codes_list = list(zip_codes)
        return zip_codes_list
    except (AttributeError, TypeError) as e:
        print(f"Error parsing zip_codes: {e}")
        return []


async def check_structure(session, cty, prov):
    try:
        city_url = f"http://www.ezpostalcodes.com/{prov}/{cty}/A"
        while True:
            response = await fetch(session, city_url, True)
            if not response:
                continue

            soup = BeautifulSoup(response, "html.parser")
            link = soup.find("a", attrs={"title": f"A {prov} Cities"})
            if link is None:
                return False
            return True
    except (AttributeError, TypeError) as e:
        print(f"Error check structure: {e}")
        return []


async def scrape_zipcodes(session, cty, prov):
    flag = await check_structure(session, cty, prov)
    if flag:
        alphabets = [
            "9",
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
        ]
    else:
        alphabets = ["A"]

    print(f"Collecting all the postal codes of {cty} city ........\n")
    streets_links, zip_codes = [], set()
    for char in alphabets:
        if char == "9":
            print("Getting streets names start with 1-9")
        else:
            if not flag:
                print("Getting streets names")
            else:
                print(f"Getting streets names start with {char}")
        city_url = f"http://www.ezpostalcodes.com/{prov}/{cty}/{char}"
        streets = None
        while True:
            response0 = await fetch(session, city_url, True)
            if not response0:
                continue
            streets = await get_streets(response0)
            break
        streets_links.extend(streets)
        delay = random.randint(2, 3)
        await asyncio.sleep(delay)

    print("_________________________________________________________________________________\n")
    for link in streets_links:
        st = link.split("/")[3]
        print(f"Getting postal codes of {st} street")
        street_url = "http://www.ezpostalcodes.com/" + link
        codes = None
        while True:
            response0 = await fetch(session, street_url, True)
            if not response0:
                continue
            codes = await get_zipcodes(response0, st)
            break
        zip_codes.update(codes)
        delay = random.randint(3, 4)
        await asyncio.sleep(delay)

    zip_codes_list = list(zip_codes)
    print("_________________________________________________________________________________\n")
    return zip_codes_list, len(zip_codes_list)
