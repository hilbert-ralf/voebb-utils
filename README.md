# voebb-wunschliste
Ein alternativer Merkzettel für die öffentlichen Bibliotheken Berlins mit Verfügbarkeitsprüfung an Wunschstandorten.

## Features

* Führen einer Liste von Wunschbibliotheken
* Führen einer Liste von Medien
* Abgleich ob Wunschmedien in Wunschbibliothek aktuell verfügbar sind und Ausgabe dessen auf der Command Line

Beispielhafte Ausgabe:
```commandline
$ python3 main.py 

INFO:root:=== Verfügbarkeiten für Medium 34891699
 - Phantastische Tierwesen - Dumbledores Geheimnisse / Regie: David Yates ; Drehbuch: Joanne K. Rowling, Steve Kloves ; Kamera: George Richmond ; Musik: James Newton Howard ; Schauspieler/in: Mads Mikkelsen, Jude Law, Eddie Redmayne [und andere] :
INFO:root:=== https://www.voebb.de//aDISWeb/app?service=direct/0/Home/$DirectLink&sp=SPROD00&sp=SAK34891699

INFO:root:===
INFO:root:In Bibliothek Mitte: Bibliothek am Luisenbad vorhanden und zu finden bei: Erwachsenenbereich -> TopTitel
INFO:root:In Bibliothek Mitte: Schiller-Bibliothek mit @hugo Jugendmedienetage vorhanden und zu finden bei: Erwachsenenbereich -> TopTitel
INFO:root:==========================================================================================
INFO:root:
INFO:root:=== Verfügbarkeiten für Medium 34908172 - Doctor Strange in the multiverse of madness / Regie: Sam Raimi ; Drehbuch: Michael Waldron ; Kamera: John Mathieson ; Musik: Danny Elfman ; Schauspieler/in: Benedict Cumberbatch, Elizabeth Olsen, Chiwetel Ejiofor [und andere] :
INFO:root:=== https://www.voebb.de//aDISWeb/app?service=direct/0/Home/$DirectLink&sp=SPROD00&sp=SAK34908172
INFO:root:===
INFO:root:In Bibliothek Mitte: Bibliothek am Luisenbad vorhanden und zu finden bei: Erwachsenenbereich -> Spielfilm Doct
INFO:root:In Bibliothek Mitte: Schiller-Bibliothek mit @hugo Jugendmedienetage vorhanden und zu finden bei: Erwachsenenbereich -> TopTitel
INFO:root:==========================================================================================
INFO:root:

```

## HowTo

### Bibliotheksliste pflegen

* standortliste-full.txt mit allen Standorten öffnen
* unerwünschte Einträge löschen
* umbenennen nach standortliste.txt

### Medienliste pflegen

* Medium über die [voebb-Seite](https://www.voebb.de/aDISWeb/app?service=direct/0/Home/$DirectLink&sp=SPROD00) suchen
* Zitierlink ermitteln ![](./doc/voebb-search.png)
* ID des Mediums kopieren ![](./doc/sak-id.png)
* ID zu medienliste.txt hinzufügen. (eine ID pro Zeile erleubt)