import logging

import pandas
import requests
from tabulate import tabulate


def main():
    logging.basicConfig(level=logging.INFO)

    f = open('medienliste.txt', 'r')
    mediums = f.readlines()

    f = open('standortliste.txt', 'r')
    libraries = f.readlines()

    logging.info(
        "Verfügbarkeit von {} Medien wird in {} Bibliotheken geprüft".format(len(mediums), len(libraries)))

    # removing newlines
    for library in libraries:
        libraries[libraries.index(library)] = library.replace('\n', '')

    # removing newlines
    for medium in mediums:
        mediums[mediums.index(medium)] = medium.replace('\n', '')

    available_results = []
    non_available_results = []

    for medium in mediums:

        logging.info(medium)

        # url = 'https://www.voebb.de//aDISWeb/app?service=direct/0/Home/$DirectLink&sp=SPROD00&sp=SAK34841213'
        # 'https://www.voebb.de//aDISWeb/app?service=direct/0/Home/$DirectLink&sp=SPROD00&sp=SAK34896410'
        url = 'https://www.voebb.de//aDISWeb/app?service=direct/0/Home/$DirectLink&sp=SPROD00&sp=SAK{}'.format(medium)

        response = requests.get(url)
        logging.debug('responsecode from {}: {}'.format(url, response))

        # todo add check if response code is 200

        if len(pandas.read_html(response.text)) < 2:
            logging.warning("Tabelle mit verfügbarkeiten nicht gefunden.")
            continue

        big_table = pandas.read_html(response.text)[1]

        if not (
                "Bibliothek" in big_table.columns and "Standort" in big_table.columns and "Verfügbarkeit" in big_table.columns):
            logging.warning("Tabelle mit verfügbarkeiten nicht gefunden.")
            continue

        logging.debug("Tabelle mit verfügbarkeiten gefunden:")
        logging.debug(big_table)

        title = medium
        for array in pandas.read_html(response.text)[0].values:
            if array[0] == 'Titel':
                title = array[1]

        logging.debug("=== Verfügbarkeiten für Medium {} :".format(title))
        logging.debug("=== " + url)
        logging.debug("===")

        found_in_libraries_count = 0

        for library in libraries:
            if library in big_table['Bibliothek'].values:
                found_in_libraries_count += 1
                library_entry = big_table.loc[big_table['Bibliothek'] == library]
                if "Verfügbar" in library_entry['Verfügbarkeit'].values:
                    location = library + ' -> ' + library_entry['Standort'].values[0] + ' -> ' + library_entry['Signatur'].values[0]
                    logging.debug("In Bibliothek {} vorhanden und zu finden bei: {}".format(library, str(location)))
                    available_results.append([medium, location, title, url])
                else:
                    logging.debug("In Bibliothek {} vorhanden aber nicht verügbar".format(library))
            else:
                logging.debug("Bibliothek {} hat dieses Medium nicht.".format(library))

        if found_in_libraries_count == 0:
            non_available_results.append([medium, title, url])

    logging.warning("Folgende Medien sind aktuell verfügbar:")
    logging.info(tabulate(available_results,
                          headers=["ID", "ORT", "TITEL", "DIREKTLINK"],
                          tablefmt="grid",
                          maxcolwidths=[None, 35, 35, None]))

    if len(non_available_results) > 0:
        logging.warning("Folgende Medien sind in keiner der gewählten Bibliotheken vorhanden:")
        logging.info(tabulate(non_available_results,
                              headers=["ID", "TITEL", "DIREKTLINK"],
                              tablefmt="grid",
                              maxcolwidths=[None, 35, None]))

if __name__ == '__main__':
    main()
