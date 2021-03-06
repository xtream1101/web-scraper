import os
import urllib.request
import urllib.error
import json
import hashlib


class Scraper:
    def __init__(self, log_file):
        self._errors = {}
        # Set default log path
        self.log_file = log_file

    def download(self, url, file_path, header={}):
        self.log("Starting download: " + url)
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        try:
            with urllib.request.urlopen(
                urllib.request.Request(url, headers=header)) as response, \
                    open(file_path, 'wb') as out_file:
                        data = response.read()
                        out_file.write(data)
        except urllib.error.HTTPError as e:
            # Something went wrong, abort
            self.error(e.code, url)
            self.log("Error [download]: " + str(e.code) + " " + url)
        # TODO: Check if dl was successful
        return True

    def get_file_ext(self, url):
        file_name, file_extension = os.path.splitext(url)
        return file_extension

    def create_save_path(self, base_path, name):
        """
        Create a directory structure using the hashed filename
        :return: string of the path to save to not including filename/ext
        """
        name_hash = hashlib.md5(name.encode('utf-8')).hexdigest()
        if base_path.endswith('/') or base_path.endswith('\\'):
            save_path = base_path
        else:
            save_path = base_path + "/"
        depth = 2  # will have depth of n dirs (MAX of 16 because length of md5 hash)
        for i in range(1, depth+1):
            end = i*2
            start = end-2
            save_path += name_hash[start:end] + "/"
        return save_path, name_hash

    def get_html(self, url, header={}):
        html = False
        request = urllib.request.Request(url, headers=header)
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            # Something went wrong, abort
            self.error(e.code, url)
            self.log("Error [get_html]: " + str(e.code) + " " + url)
        else:
            try:
                html = response.read().decode('utf-8')
            except UnicodeDecodeError as e:
                self.log("Error [get_html][UnicodeDecodeError]:" + str(e) + " " + url )
        return html

    def sanitize(self, string):
        """
        Catch and replace and invalid path chars
        """
        replace_chars = [
            ['\\', '-'], [':', '-'], ['/', '-'],
            ['?', ''], ['<', '>'], ['`', '`'],
            ['|', '-'], ['*', '`'], ['"', '\'']
        ]
        for ch in replace_chars:
            string = string.replace(ch[0], ch[1])
        return string

    def save_props(self, data):
        self.log("Saving metadata: " + data['id'])
        data['save_path'] = data['save_path']
        with open(data['save_path'] + ".json", 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4)

    def error(self, error, data):
        """
        Save error to self._errors dict
        :param error: Error name
        :param data: Command/value that caused the error
        :return:
        """
        if error not in self._errors.keys():
            self._errors[error] = []
        self._errors[error].append(data)

    def save_errors(self, file):
        """
        Save errors into json file for review
        :return:
        """
        if self._errors:
            if not os.path.exists(os.path.dirname(file)):
                os.makedirs(os.path.dirname(file))
            with open(file + ".json", 'a') as errorfile:
                json.dump(self._errors, errorfile, sort_keys=True, indent=4)

    def log(self, data):
        if not os.path.exists(os.path.dirname(self.log_file)):
            os.makedirs(os.path.dirname(self.log_file))
        with open(self.log_file, 'a') as log_file:
            log_file.write(str(data) + "\n")

        return str(data)

    def save_progress(self, file, count):
        """
        Save the last id checked
        :return:
        """
        if not os.path.exists(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file))
        with open(file, 'w') as outfile:
            if count < 0:
                count = 0
            outfile.write(str(count))