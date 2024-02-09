import requests


def get_valid_province() -> str:
    while True:
        prov = input("Enter a province name: ").strip()
        url = f"http://www.ezpostalcodes.com/{prov}"
        res = requests.get(url).status_code
        if res == 200:
            return prov
        else:
            print(
                f"\nEnter the city name as it appears in the URL.\n"
                f"If it's not working, manually check the URL to see if the page is still accessible.\n'{url}'\n"
            )


def get_valid_city_name() -> tuple:
    while True:
        prov = get_valid_province().strip().upper()
        cit = input("Enter a city name: ").strip().upper()
        url = f"http://www.ezpostalcodes.com/{prov}/{cit}/A"
        res = requests.get(url).status_code
        if res == 200:
            return cit, prov
        else:
            print(
                f"\nEnter the city name as it appears in the URL.\n"
                f"If it's not working, manually check the URL to see if the page is still accessible.\n'{url}'\n"
            )


def get_valid_num(list_len: int, cty: int) -> int:
    while True:
        try:
            print(f"There are {list_len} postal codes in {cty} city.")
            num = int(input(f"Select a quantity of postal codes to scrape, ranging from 1 to {list_len}: "))
            if 0 < num <= list_len:
                break
            else:
                print(f"!!! The number you have selected is outside the range of 1 to {list_len} !!!\n\n")
        except ValueError:
            print("!!! Invalid input. Please enter an integer number !!!\n\n")

    return num


def dir_postalcodes() -> tuple:
    input_string = input("\nEnter a comma-separated list of postal codes or a single postal code:\n")
    print("\n")
    filename = input_string
    input_list = input_string.split(",")
    input_list = [value.strip() for value in input_list]
    if len(input_list) > 5:
        filename = input("Select a name for your file: ")
    return input_list, filename
