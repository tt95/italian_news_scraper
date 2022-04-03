# italian news scraper 
- Funziona per i siti ansa.it, ilgiornale.it, lastampa.it, repubblica.it
- convenzione date %Y-%m-%d


## Index

- [Uso](#Uso)
  - [Link utili](#link_utili)
- [Problemi](#credits)



## Uso
1. Run mementos_downloader.py
```
python3 mementos_downloader.py --newspaper ansa.it --from_date 2021-01-01 --to_date 2021-01-04

```
in ./mementos vengono creati i file
- all_ansa_from_2021-01-01_to_2021-01-04.csv contenente tutti i mementos (eccetto quelli con status code 4xx o 5xx) per la homepage del sito in quelle date
- days_ansa_from_2021-01-01_to_2021-01-04.csv che riporta solo il primo mementos di ogni giornata (è un filtraggio di all_ansa_from_2021-01-01_to_2021-01-04.csv)
3. Scarica gli html delle homepage ricavate con 
```
python3 Downloader.py --newspaper ansa.it --from_date 2021-01-01 --to_date 2021-01-04 --target homepage
```
in ./homepages/ansa_from_2021-01-01_to_2021-01-04/ vengono salvati gli html scaricati. Il nome segue la convenzione date_time.html
4. Run dello scraper specifico per quel sito:
```
python3 AnsaScraper.py --from_date 2021-01-01 --to_date 2021-01-04
```
in ./news/ viene creato il file ansa_news_from_2021-01-01_to_2021-01-04.csv che contiene i link alle notizie in homepage con relativo rank. Di default sono estratte solo le prime 5 news per homepage, ma è possibile modificare il parametro nel codice di ogni scraper

5. Scarica gli html delle news ricavate con
```
python3 Downloader.py --newspaper ansa.it --from_date 2021-01-01 --to_date 2021-01-04 --target news
```
in ./news/ansa_from_2021-01-01_to_2021-01-04/ vengono salvati gli html scaricati. Il nome segue la convenzione RankPosition_date_time.html

6. Estrai il contenuto di ogni news con
```
python3 extract_content.py --file ansa_news_from_2021-01-01_to_2021-01-04.csv
```
il risultato è salvato in ./news/content_ansa_news_from_2021-01-01_to_2021-01-04.csv  
l'estrazione dei dati è fatta con Trafilatura (https://github.com/adbar/trafilatura)

###  Link Utili
- https://beautiful-soup-4.readthedocs.io/en/latest/index.html?highlight=find_all#
- https://wayback.readthedocs.io/en/stable/usage.html#tutorial
- https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server
- https://trafilatura.readthedocs.io/en/latest/

##  Problemi
- Ansa:
  - problema nello scraping di homepage che si aprono con video/live
- La Stampa
  - per homepage precedenti il 2021-10-29 vengono conteggiate tra le news anche le promozioni per l'abbonamento al giornale stesso
- Repubblica:
  - in blocchi notizia come quello sullo smog nelle città presente qui https://web.archive.org/web/20200115074638/https://www.repubblica.it/ non tutte le news vengono conteggiate
  - per date precedenti al 2020-10-19. Controllare che funzioni come desiderato (attualmente i blocchi di "soft-news","live-news" e "rubriche" vengono saltati)
- IlGiornale
  - lo scraper va modificato per funzionare con un numero maggior di news da estrarre. Attualmente per homepage dopo il 2021-4-12 vengono considerate solo la prima news e quelle nel blocco "primo piano"

- Corriere
  - testato solo su pagine del 2021, non è detto funzioni su altri range temporali se cambia il layout. Nel caso modificare lo scraper


il notebook check_download.ipynb può essere usato per verificare se non sono state scaricate alcune homepage o news. 
In caso i link delle news non siano presenti su internet archive, provare a rimuovere i parametri presenti nel link dal '?' in avanti.

NB: In caso una o più notizie di una homepage in un dato giorno non siano state scaricate, le restati saranno comunque presenti nel file finale. Quindi potrebbero esserci rank con numeri mancanti (coincidenti con i file mancanti)

