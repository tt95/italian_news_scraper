import argparse
import datetime
import os
from datetime import date
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup

CHANGING_LAYOUT_DATE = date(2021, 10, 29)  # On 12 April 2021 ilgiornale launched a new layout

def extract_news(soup, num_news):
    colonne = soup.find_all('div',attrs={'class':'block__item'})
    articles = []
    
    titles = []
    links = []

    for c in colonne:
        art = c.find_all('article',attrs={'class':'entry default'})
        art = [(int(a['data-sindex']) , a) for a in art]
        articles.extend(art)

    
    for idx,art in articles:
        titles.insert(idx-1,art.find('h2',attrs={'class':'entry__title'}).find('a').text.strip())
        links.insert(idx-1, art.find('a')['href'].strip())
    
    return titles, links



class laStampaScraper():
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

        final_frame.to_csv("./news/lastampa_news" + from_to_str + ".csv", sep=",", index=False)



    def getHomepageOfDay(self, day_to_scrape):
        day_to_scrape = PATH + "/" + day_to_scrape
        with open(day_to_scrape, 'r') as f:
            soup = BeautifulSoup(f.read(), 'lxml')
        return soup  #todo check else


    def scrapeDay(self, memento_datetime, soup):
        links = []
        titles = []
        if memento_datetime.date() >= CHANGING_LAYOUT_DATE: # scrape the NEW LAYOUT

            gd_columns = soup.find('main',attrs={'id':'homeContent', 'role':'main'}).find_all('div', attrs={'class':'gd-column-12'})

            index = 0
            for i in range(len(gd_columns)):
                if gd_columns[i].find('section') is not None:
                    index = i
                    break


            sections = gd_columns[i].find_all("section")
                    
            for g in sections:
                
                if g['data-zona'].strip() in ["Standard 5","Standard","Standard 3", "bbc", "Extra"]: # TODO EXTEND IF NECESSARY
                    content = g
                    num_news = int(len(content.find_all('article')))
                
                    titles_tmp, links_tmp = extract_news(content, num_news)
                    titles.extend(titles_tmp)
                    links.extend(links_tmp)


                if len(links) > self.num_articles:
                    links = links[:self.num_articles]
                    titles = titles[:self.num_articles]
                    break


        else:  # OLD LAYOUT
            
            main=soup.find('main',attrs={'class':'main__content', 'role':'main'})

            sections = main.find_all('section',attrs={'class':'ls-section'})

            ls_main = []
            for s in sections:
                main = s.find('div',attrs={'class':'ls-main'})
                if main is not None:
                    ls_main.append(main)
                else:
                    row = s.find('div',attrs={'class':'ls-row'})
                    ls_main.append(row)


            articles = []
            for s in ls_main:
                bs = s.find_all('article')
                articles.extend(bs)
                if len(articles) > self.num_articles:
                    articles = articles[:self.num_articles]
                    break
                
            for art in articles:
                titles.append(art.find('h2',attrs={'class':'entry__title'}).find('a').text.strip())
                links.append(art.find('a')['href'].strip())


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

    PATH = "./homepages/lastampa" + from_to_str
    scraper = laStampaScraper(input_path=PATH, num_articles=5)


