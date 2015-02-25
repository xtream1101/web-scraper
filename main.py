import os
import sys
import argparse
import configparser
from utils.process import Process
# They are imported as all lowercase
#   so it is case insensitive in the config file
from modules.tuebl import Tuebl as tuebl
from modules.itebooks import ItEbooks as itebooks
from modules.wallhaven import Wallhaven as wallhaven


parser = argparse.ArgumentParser()
parser.add_argument('config', help='custom config file', nargs='?', default='./config.ini')
args = parser.parse_args()

config = configparser.ConfigParser()


def stop():
    """
    Save any data before exiting
    """
    for site in scrape:
        print(scrape[site].log("Exiting..."))
        scrape[site].stop()
    sys.exit(0)

if __name__ == "__main__":
    # Read config file
    if not os.path.isfile(args.config):
        print("Invalid config file")
        sys.exit(0)
    config.read(args.config)

    # Parse config file
    scrape = {}
    for site in config.sections():
        if config[site]['enabled'].lower() == 'true':
            try:  # If it not a class skip it
                site_class = getattr(sys.modules[__name__], site.lower())
            except AttributeError as e:
                print("\nThere is no module named " + site + "\n")
                continue
            dl_path = os.path.expanduser(config[site]['download_path'])
            num_files = int(config[site]['number_of_files'])
            threads = int(config[site]['threads'])
            scrape[site] = Process(site_class, dl_path, num_files, threads)

    # Start site parser
    try:
        for site in scrape:
            print("#### Scrapeing: " + site)
            scrape[site].start()
    except Exception as e:
        print("Exception [main]: " + str(e))
        stop()