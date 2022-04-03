import argparse
import pathlib
import sys
import time
from datetime import date
import pandas as pd
import requests

MEMENTOS_PATH = "./mementos/"  # contains one wayback link per memento_datetime per newspaper
HOMEPAGES_PATH = "./homepages/"  # contains raw html of homepage of newspapers per memento_datetime
NEWS_PATH = "./news/"


def download_homepages(newspaper, from_to_str):
    df = pd.read_csv(MEMENTOS_PATH + "days_" + newspaper + from_to_str + ".csv", sep=",")
    urls = df.homepage_url.tolist()
    datetimes = df.memento_datetime.tolist()
    datetimes = [d.replace(" ", "_") for d in datetimes]

    for i in range(len(urls)):
        try:
            html_page_content = requests.get(urls[i], timeout=10).text
        except Exception as e:
            error_type, error_obj, error_info = sys.exc_info()
            print('ERROR FOR LINK:', urls[i])
            print(error_type, 'Line:', error_info.tb_lineno)
            continue  # ignore this page

        file_name = datetimes[i]

        pathlib.Path(HOMEPAGES_PATH + newspaper + from_to_str).mkdir(parents=True, exist_ok=True)
        with open(HOMEPAGES_PATH + newspaper + from_to_str + "/" + file_name + ".html", 'w', encoding='utf-8') as f:
            f.write(html_page_content)


def download_news(newspaper, from_to_str):
    file_to_read = NEWS_PATH + newspaper + "_news" + from_to_str

    df = pd.read_csv(file_to_read+".csv", sep=",")
    urls = df['news_link'].tolist()
    date = df['memento_datetime'].tolist()
    rank = df['rank'].tolist()

    for i in range(len(urls)):
        try:
            html_page_content = requests.get(urls[i], timeout=10).text
        except Exception as e:
            error_type, error_obj, error_info = sys.exc_info()
            print('ERROR FOR LINK:', urls[i])
            print(error_type, 'Line:', error_info.tb_lineno)
            continue  # ignore this page

        file_name = str(rank[i]) + "_" + date[i].replace(" ","_") + ".html"

        pathlib.Path(NEWS_PATH + newspaper + "_news"+from_to_str).mkdir(parents=True, exist_ok=True)
        with open(NEWS_PATH + newspaper + "_news"+from_to_str + "/" + file_name, 'w', encoding='utf-8') as f:
            f.write(html_page_content)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--newspaper', required=True)
    parser.add_argument('--target', required=True)   # homepage or news
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

    nwsp = args.newspaper.split(".")[0] if "." in args.newspaper else args.newspaper

    start_time = time.time()
    if args.target == "homepage":
        download_homepages(nwsp, from_to_str)
    elif args.target == "news":
        download_news(nwsp, from_to_str)
    else:
        print("target must be 'homepage' or 'news' ") #todo use argparse instead of print

    print("--- %s seconds ---" % (time.time() - start_time))
