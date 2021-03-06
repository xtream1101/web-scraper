from bs4 import BeautifulSoup
from utils.scraper import Scraper


class Tuebl(Scraper):
    def __init__(self, base_dir, url_header, log_file):
        super().__init__(log_file)
        self._base_dir = base_dir
        self._url_header = url_header

    def get_latest(self):
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

    def parse(self, id_):
        """
        Using BeautifulSoup, parse the page for the wallpaper and its properties
        :param id_: id of the book on `tuebl.ca`
        :return:
        """
        prop = {}
        prop['id'] = str(id_)

        url = "http://tuebl.ca/books/" + prop['id']
        # get the html from the url
        html = self.get_html(url, self._url_header)
        if not html:
            return False
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
