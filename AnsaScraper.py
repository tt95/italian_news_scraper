import os

import pandas as pd
import time
import urllib.request, sys, time
from bs4 import BeautifulSoup
import argparse
import sys
import pathlib
import requests
import pandas as pd
import datetime
from datetime import date
from datetime import datetime, timedelta
import pandas as pd


NEWS_PATH ="./news/"

class AnsaScraper():
    def __init__(self, input_path, num_articles):
        self.PATH = input_path
        all_frames = []
        self.num_articles = num_articles

        files_list = os.listdir(self.PATH)
        for f in files_list:
            filename = f.split(".")[0]
            homepage_of_day = self.getHomepageOfDay(f)
            news_of_day = self.scrapeDay(filename.replace("_"," "), homepage_of_day)
            all_frames.append(news_of_day)

        final_frame = pd.concat(all_frames, ignore_index=True)
        final_frame = final_frame.sort_values(by=["memento_datetime", "rank"], ignore_index=True)

        pathlib.Path(NEWS_PATH).mkdir(parents=True, exist_ok=True)
        final_frame.to_csv(NEWS_PATH + "ansa_news" + from_to_str + ".csv", sep=",", index=False)



    def getHomepageOfDay(self, day_to_scrape):
        day_to_scrape = PATH + "/" + day_to_scrape
        with open(day_to_scrape, 'r') as f:
            soup = BeautifulSoup(f.read(), 'lxml')
        return soup  #todo check else


    def scrapeDay(self, memento_datetime, soup):
        links = []
        titles = []

        # ARTICOLO IN PRIMO PIANO
        #todo problema se c'è live al posto dell'immagine:
        can_read_initial_block = soup.find('div', attrs={'class': "pp-img"})
        if can_read_initial_block is None:  #TODO FARE QUESTO CHECK PER TUTTI I SITI
            return pd.DataFrame()

        link = soup.find('div', attrs={'class': "pp-img"}).find('a')['href'].strip()
        primo_piano_link = "https://web.archive.org" + link
        primo_piano_title = soup.find('article', attrs={'class': "big"}).header.get_text()

        links.append(primo_piano_link)
        titles.append(primo_piano_title)

        # TUTTI GLI ALTRI ARTICOLI
        news = soup.find_all('h3', attrs={'class': "news-title area-primopiano"}, limit=self.num_articles-1)

        for n in news:
            link = n.a['href'].strip()
            title = n.a.text.strip()
            links.append(link)
            titles.append(title)


        links = ["http://web.archive.org" + elem if elem.startswith("/web/") else elem for elem in
                 links]

        df = pd.DataFrame({"headline": titles, "news_link": links})
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


    PATH = "./homepages/ansa" + from_to_str

    scraper = AnsaScraper(input_path=PATH, num_articles=5)


