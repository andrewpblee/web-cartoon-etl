from bs4 import BeautifulSoup
import requests
from datetime import date, timedelta, time, datetime
import pandas as pd
import re


class Dilbert_Crawl():

    def __init__(self, execution_date):
        self.execution_date = execution_date

    def grab_dilbert_comic_image(blob):
    comic = blob.find('img', {'class': 'img-responsive img-comic'})
    comic_src = f'https:{comic["src"]}'
    comic_alt = comic['alt']
    return {
        'src': comic_src,
        'alt': comic_alt
    }

    def grab_dilbert_tags(blob):
        # finds the class with the tags of the comic and returns them as a list
    try:
        tag_wrapper = blob.find('p', {'class': 'small comic-tags'})
        tags = tag_wrapper.findAll('a', {'class': 'link'})
        filtered = list(map(lambda a: a.text[1:], tags))
    except AttributeError:
        filtered = 'empty'
    return filtered

    def scrape_dilbert(execution_date):
        base_url = f"https://dilbert.com/strip/{execution_date}"
        response = requests.get(base_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        comic_features = grab_dilbert_comic_image(soup)
        data = {
            'date': execution_date,
            'comic_src': comic_features['src'],
            'comic_alt': comic_features['alt'],
            'comic_tags': grab_dilbert_tags(soup),
            'transcript': grab_dilbert_transcript(soup, execution_date)
        }
        return data


def strip_alt_text(string):
    try:
        return str(string).split(' - ')[0]
    except:
        return string



def grab_dilbert_transcript(blob, date):
    # finds transcript of the comic and returns the text
    transcript_wrapper = blob.find('div',
                                   {'class': 'js-toggle-container',
                                    'id': f'js-toggle-transcript-{str(date)}'})
    transcript = transcript_wrapper.find('p')
    return transcript.text


def clean_transcript(blob):
    return re.sub('[\r\n]', ' ', blob)


def clean_tags(list):
    if list != 'empty':
        return ', '.join(list)
    else:
        return list

    # should this return a dataframe instead?


def clean_dilbert(dict):
    return {
        'date': str(dict['date']),
        'src': dict['comic_src'],
        'alt': strip_alt_text(dict['comic_alt']),
        'tags': clean_tags(dict['comic_tags']),
        'transcript': clean_transcript(dict['transcript'])
    }


def create_dilbert_df(dict):
    df = pd.DataFrame(
        dict, columns=['date', 'src', 'alt', 'tags', 'transcript'], index=[0])
    return df


def dilbert_etl(execution_date):
    scraped = scrape_dilbert(execution_date)
    cleaned = clean_dilbert(scraped)
    transformed = create_dilbert_df(cleaned)
    return transformed


# df = pd.DataFrame()
# for i in range(3):
#     day = date.today() - timedelta(days=i)
#     got_dilbert = dilbert_etl(day)
#     df = df.append(got_dilbert)
#     print(f'{day} complete')
# df.to_csv('example.csv')

dilbert_list = []

start_date = datetime.strptime('1989-04-16', '%Y-%m-%d').date()
while start_date <= date.today():
    try:
        scrape_the_day = scrape_dilbert(start_date)
        dilbert_list.append(scrape_the_day)
        start_date += timedelta(days=1)
        print(f'{start_date} - complete!')
    except Exception as e:
        raise(e)
