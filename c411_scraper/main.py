import os
import timeit
import asyncio
import aiohttp
import random
from c411_scraper.functions_util import write_json, read_json
from input_handler import get_valid_city_name, dir_postalcodes
from scraping_core import scrape, scrape_leads


async def reset_specific_city(jsonfile: str) -> None:
    city_name = input("Enter the name of the city whose postal codes you want to delete: ").upper()
    confirm = input(
        f"Confirm whether you would like to reset ({city_name}) city by pressing 'y' for " f"yes or 'n' for no: "
    ).lower()
    if confirm == "y":
        file_data = read_json(jsonfile)
        write_json(city_name, file_data, jsonfile, modify=False)


async def reset_all_cities(jsonfile: str) -> None:
    confirm = input(
        "Confirm whether you would like to reset all cities by pressing 'y' for yes or 'n' " "for no: "
    ).lower()
    if confirm == "y" and os.path.exists(jsonfile):
        os.remove(jsonfile)


async def main() -> None:
    try:
        mode = input("(1. Scrape by city    2. Scrape by postal code    3. reset): ")
        start = timeit.default_timer()
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=random.randint(25, 50))) as session:
            jsonfile = os.path.join(str(os.getenv("APPDATA")), "CaZipCodes.json")

            if mode == "1":
                city, province = get_valid_city_name()
                await scrape(session, city, province)
            elif mode == "2":
                postalcodes, file_name = dir_postalcodes()
                await scrape_leads(session, f_name=file_name, codes=postalcodes, multi=False)
            elif mode == "3":
                mode1 = input("(1. reset a specific city    2. reset all cities): ")
                if mode1 == "1":
                    await reset_specific_city(jsonfile)
                elif mode1 == "2":
                    await reset_all_cities(jsonfile)

        end = timeit.default_timer()
        exe_time = end - start
        hours = exe_time // 3600
        minutes = (exe_time % 3600) // 60
        seconds = (exe_time % 3600) % 60
        print(
            f"\nThe elapsed time of scraping data for this process:\n"
            f"{hours} hours, {minutes} minutes, {round(seconds, 2)} seconds.\n"
        )

    except Exception as e:
        print(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
