import requests
import pandas
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    f = open('medienliste.txt', 'r')
    mediums = f.readlines()

    f = open('standortliste.txt', 'r')
    libraries = f.readlines()

    logging.info("Verfügbarkeit von {} Medien wird in {} Bibliotheken werden geprüft".format(len(mediums), len(libraries)))

    # removing newlines
    for library in libraries:
        libraries[libraries.index(library)] = library.replace('\n','')

    for medium in mediums:

        #url = 'https://www.voebb.de//aDISWeb/app?service=direct/0/Home/$DirectLink&sp=SPROD00&sp=SAK34841213'
        #'https://www.voebb.de//aDISWeb/app?service=direct/0/Home/$DirectLink&sp=SPROD00&sp=SAK34896410'
        url = 'https://www.voebb.de//aDISWeb/app?service=direct/0/Home/$DirectLink&sp=SPROD00&sp=SAK{}'.format(medium)

        response = requests.get(url)
        logging.debug('responsecode from {}: {}'.format(url, response))

        #todo add check if response code is 200

        if len(pandas.read_html(response.text)) < 2:
            logging.warning("Tabelle mit verfügbarkeiten nicht gefunden.")
            continue

        big_table = pandas.read_html(response.text)[1]

        if not ("Bibliothek" in big_table.columns and "Standort" in big_table.columns and "Verfügbarkeit" in big_table.columns):
            logging.warning("Tabelle mit verfügbarkeiten nicht gefunden.")
            continue

        logging.debug("Tabelle mit verfügbarkeiten gefunden:")
        logging.debug(big_table)


        title = medium
        for array in pandas.read_html(response.text)[0].values:
            if array[0] == 'Titel':
                title += " - " + array[1]


        logging.info("=== Verfügbarkeiten für Medium {} :".format(title))
        logging.info("=== " + url)
        logging.info("===")

        for library in libraries:
            if library in big_table['Bibliothek'].values:
                library_entry = big_table.loc[big_table['Bibliothek'] == library]
                if "Verfügbar" in library_entry['Verfügbarkeit'].values:
                    location = library_entry['Standort'].values[0] + ' -> ' + library_entry['Signatur'].values[0]
                    logging.info("In Bibliothek {} vorhanden und zu finden bei: {}".format(library, str(location)))
                else:
                    logging.debug("In Bibliothek {} vorhanden aber nicht verügbar".format(library))
            else:
                logging.debug("Bibliothek {} hat dieses Medium nicht.".format(library))

        logging.info("==========================================================================================")
        logging.info("")


    #todo maybe send mail
