from bs4 import BeautifulSoup
from utils.scraper import Scraper
import re


class Wallhaven(Scraper):
    def __init__(self, base_dir, url_header, log_file):
        super().__init__(log_file)
        self._base_dir = base_dir
        self._url_header = url_header

    def get_latest(self):
        """
        Parse `http://alpha.wallhaven.cc/latest` and get the id of the newest book
        :return: id of the newest item
        """
        print(self.log("##\tGetting newest upload id..."))
        url = "http://alpha.wallhaven.cc/latest"
        # get the html from the url
        html = self.get_html(url, self._url_header)
        if not html:
            return 0
        soup = BeautifulSoup(html)
        max_id = soup.find("section", {"class": "thumb-listing-page"}).find("li").a['href'].split('/')[-1]
        print(self.log("##\tNewest upload: " + max_id))
        return int(max_id)

    def parse(self, id_):
        """
        Using BeautifulSoup, parse the page for the wallpaper and its properties
        :param id_: id of the book on `http://alpha.wallhaven.cc/wallpaper/`
        :return:
        """
        prop = {}
        prop['id'] = str(id_)

        url = "http://alpha.wallhaven.cc/wallpaper/" + prop['id']
        # get the html from the url
        html = self.get_html(url, self._url_header)
        if not html:
            return False
        soup = BeautifulSoup(html)

        # Find all sidebar data
        sidebar = soup.find("aside", {"id": "showcase-sidebar"})

        #####
        # Get colors
        #####
        prop['colors'] = []
        wp_colors = sidebar.find("ul", {"class": "color-palette"})
        for li in wp_colors.find_all("li"):
            prop['colors'].append(li['style'].split(':')[1])

        #####
        # Get tags
        #####
        prop['tags'] = []
        wp_tags = sidebar.find("ul", {"id": "tags"})
        for li in wp_tags.find_all('li'):
            tag = {}
            tag['purity'] = li.get("class", [])[1]
            tag['id'] = li['data-tag-id']
            tag['name'] = li.find("a", {"class": "tagname"}).getText().strip()
            prop['tags'].append(tag)

        #####
        # Get purity
        #####
        prop['purity'] = sidebar.find("fieldset", {"class": "framed"}).find("label").getText()

        #####
        # Get properties
        #####
        wp_prop = sidebar.find("dl")
        for dt in wp_prop.findAll('dt'):
            prop_name = dt.getText().strip()
            dd = dt.findNext("dd")
            if prop_name == 'Favorites':
                prop_value = dd.getText().strip()
            elif prop_name == 'Uploaded by':
                prop_value = dd.find(attrs={"class": "username"}).getText().strip()
            elif prop_name == "Added":
                prop_value = dd.find("time").get("datetime")
            else:
                prop_value = dd.getText().strip()

            prop[prop_name] = prop_value

        #####
        # Get image
        #####
        img_src = "http:" + soup.find("img", {"id": "wallpaper"}).get('src')

        #####
        # Download images
        #####
        file_ext = self.get_file_ext(img_src)
        file_name = "alphaWallhaven-" + prop['id']
        prop['save_path'], prop['hash'] = self.create_save_path(self._base_dir, file_name)
        prop['save_path'] += file_name + file_ext
        if self.download(img_src, prop['save_path'], self._url_header):
            self.save_props(prop)

        # Everything was successful
        return True







#     def _get_latest(self):
#         """
#         Parse `http://alpha.wallhaven.cc/latest` and get the id of the newest image
#         :return:
#         """
#         print("Getting latest upload id...")
#         url = "http://alpha.wallhaven.cc/latest"
#         # get the html from the url
#         html = self.get_html(url, self._url_header)
#         if not html:
#             return 0
#         soup = BeautifulSoup(html)
#         max_id = soup.find("section", {"class": "thumb-listing-page"}).find("li").a['href'].split('/')[-1]
#         print("Newest upload:"+max_id)
#         return int(max_id)
#
#     def _parse_wp(self, id_):
#         """
#         Using BeautifulSoup, parse the page for the wallpaper and its properties
#         :param id_: id of the wallpaper on `wallhaven.cc`
#         :return:
#         """
#         prop = {}
#         prop['id'] = str(id_)
#
#         print(prop['id']+"\tGetting HTML...")
#         url = "http://alpha.wallhaven.cc/wallpaper/"+prop['id']
#         # get the html from the url
#         html = self.get_html(url, self._url_header)
#         if not html:
#             return 'Skipping...'
#         soup = BeautifulSoup(html)
#         print(prop['id']+"\tStart parsing data...")
#
#         # Find all sidebar data
#         sidebar = soup.find("div", {"class": "sidebar-content"})
#
#         #####
#         # Get colors
#         #####
#         prop['colors'] = []
#         wp_colors = sidebar.find("ul", {"class": "color-palette"})
#         for li in wp_colors.find_all("li"):
#             prop['colors'].append(li['style'].split(':')[1])
#
#         #####
#         # Get tags
#         #####
#         prop['tags'] = []
#         wp_tags = sidebar.find("ul", {"id": "tags"})
#         for li in wp_tags.find_all('li'):
#             tag = {}
#             tag['purity'] = li.get("class", [])[1]
#             tag['id'] = li['data-tag-id']
#             tag['name'] = li.find("a", {"class": "tagname"}).contents[0].strip()
#             prop['tags'].append(tag)
#
#         #####
#         # Get purity
#         #####
#         wp_purity = sidebar.find("fieldset", {"class": "framed"}).find("input", {"checked": "checked"}).get("value")
#         prop['purity'] = wp_purity
#
#         #####
#         # Get properties
#         #####
#         wp_prop = sidebar.find("dl", {"id": "wallpaper-info"})
#         for dt in wp_prop.find_all('dt', text=False):
#             prop_name = dt.contents[0].strip()
#             dd = dt.findNext("dd")
#             if prop_name == 'Favorites':
#                 try:    prop_value = dd.find("a").contents[0].strip()
#                 except: prop_value = dd.contents[0].strip()
#             elif prop_name == 'Uploaded by':
#                 prop_value = dd.find(attrs={"class": "username"}).contents[0].strip()
#             elif prop_name == "Added":
#                 prop_value = dd.find("time").get("datetime")
#             else:
#                 prop_value = dd.contents[0].strip()
#
#             prop[prop_name] = prop_value
#
#         #####
#         # Get image
#         #####
#         img_src = soup.find("img", {"id": "wallpaper"}).get('src')
#
#         #####
#         # Download images
#         #####
#         file_ext = self.get_file_ext(img_src)
#         file_name = "wallhaven-"+prop['id']
#         prop['save_path'], prop['hash'] = self.create_save_path(self._base_dir, file_name)
#         prop['save_path'] += file_name+file_ext
#         if self.download(img_src, prop['save_path'], self._url_header):
#             self.save_props(prop)
#
#         #####
#         # Everything was successful
#         #####
#         self._last_id = int(prop['id'])
#         return True
#
#     def parse_tag(self, id_):
#         """
#         Using BeautifulSoup, parse the page for the tag information
#         :param id_: id of the tag on `wallhaven.cc`
#         :return:
#         """
#         # TODO: create list of tags
#         pass