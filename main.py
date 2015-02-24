import sys
from utils.process import Process
from modules.tuebl import Tuebl
from modules.itebooks import ItEbooks


def stop():
    """
    Save any data before exiting
    """
    for site in scrapes:
        print(scrapes[site].log("Exiting..."))
        scrapes[site].stop()
    sys.exit(0)

if __name__ == "__main__":
    # Initialize parser
    # module(
    #   site, (class of the site you want to parse)
    #   dir, (where the data should be saved to)
    #   num of items to parse,(parse n items then stop default=10) set to `0` to parse up to the most recent
    #   threads(default=1)
    # )
    # Comment out the sites you do not want to run
    scrapes = {}
    scrapes['tuebl'] = Process(Tuebl, './dl_test/tuebl', 60, 10)
    scrapes['itebooks'] = Process(ItEbooks, './dl_test/itebooks', 60, 10)

    # Start parser
    try:
        for site in scrapes:
            print("#### Scrapeing: " + site)
            scrapes[site].start()
    except Exception as e:
        print("Exception [main]: " + str(e))
        stop()