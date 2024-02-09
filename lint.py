from subprocess import run


def main():
    # Run Flake8
    run(["poetry", "run", "flake8", "c411_scraper"])

    # Run Mypy
    run(["poetry", "run", "mypy", "c411_scraper"])


if __name__ == "__main__":
    main()
