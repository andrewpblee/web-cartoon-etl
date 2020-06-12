from bs4 import BeautifulSoup
import requests
from datetime import date
import pandas as pd
import re


class Dilbert():
    def __init__(self, date):
        self.date = date

    def grab_comic_image(self, blob):
        # Grab the comic image url and the alt text
        comic = blob.find('img', {'class': 'img-responsive img-comic'})
        comic_src = f'https:{comic["src"]}'
        comic_alt = comic['alt']
        return {
            'src': comic_src,
            'alt': comic_alt
        }

    def grab_tags(self, blob):
        # finds the class with the tags of the comic and returns them as a list
        try:
            tag_wrapper = blob.find('p', {'class': 'small comic-tags'})
            tags = tag_wrapper.findAll('a', {'class': 'link'})
            filtered = [*map(lambda a: a.text[1:], tags)]
        except AttributeError:
            filtered = 'empty'
        return filtered

    def grab_transcript(self, blob, date):
        try:
            # finds transcript of the comic and returns the text
            transcript_wrapper = blob.find('div',
                                           {'class': 'js-toggle-container',
                                            'id': f'js-toggle-transcript-{str(date)}'})
            transcript = transcript_wrapper.find('p')
            return transcript.text
        except Exception as e:
            return 'no transcript found'

    def scrape(self):
        # scrape the dilbert with the provided date
        base_url = f"https://dilbert.com/strip/{self.date}"
        try:
            response = requests.get(base_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            comic_features = self.grab_comic_image(soup)
            # return a dict with the src, alt tags and transcript 
            return {
                'date': self.date,
                'comic_src': comic_features['src'],
                'comic_alt': comic_features['alt'],
                'comic_tags': self.grab_tags(soup),
                'transcript': self.grab_transcript(soup, self.date)
            }
        except Exception as e:
            print(e)

    def clean_alt_text(self, string):
        # strip out latter half of the alt text
        try:
            return str(string).split(' - ')[0]
        except:
            return string

    def clean_transcript(self, blob):
        # remove all new line and carriage returns
        return re.sub('[\r\n]', ' ', blob)

    def clean_tags(self, list):
        # joined list back together
        if list != 'empty':
            return ', '.join(list)
        else:
            return list

    def clean(self, dict):
        # bring all cleaning funcs together
        return {
            'date': str(dict['date']),
            'src': dict['comic_src'],
            'alt': self.clean_alt_text(dict['comic_alt']),
            'tags': self.clean_tags(dict['comic_tags']),
            'transcript': self.clean_transcript(dict['transcript'])
        }

    def load(self, dict):
        # return data as a dataframe
        return pd.DataFrame(
            dict, columns=['date', 'src', 'alt', 'tags', 'transcript'], index=[0])
