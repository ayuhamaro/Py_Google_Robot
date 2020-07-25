#!/usr/bin/python
# 用法範例；/path/python robot.py 鋼彈

import os
import sys
import json
import urllib
import requests
from pprint import pprint
from urllib.request import urlopen
from urllib.parse import urlencode


class Robot:
    GOOGLE_API_URI = 'https://www.googleapis.com/customsearch/v1'
    GOOGLE_CX = 'xxx'
    GOOGLE_KEY = 'xxx'
    GOOGLE_DATA_RESTRICT = 'w1'
    MAILGUN_API_URI = 'https://api.mailgun.net/v3/xxx/messages'
    MAILGUN_KEY = 'xxx'
    MAIL_SENDER = 'xxx'
    MAIL_RECIPIENT = 'xxx'
    MAIL_SUB_PREFIX = 'Google Robot - '

    def __init__(self):
        pass

    def __send_mail(self, search_word, send_dict):
        html = ''
        for key, value in send_dict:
            html += '<li><a href="{}">{}</a></li>'.format(value, key)
        html = '<ul>' + html + '</ul>'

        requests.post(
            self.MAILGUN_API_URI,
            auth=("api", self.MAILGUN_KEY),
            data={
                "from": '{} <{}>'.format(self.MAIL_SUB_PREFIX + search_word, self.MAIL_SENDER),
                "to": [self.MAIL_RECIPIENT],
                "subject": self.MAIL_SUB_PREFIX + search_word,
                "html": html,
            },
        )

    def __get_api(self, search_word, start=1):
        data_dict = {}
        query = '{}?cx={}&key={}&dateRestrict={}&start={}&q={}'. \
            format(self.GOOGLE_API_URI, self.GOOGLE_CX,
                   self.GOOGLE_KEY, self.GOOGLE_DATA_RESTRICT, start,
                   urllib.parse.quote(search_word))

        try:
            response = urlopen(query).read().decode('utf-8')
        except HTTPError as e:
            print(e)
        else:
            response_json = json.loads(response)
            for item in response_json.get('items'):
                data_dict[item.get('title')] = item.get('link')

            return data_dict, response_json.get('queries').get('nextPage')

    def search(self):
        if len(sys.argv) == 2:
            data_dict = {}
            search_word = sys.argv[1]
            data_filename = 'q_{}.json'.format(search_word)

            start = 1
            api_has_next = True
            while api_has_next:
                data, next_page = self.__get_api(search_word, start)
                data_dict.update(data)
                start += 10
                if next_page is None:
                    api_has_next = False

            if len(data_dict) > 0:
                if not os.path.isfile(data_filename):
                    with open(data_filename, 'w') as _:
                        _.write('{}')

                file_dict = json.load(open(data_filename))
                dict_diff = data_dict.items() - file_dict.items()
                if len(dict_diff) == 0:
                    print('沒有新資料')
                else:
                    pass
                    json.dump(data_dict, open(data_filename, "w"))
                    self.__send_mail(search_word, dict_diff)


robot = Robot()
robot.search()
