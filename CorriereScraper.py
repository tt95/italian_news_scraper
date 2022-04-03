import os

import pandas as pd
import time
import urllib.request, sys, time
from bs4 import BeautifulSoup
import argparse
import requests
import pandas as pd
import datetime
from datetime import date
from datetime import datetime, timedelta
import pandas as pd

class CorriereScraper():
    def __init__(self, input_path, num_articles):
        self.PATH = input_path
        all_frames = []
        self.num_articles = num_articles

        files_list = os.listdir(self.PATH)

        for f in files_list:
            filename = f.split(".")[0]
            homepage_of_day = self.getHomepageOfDay(f)

            dt_tuple = tuple([int(x) for x in filename[:10].split('-')]) + tuple(
                [int(x) for x in filename[11:].split(':')])
            memento_datetime = datetime(*dt_tuple)

            news_of_day = self.scrapeDay(memento_datetime, homepage_of_day)
            all_frames.append(news_of_day)

        final_frame = pd.concat(all_frames, ignore_index=True)
        final_frame = final_frame.sort_values(by=["memento_datetime", "rank"], ignore_index=True)

        final_frame.to_csv("./news/corriere_news" + from_to_str + ".csv", sep=",", index=False)



    def getHomepageOfDay(self, day_to_scrape):
        day_to_scrape = PATH + "/" + day_to_scrape

        '''try:
            f = open(day_to_scrape, 'rb')
        except OSError:
            print("Could not open/read file:", day_to_scrape)
            sys.exit()'''


        with open(day_to_scrape, 'r') as f:
            soup = BeautifulSoup(f.read(), 'lxml')
        return soup  #todo check else


    def scrapeDay(self, memento_datetime, soup):
        #news = soup.find_all('div', attrs={'class': 'bck-media-news'}, limit=self.num_articles)  # TODO problemi togliendo limite

        news = soup.find_all('div', attrs={'class': "bck-media-news"}, limit=self.num_articles)  # TODO problemi togliendo limite

        # escludi frame o div che hanno class non strettamente uguale a "bck-media-news"
        counter = 0
        for n in news:
            if len(n['class']) > 1:
                counter += 1

        if counter:
            news = soup.find_all('div', attrs={'class': "bck-media-news"}, limit=self.num_articles + counter)

        links = []
        titles = []

        for n in news:
            if len(n['class']) > 1:
                continue

            if n.find('div', attrs={'class': "media-news__content is-paddingless"}):
                link = n.find('div', attrs={'class': "media-content"}).h4.find('a')['href'].strip()
                links.append(link)
                title = n.find('div', attrs={'class': "media-content"}).h4.find('a').text.strip()
                titles.append(title)


            elif n.find('div', attrs={'class': "media-news__content"}):  # FULL SIZE NEWS
                media_news_content = n.find('div', attrs={'class': "media-news__content"})

                if media_news_content.find("a") is None:
                    # SIGNIFICA CHE il bck-media-news è in bck-media-pastiglione oppure è un video
                    link = n.find('div', attrs={'class': "media-news__image"}).find('a')['href'].strip()

                    # il link va pulito altrimenti non va
                    link = link.split("?")[0]
                    title = n.find('div', attrs={'class': "media-news__content"}).find('h4').text.strip()

                else:
                    link = n.find('div', attrs={'class': "media-news__content"}).h4.find('a')['href'].strip()
                    title = n.find('div', attrs={'class': "media-news__content"}).h4.find('a').text.strip()

                links.append(link)
                titles.append(title)

        links = ["http://web.archive.org" + elem if elem.startswith("/web/") else elem for elem in
                 links]

        df = pd.DataFrame({"title": titles, "news_link": links})
        df['memento_datetime'] = memento_datetime
        df['rank'] = [i+1 for i in df.index]
        return df




if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--from_date', required=True)
    parser.add_argument('--to_date', required=True)
    args = parser.parse_args()

    start = args.from_date.split("-")  # %Y-%m-%d
    end = args.to_date.split("-")
    start = [int(x) for x in start]
    end = [int(x) for x in end]

    starting_date = date(start[0], start[1], start[2])
    ending_date = date(end[0], end[1], end[2])
    from_to_str = "_from_" + str(starting_date) + "_to_" + str(ending_date)

    PATH = "./homepages/corriere" + from_to_str

    scraper = CorriereScraper(input_path=PATH, num_articles=5)


