import argparse
import datetime
import os
from datetime import date
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup

CHANGING_LAYOUT_DATE = date(2021, 4, 12)  # On 12 April 2021 ilgiornale launched a new layout

def extract_news_new_layout(soup, div_class, titles, links, limit):
    div = soup.find('div', attrs={'class': div_class})

    tmp_links = div.find_all('a', attrs={'class': "card"}, limit=limit)
    tmp_titles = div.find_all('div', attrs={'class': 'card__title'}, limit=limit)
    for l in tmp_links:
        links.append(l['href'].strip())
    for t in tmp_titles:
        titles.append(t.text.strip('\t'))


class ilGiornaleScraper():
    def __init__(self, input_path, num_articles):
        self.PATH = input_path
        all_frames = []
        self.num_articles = num_articles

        files_list = os.listdir(self.PATH)
        for f in files_list:
            filename = f.split(".")[0]
            homepage_of_day = self.getHomepageOfDay(f)

            dt_tuple = tuple([int(x) for x in filename[:10].split('-')]) + tuple([int(x) for x in filename[11:].split(':')])
            memento_datetime = datetime(*dt_tuple)

            news_of_day = self.scrapeDay(memento_datetime, homepage_of_day)
            all_frames.append(news_of_day)

        final_frame = pd.concat(all_frames, ignore_index=True)
        final_frame = final_frame.sort_values(by=["memento_datetime", "rank"], ignore_index=True)

        final_frame.to_csv("./news/ilgiornale_news" + from_to_str + ".csv", sep=",", index=False)

    def getHomepageOfDay(self, day_to_scrape):
        day_to_scrape = PATH + "/" + day_to_scrape
        with open(day_to_scrape, 'r') as f:
            soup = BeautifulSoup(f.read(), 'lxml')
        return soup  #todo check else


    def scrapeDay(self, memento_datetime, soup):
        links = []
        titles = []
        if memento_datetime.date() > CHANGING_LAYOUT_DATE: # scrape the NEW LAYOUT
            ### NOTIZIA APERTURA
            div_apertura = soup.find('div', attrs={'class': "block-home-opening__main image-overlay"})
            link_apertura = div_apertura.find('a', attrs={'class': 'card'})['href'].strip()
            title_apertura = div_apertura.img['alt'].strip()
            links.append(link_apertura)
            titles.append(title_apertura)

            extract_news_new_layout(soup, "stripe-primo-piano__contents", titles, links, self.num_articles-1)

        else:  # OLD LAYOUT

            ### NOTIZIA APERTURA
            div_apertura = soup.find('div', attrs={'class': "hp_apertura"})
            news_apertura = div_apertura.find('h2', attrs={'class': "entry-title"})
            link_apertura = news_apertura.a['href'].strip()
            title_apertura = news_apertura.a.text.strip()
            links.append(link_apertura)
            titles.append(title_apertura)

            ### UPPER PART LEFT COLUMN
            news_container_top = soup.find('div', attrs={'id': 'block-ilg-elenco-item-home-home-top-1',
                                                         'class': "block block-ilg-elenco-item-home"})
            news = news_container_top.find_all('h2', attrs={'class': "entry-title"}, limit=self.num_articles-1)

            for n in news:
                link = n.a['href'].strip()
                title = n.a.text.strip()
                links.append(link)
                titles.append(title)


        links = ["http://web.archive.org" + elem if elem.startswith("/web/") else elem for elem in
                 links]

        # FIX LINK ESTERNI AL GIORNALE MA RECUPERABILI TOGLIENDO I PARAMETRI
        # i.e http://web.archive.org/web/20210102034956/https://it.insideover.com/religioni/i-cristiani-di-idlib-che-resistono-ai-jihadisti.html?utm_source=ilGiornale&utm_medium=article&utm_campaign=article_redirect
        links = [ l.split("?")[0] if "www.ilgiornale.it" not in l else l for l in links]

        ### CLENING SPECIAL CHARACTERS
        titles = [t.replace("\t", "") for t in titles]
        titles = [t.replace("\n", " ") for t in titles]

        df = pd.DataFrame({"headline": titles, "news_link": links})
        df['memento_datetime'] = memento_datetime
        df['rank'] = [i + 1 for i in df.index]
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

    PATH = "./homepages/ilgiornale" + from_to_str
    scraper = ilGiornaleScraper(input_path=PATH, num_articles=3)


