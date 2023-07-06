import configparser
import logging
import smtplib
import ssl
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas
import requests
from tabulate import tabulate

# initialize config
config = configparser.ConfigParser()
config.read('config.ini')

# initialize logging
logging.basicConfig(level=logging.getLevelName(config['DEFAULT']['LoggingLevel']),
                    format='%(asctime)s - %(levelname)s - %(message)s')


def main(path_mediums_list):
    mediums = open(path_mediums_list, 'r').readlines()
    libraries = open('standortliste.txt', 'r').readlines()

    logging.info(
        "Verfügbarkeit von {} Medien wird in {} Bibliotheken geprüft ...".format(len(mediums), len(libraries)))

    # removing newlines
    for library in libraries:
        libraries[libraries.index(library)] = library.replace('\n', '')

    # removing newlines
    for medium in mediums:
        mediums[mediums.index(medium)] = medium.replace('\n', '')

    available_results = []
    tmp_non_available_results = []
    non_available_results = []

    for medium in mediums:

        logging.info("Prüfe Medium {}".format(medium))

        sak_id = medium.split(",")[0]

        url = 'https://www.voebb.de//aDISWeb/app?service=direct/0/Home/$DirectLink&sp=SPROD00&sp=SAK{}'.format(sak_id)

        response = requests.get(url)
        logging.debug('response code from {}: {}'.format(url, response))

        # todo add check if response code is 200

        if len(pandas.read_html(response.text)) < 2:
            logging.warning("Tabelle mit verfügbarkeiten nicht gefunden. Medium '{}' wird übersprungen".format(medium))
            continue

        big_table = pandas.read_html(response.text)[1]

        if not (
                "Bibliothek" in big_table.columns and "Standort" in big_table.columns and "Verfügbarkeit" in big_table.columns):
            logging.warning("Tabelle mit verfügbarkeiten nicht gefunden. Medium {} wird übersprungen".format(medium))
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
                logging.debug("columns found: {}".format(library_entry.columns))
                if "Verfügbar" in library_entry['Verfügbarkeit'].values:
                    location = library + ' -> ' + library_entry['Standort'].values[0]
                    if 'Signatur' in library_entry.columns:
                        location += ' -> ' + library_entry['Signatur'].values[0]

                    logging.debug("In Bibliothek {} vorhanden und zu finden bei: {}".format(library, str(location)))
                    available_results.append([medium, location, title, url])
                else:
                    logging.debug("In Bibliothek {} vorhanden aber nicht verügbar".format(library))
                    tmp_non_available_results.append([medium, library_entry['Verfügbarkeit'].values[0], title, url])
            else:
                logging.debug("Bibliothek {} hat dieses Medium nicht.".format(library))

        if found_in_libraries_count == 0:
            non_available_results.append([medium, title, url])

    if len(non_available_results) > 0:
        logging.warning("Folgende Medien sind in keiner der gewählten Bibliotheken vorhanden:")
        logging.info(generate_non_available_table(non_available_results, 'grid'))

    logging.info('Folgende Medien sind aktuell verfügbar:\n' + generate_medium_table(available_results, 'grid', "ORT"))
    logging.info('\n\n\n')
    logging.info(
        'Folgende Medien sind gelistet aber verliehen:\n' + generate_medium_table(tmp_non_available_results, 'grid',
                                                                                  "Fälligkeit"))

    if 'Mailing' in config:
        logging.info("Mailversand ist aktiviert und wird vorbereitet")
        send_result_via_mail(available_results, tmp_non_available_results, non_available_results)
    else:
        logging.debug("Mailversand nicht konfiguriert")


def send_result_via_mail(available_results, tmp_non_available_results, non_available_results):
    non_available_table_html = None
    non_available_table_plain = None
    if len(non_available_results) > 0:
        non_available_table_html = generate_non_available_table(non_available_results, 'html')
        non_available_table_plain = generate_non_available_table(non_available_results, 'grid')
    style = """
    table, th, td {
      border: 1px solid;
      padding: 10px;
      text-align: left;
    }
    
    table {
      border-collapse: collapse;
    }
    tr:nth-child(even) {background-color: #f2f2f2;}
    """
    mail_content_html = """
    <html>
      <head>
        <style>
        {}
        </style>
      </head>
      <body>
        Folgende Medien sind aktuell verfügbar:
        {}
        
        Folgende Medien sind gelistet aber verliehen:
        {}
    
        Folgende Medien sind in keiner der gewählten Bibliotheken vorhanden:
        {}
      </body>
    </html>
    """.format(style,
               generate_medium_table(available_results, 'html', "ORT"),
               generate_medium_table(tmp_non_available_results, 'html', "Fälligkeit"),
               non_available_table_html)
    mail_content_plain = """
    Folgende Medien sind aktuell verfügbar:
    {}
    
    Folgende Medien sind gelistet aber verliehen:
    {}

    Folgende Medien sind in keiner der gewählten Bibliotheken vorhanden:
    {}
    """.format(generate_medium_table(available_results, 'grid', "ORT"),
               generate_medium_table(tmp_non_available_results, 'grid', "Fälligkeit"),
               non_available_table_plain)

    sender_email = config['Mailing']['User']
    password = config['Mailing']['Password']
    # Create a secure SSL context
    context = ssl.create_default_context()
    with smtplib.SMTP(config['Mailing']['SmtpServerAddress'], int(config['Mailing']['SmtpServerPort'])) as server:
        server.starttls(context=context)
        server.login(sender_email, password)

        recipient_mails = config['Mailing']['Recipients'].split(',')

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Neuigkeiten von deiner voebb-wunschliste"
        msg['From'] = sender_email

        part1 = MIMEText(mail_content_plain, 'plain')
        part2 = MIMEText(mail_content_html, 'html')
        msg.attach(part1)
        msg.attach(part2)

        server.sendmail(sender_email, recipient_mails, msg.as_string())
        logging.info("Mail erfolgreich versand an {}".format(recipient_mails))


def generate_non_available_table(non_available_results, type):
    non_available_table = tabulate(non_available_results,
                                   headers=["ID", "TITEL", "DIREKTLINK"],
                                   tablefmt=type,
                                   maxcolwidths=[None, 35, None])
    return non_available_table


def generate_medium_table(available_results, type, availability):
    available_table = tabulate(available_results,
                               headers=["ID", availability, "TITEL", "DIREKTLINK"],
                               tablefmt=type,
                               maxcolwidths=[None, 35, 35, None])
    return available_table


if __name__ == '__main__':
    file_path = "medienliste.txt"
    # sys.argv[0] is set by thew name of the script itself
    if len(sys.argv) == 2:
        file_path = sys.argv[1]

    main(file_path)
