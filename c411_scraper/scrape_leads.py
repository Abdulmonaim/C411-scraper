import openpyxl
import os
import asyncio
import random
import aiohttp
from bs4 import BeautifulSoup
from functions_util import fetch
from typing import Optional, List, Any, Tuple


class LeadScraper:
    def __init__(self, session: aiohttp.ClientSession, xfile: Optional[str] = None, file_name: str = ""):
        self.session = session
        self.xfile = xfile
        self.file_name = file_name
        self.wb = openpyxl.Workbook()
        self.ws = self.wb.active
        self.ws.append(["Name", "Phone", "Address"])

    async def scrape_leads(self, codes: Optional[List[str]] = None, multi: bool = True) -> None:
        try:
            # If we are not conducting multi scraping (scraping postal codes before leads),
            # set the output file path to the specified location in the user's Downloads folder.
            # In multi scraping, the file is assumed to be already created, so we reuse the provided file path.
            if not multi:
                self.xfile = os.path.join(str(os.getenv("userprofile")), "Downloads", f"{self.file_name}.xlsx")

            postal_codes = codes or []
            categories_count = len(postal_codes)

            for zipcode_order, zipcode in enumerate(postal_codes, start=1):
                zipcode_url = f"https://www.canada411.ca/search/?stype=pc&pc={zipcode}"
                lead_page = 1

                while True:
                    try:
                        response = await self.fetch_and_process_page(
                            lead_page, zipcode_url, zipcode_order, categories_count
                        )

                        next_page = BeautifulSoup(response, "html.parser").find("li", class_="pagingNext")
                        if not next_page:
                            break

                        next_page_link = next_page.find("a", string="Next")
                        zipcode_url = "https://www.canada411.ca" + next_page_link["href"]
                        lead_page += 1
                        delay = random.randint(5, 10)
                        await asyncio.sleep(delay)

                    except Exception as e:
                        print(f"Error processing data for postal code {zipcode_order}) {zipcode}: {e}")

        except Exception as e:
            print(f"Error in scrape_leads: {e}")
        finally:
            self.wb.close()

    async def fetch_and_process_page(self, lead_page: int, url: str, zipcode_order: int, categories_count: int) -> Any:
        try:
            response: Any = await fetch(self.session, url)
            if not response:
                return

            names, phones, addresses, flag = await get_leads(response)

            if not names:
                print(
                    f"postal code {zipcode_order} of {categories_count}: We didn't find any result for {url.split('=')[-1]}"
                )
                return

            leads_count = len(names)
            for lead_order, (name, phone, address) in enumerate(zip(names, phones, addresses), start=1):
                print(
                    f"lead {lead_order} of {leads_count} of page {lead_page}, "
                    f"postal code {zipcode_order} of {categories_count}: {name}, {phone}, {address}"
                )
                await parse(wb, [name, phone, address], xfile)
                lead_order += 1 if flag else 0

            return response

        except Exception as e:
            print(f"Error processing data for page {lead_page}) {name}: {e}")

        finally:
            self.wb.close()

    async def get_leads(self, response: str) -> Tuple[List[str], List[str], List[str], bool]:
        try:
            soup = BeautifulSoup(response, "html.parser")
            names = soup.find_all("h2", class_="c411ListedName")

            if not names:
                if soup.find("h1", class_="vcard__name") is None:
                    return [], [], [], False

                names.append(soup.find("h1", class_="vcard__name").text)
                phone = [soup.find("span", class_="vcard__label").text]
                address = [soup.find("div", class_="c411Address vcard__address").text]

                return names, phone, address, False
            else:
                phones = soup.find_all("span", class_="c411Phone")
                addresses = soup.find_all("span", class_="adr")
                titles, tele, adds = [], [], []

                for i in range(len(names)):
                    titles.append(names[i].find("a").text)
                    tele.append(phones[i].text)
                    adds.append(addresses[i].text)

                return titles, tele, adds, True

        except (AttributeError, TypeError) as e:
            print(f"Error parsing lead links: {e}")
            return [], [], [], False

    async def parse(self, row: List[Any], xfile: Optional[str]) -> None:
        try:
            self.ws = self.wb.active
            self.ws.append(row)
            self.wb.save(xfile)

        except AttributeError as e:
            print(f"Error parsing response: {e}")
        except TypeError as e:
            print(f"Error parsing response: {e}")
        except Exception as e:
            print(f"Error in parse function: {e}")
