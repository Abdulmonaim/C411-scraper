from bs4 import BeautifulSoup
import re
import os
import json
from functions_util import write_json, read_json
from input_handler import get_valid_num
from typing import Optional, List, Any


async def check_city(session, cty, prov):
    try:
        city_url = f"http://www.ezpostalcodes.com/{prov}/{cty}/A"

        while True:
            response = await fetch(session, city_url, True)

            if not response:
                continue

            soup = BeautifulSoup(response, "html.parser")
            links = soup.find_all("table", string=re.compile("NO RESULTS FOUND!"))
            flag = False

            for i in links:
                if i.text.strip() == "NO RESULTS FOUND!":
                    flag = True

            if flag:
                return True

            return False

    except (AttributeError, TypeError) as e:
        print(f"Error check structure: {e}")
        return []


async def scrape(session, cty, prov):
    try:
        flag = await check_city(session, cty, prov)

        if flag:
            print("NO RESULTS FOUND!")
            return None

        json_file = os.path.join(str(os.getenv("APPDATA")), "CaZipCodes.json")

        if os.path.exists(json_file):
            postal_codes = read_json(json_file)

            if cty in postal_codes:
                part, zipcodes = postal_codes[cty][0], postal_codes[cty][1]
                part, zipcodes_len = part + 1, len(zipcodes)
                num = get_valid_num(zipcodes_len, cty)
                filepath = os.path.join(str(os.getenv("userprofile")), "Downloads", f"{cty} part({part}).xlsx")

                await scrape_leads(session, xfile=filepath, codes=zipcodes[:num])
                del zipcodes[:num]

                if len(zipcodes) == 0:
                    write_json(cty, postal_codes, json_file, modify=False)
                else:
                    write_json(cty, postal_codes, json_file, [part, zipcodes])

            else:
                zipcodes, zipcodes_len = await scrape_zipcodes(session, cty, prov)
                num = get_valid_num(zipcodes_len, cty)
                filepath = os.path.join(str(os.getenv("userprofile")), "Downloads", f"{cty} part(1).xlsx")

                await scrape_leads(session, xfile=filepath, codes=zipcodes[:num])
                del zipcodes[:num]

                if len(zipcodes) == 0:
                    write_json(cty, postal_codes, json_file, modify=False)
                else:
                    write_json(cty, postal_codes, json_file, [1, zipcodes])

        else:
            zipcodes, zipcodes_len = await scrape_zipcodes(session, cty, prov)
            num = get_valid_num(zipcodes_len, cty)
            filepath = os.path.join(str(os.getenv("userprofile")), "Downloads", f"{cty} part(1).xlsx")

            await scrape_leads(session, xfile=filepath, codes=zipcodes[:num])
            del zipcodes[:num]

            if len(zipcodes) != 0:
                data = {cty: [1, zipcodes]}

                with open(json_file, "w") as file:
                    json.dump(data, file)

    except Exception as e:
        print(f"Error with client session: {e}")
