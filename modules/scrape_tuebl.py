import os
import sys
import signal
import queue
import threading
from bs4 import BeautifulSoup
from scraper import Scraper


class Tuebl(Scraper):
    def __init__(self, base_dir, parse_count=10, threads=1):
        super().__init__()
        self._base_dir = base_dir
        self._progress_file = self._base_dir + "/progress"
        self.log_file = self._base_dir + "/logs"
        self._url_header = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
        self._last_id = 0
        self._max_id = 0
        self._parse_count = parse_count
        self._threads = threads

    def start(self):
        self._max_id = self._get_latest()
        start_val = 1
        # Get start val from progress file if exist
        if os.path.isfile(self._progress_file):
            with open(self._progress_file, 'r') as outfile:
                start_val = int(outfile.read())+1
        print(self.log("##\tStarting at: " + str(start_val)))

        # Find out where to stop
        end_val = start_val + self._parse_count
        if self._parse_count == 0 and self._max_id != 0:
            end_val = self._max_id

        self._q = queue.Queue()
        for i in range(self._threads):
            t = threading.Thread(target=self._thread_setup)
            t.daemon = True
            t.start()

        for item_id in range(start_val, end_val):
            self._q.put(item_id)
        self._q.join()

        self._done()

    def _thread_setup(self):
        while True:
            num = self._q.get()
            print(self.log("Processing book: " + str(num)), end='\r')
            self._parse(num)
            self._q.task_done()

    def _get_latest(self):
        """
        Parse `http://tuebl.ca/browse/new` and get the id of the newest book
        :return: id of the newest item
        """
        print(self.log("##\tGetting newest upload id..."))
        url = "http://tuebl.ca/browse/new"
        # get the html from the url
        html = self.get_html(url, self._url_header)
        if not html:
            return 0
        soup = BeautifulSoup(html)
        max_id = soup.find("h2", {"class": "book-title"}).a['href'].split('/')[-1]
        print(self.log("##\tNewest upload: " + max_id))
        return int(max_id)

    def _parse(self, id_):
        """
        Using BeautifulSoup, parse the page for the wallpaper and its properties
        :param id_: id of the book on `tuebl.ca`
        :return:
        """
        self._last_id = id_
        prop = {}
        prop['id'] = str(id_)

        url = "http://tuebl.ca/books/"+prop['id']
        # get the html from the url
        html = self.get_html(url, self._url_header)
        if not html:
            return 'Skipping...'
        soup = BeautifulSoup(html)

        # Find data
        prop['title'] = soup.find("h2", {"class": "section-title"}).getText().strip()
        if prop['title'] == "Sorry This Book Has Been Removed":
            # If the book has been removed, move on to the next
            self.log("DCMA: " + prop['id'])
            return True

        content = soup.findAll("h3", {"class": "section-title"})
        series = content[0]
        author = content[1]
        if series.contents:
            prop['series_name'] = series.find("a").getText().strip()
            prop['series_id'] = series.a['href'].split('/')[-1]

        # book must have an author
        prop['author_name'] = author.find("a").contents[0].strip()
        prop['author_id'] = author.a['href'].split('/')[-1]

        content = soup.find("div", {"class": "row book-summary"})
        prop['summary'] = content.find("div", {"class": "col-3-4"}).getText().strip()

        book_cover_url = content.find("img", {}).get('src')

        # sanitize data
        prop['author_name'] = self.sanitize(prop['author_name'])
        prop['title'] = self.sanitize(prop['title'])

        # Download images and save
        book_dl_url = "http://tuebl.ca/books/" + prop['id'] + "/download"
        file_ext_book = ".epub"  # assume all books are epubs
        file_ext_cover = self.get_file_ext(book_cover_url)

        file_name = prop['author_name'] + " - " + prop['title']
        first_letter = prop['author_name'][0]

        prop['save_path'] = self._base_dir + "/" + first_letter + "/" + prop['author_name'] + "/" + prop['title'] + "/"
        prop['save_path_cover'] = prop['save_path'] + file_name + file_ext_cover
        prop['save_path'] += file_name + file_ext_book

        if self.download(book_cover_url, prop['save_path_cover'], self._url_header) \
                and self.download(book_dl_url, prop['save_path'], self._url_header):
            self.save_props(prop)

        # Everything was successful
        return True

    def parse_author(self, id_):
        """
        Using BeautifulSoup, parse the page for the tag information
        :param id_: id of the author
        :return:
        """
        # TODO: create list of authors
        pass

    def parse_series(self, id_):
        """
        Using BeautifulSoup, parse the page for the tag information
        :param id_: id of the series
        :return:
        """
        # TODO: create list of series
        pass

    def _done(self):
        """
        Done parsing/downloading, clean up and save progress
        :return:
        """
        print("\n")  # Since we are using `\r` above, we need to enter down when exiting the script
        self.save_progress(self._progress_file, self._last_id)

    def stop(self):
        # not sure what is the last thread to run since it is async, so reparse all current threads on next start
        self._last_id = self._last_id - self._threads
        self._done()
