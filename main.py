import sys
from utils.process import Process
from modules.tuebl import Tuebl
from modules.itebooks import ItEbooks
from modules.wallhaven import Wallhaven


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
    # Uncomment the sites you do not want to parse
    scrapes = {}
    # scrapes['tuebl'] = Process(Tuebl, './dl_test/tuebl', 100, 5)  # http://tuebl.ca/
    # scrapes['itebooks'] = Process(ItEbooks, './dl_test/itebooks', 100, 5)  # http://it-ebooks.info/
    # scrapes['wallhaven'] = Process(Wallhaven, './dl_test/alphaWallhaven', 100, 5)  # http://alpha.wallhaven.cc/

    # Start parser
    try:
        for site in scrapes:
            print("#### Scrapeing: " + site)
            scrapes[site].start()
    except Exception as e:
        print("Exception [main]: " + str(e))
        stop()