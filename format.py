from subprocess import run


def main():
    run(["poetry", "run", "black", "c411_scraper"])


if __name__ == "__main__":
    main()
