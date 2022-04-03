import argparse
import pandas as pd
import trafilatura

PATH = "./news/"

def extract_data(row, directory_name, final_columns):

    file_name = str(row.loc['rank']) + "_" + row.loc['memento_datetime'].strftime("%Y-%m-%d_%H:%M:%S") + ".html"

    fullpath = PATH + directory_name + "/" + file_name

    tmp_diz = {}

    try:
        with open(fullpath, 'r', encoding='utf-8') as f:
            try:
                html_content = f.read()
                tmp_diz = trafilatura.bare_extraction(html_content, output_format='json', favor_precision=True)
                return create_row(row, tmp_diz, final_columns)
            except ValueError as e:
                print("ERRORE LETTURA UTF-8")
                return None
    except FileNotFoundError:
        print(f"FILE {fullpath} NON ESISTE")


def create_row(row, diz, final_columns):
    return pd.Series([row.loc['news_link'],
                      row.loc['memento_datetime'],
                      int(row.loc['rank']),
                      diz['title'],
                      diz['description'],
                      diz['raw-text']],
                     index=final_columns)


def main(input_file):
    df = pd.read_csv(PATH + input_file, sep=",", parse_dates=["memento_datetime"])
    

    from_date = input_file.split("from_")[1].split("_")[0]
    to_date = input_file.split("to_")[1].split(".")[0]
    newspaper = input_file.split("_")[0]
    from_to_string = "from_" + from_date + "_to_" + to_date
    directory_name = input_file.split(".")[0]



    df_out = pd.DataFrame({
        'news_link': [],
        'memento_datetime': [],
        'rank': [],
        'title': [],
        'description': [],
        'text': []
    })


    for idx in df.index:
        row_to_insert = extract_data(row=df.loc[idx, :], directory_name=directory_name, final_columns=df_out.columns)
        if row_to_insert is not None:
            df_out = df_out.append(row_to_insert, ignore_index=True)  ## PASSA IL NOME DEL FILE E BASTA
        else:
            print("RIGA NULLA")

    df_out.to_csv(PATH + "content_"+input_file, sep=",", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    args = parser.parse_args()
    main(input_file=args.file)
