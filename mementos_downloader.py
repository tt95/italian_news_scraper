import argparse
from datetime import date
import pathlib
import pandas as pd
from wayback import WaybackClient

# PATH FOR SAVING
PATH = "./mementos/"  # contains one wayback link per memento_datetime per newspaper


def check_memento_date(memento_date, url):
    scraping_date = str(memento_date).replace("-", "")
    return scraping_date in url


def create_complete_file(retrieved, site, from_date, to_date):
    df = pd.DataFrame({
        'website': [],
        'memento_datetime': [],
        'homepage_url': [],
        'same_date': [],
    })
    for memento in retrieved:
        if memento.mime_type == "text/html":
            same_date = check_memento_date(memento.timestamp.date(), memento.view_url)
            df = df.append(pd.Series([site,
                                      memento.timestamp.replace(tzinfo=None),
                                      memento.view_url,
                                      "True" if same_date else "False"],
                                     index=df.columns), ignore_index=True)

    newspaper = site.split(".")[0]
    from_to_str = "_from_" + str(from_date) + "_to_" + str(to_date)

    # PRIMA DI SALVARLO ELIMINO EVENTUALI DOPPIONI
    duplicates = df.loc[df.duplicated("memento_datetime"), :]
    df = df.drop(index=duplicates.index.tolist())
    df = df.reset_index(drop=True)

    pathlib.Path(PATH).mkdir(parents=True, exist_ok=True)
    df.to_csv(PATH + "all_" + newspaper + from_to_str + ".csv",
              sep=",", index=False)



    df['date'] = df['memento_datetime'].apply(lambda x: x.date())
    keep_one_per_day(df, newspaper, from_to_str)


def keep_one_per_day(df_complete, newspaper, from_to_str):
    df = df_complete.drop_duplicates(subset=['date'], keep="first")
    df = df.loc[:, ['website', 'memento_datetime', 'homepage_url', 'same_date']]
    df.to_csv(PATH + "days_" + newspaper + from_to_str + ".csv", sep=",", index=False)


class MementosDownloader:
    def __init__(self, newspaper, from_date, to_date):
        self.client = WaybackClient()
        self.from_date = from_date
        self.to_date = to_date
        self.newspaper = newspaper

        self.download()

    def download(self):
        retrieved = self.client.search(url=self.newspaper, matchType="exact", from_date=self.from_date,
                                       to_date=self.to_date,
                                       skip_malformed_results=True, filter_field="!statuscode:(4|5)[0-9][0-9]")  # filter out 4xx and 5xx error status code
        create_complete_file(retrieved, self.newspaper, self.from_date, self.to_date)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--from_date', required=True)
    parser.add_argument('--to_date', required=True)  # last day is excluded
    parser.add_argument('--newspaper', required=True)
    args = parser.parse_args()

    start = args.from_date.split("-")  # %Y-%m-%d
    end = args.to_date.split("-")
    start = [int(x) for x in start]
    end = [int(x) for x in end]

    starting_date = date(start[0], start[1], start[2])
    ending_date = date(end[0], end[1], end[2])
    nwsp = args.newspaper if "." in args.newspaper else args.newspaper + ".it"

    MementosDownloader(newspaper=nwsp, from_date=starting_date, to_date=ending_date)





