import argparse
import datetime
import os
from datetime import date
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup

CHANGING_LAYOUT_DATE = date(2020,10,19)


def drop_section_with_class(sections, drop_class):
    to_remove = []
    for i in range(len(sections)):
        class_attr = " ".join(sections[i]['class'])
        for dc in drop_class:
            if dc in class_attr:
                to_remove.append(i)
    
    to_remove.sort(reverse = True)
    return to_remove


def extract_news(soup):
    colonne = soup.find_all('div', attrs={'class': 'block__item'})
    articles = []

    titles = []
    links = []

    for c in colonne:
        art = c.find_all('article', attrs={'class': 'entry'})
        art = [(int(a['data-sindex']), a) for a in art]
        articles.extend(art)

    for idx, art in articles:
        titles.insert(idx - 1, art.find('h2', attrs={'class': 'entry__title'}).find('a').text.strip())
        links.insert(idx - 1, art.find('a')['href'].strip())

    return titles, links




class RepubblicaScraper():
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

        final_frame.to_csv("./news/repubblica_news" + from_to_str + ".csv", sep=",", index=False)



    def getHomepageOfDay(self, day_to_scrape):
        day_to_scrape = PATH + "/" + day_to_scrape
        with open(day_to_scrape, 'r') as f:
            soup = BeautifulSoup(f.read(), 'lxml')
        return soup  #todo check else


    def scrapeDay(self, memento_datetime, soup):
        links = []
        titles = []

        if memento_datetime.date() >= CHANGING_LAYOUT_DATE: # scrape the NEW LAYOUT
            main = soup.find('main').find("div", attrs={'class': "gd-column-12"})
            sections = main.find_all("section", limit=15)  # limito alle prime 15 sezioni e poi tengo solo quelle da "primo piano" in avanti

            for s in sections:
                content = s
                titles_tmp, links_tmp = extract_news(content)
                titles.extend(titles_tmp)
                links.extend(links_tmp)

                if len(links) > self.num_articles:
                    links = links[: self.num_articles]
                    titles = titles[: self.num_articles]
                    break

        else: # OLD LAYOUT

            main = soup.find("div", attrs={'class':'rep-container'}).find("div",attrs={'class':"column-12 zone first-page-top"})
            sections = main.find_all("section",limit=15)  #limito alle prime 15 sezioni e poi filtro quelle che non servono

            if len(sections) == 1: # layout con striscia iniziale e poi sotto la pagina è divisa in due colonne
                main = soup.find("div", attrs={'class':'rep-container'}).find("div",attrs={'class':"column-8 zone first-page-left"})
                sections = main.find_all("section",limit=15)  


            drop_class = ["soft-news","rubrica","live-news"] # rimuove striscia iniziale rep-tv (soft-news) e rubriche
            to_remove = drop_section_with_class(sections, drop_class)
            for idx in to_remove:
                del sections[idx]


            articles = []
            for s in sections:
                art = s.find_all("article")
                articles.extend(art)
                if len(articles) > self.num_articles:
                    articles = articles[:self.num_articles]
                    break

            for art in articles:
                h2 = art.find("h2",attrs={'class':"entry-title"})
                link = h2.a['href'].strip()
                title = h2.a.text.strip()
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

    PATH = "./homepages/repubblica" + from_to_str

    scraper = RepubblicaScraper(input_path=PATH, num_articles=5)


