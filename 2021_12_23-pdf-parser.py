# -*- coding: utf-8 -*-

# Bibliotheken importieren
import os
import tika
from tika import parser
import PyPDF2
from PyPDF2 import PdfFileReader
import pandas as pd


from urllib import request

# PDF-Datei von Webadresse in Variable URL speichern
#url = "https://www.nature.com/articles/s42004-021-00582-3.pdf"
url = "https://www.nature.com/articles/s41598-018-37132-2.pdf"

# PDF-Datei von lokalem Speicherplatz in Variable paper speichern
paper = "paper-02.pdf"

# Überprüfen, ob eine Datei in der Variablen paper vorhanden ist. Wenn nicht, variable "Papper" lehr ist, Datei von URL abrufen und in paper speicher 
if not os.path.isfile(paper):
     request.urlretrieve(url, paper)

# Extrahieren des Dateiinhaltes und in der Variablen parsed abspeichern
parsed = tika.parser.from_file(paper)


# druckbaren Zeichenfolge der pdf-Datei in die Variable Text speichern
import string
text = ''.join(filter(lambda x:x in string.printable, parsed["content"]))


def finde_mailadressen(text):
    '''
    Die Funktion findet sämtliche EMailadressen im Text und gibt sie in einer Liste zurück.
    Es werden zwei weitere Listen zurückgegeben in denen die Verwendeten Nutzernamen und die Domainen enthalten sind.

    '''
    # Leere Liste initialisieren
    adressen = []
    
    # Bibliothek für REs importieren
    import re
    
    # Alle gfundenen Übereinstimmungen in Liste: "matches" abspeichern
    matches = re.findall(r'([\w.-]+@[\w.-]+)', text)
    
    # die Liste matches wird durchsucht, die Leerzeichen, Tabs etc. werden entfernt und die Liste mit Links wird gefüllt
    # jeder Link jeweil einmal
    for eintrag in matches:
        #eintrag = eintrag.strip()
        if eintrag in adressen:
            continue
        else:
            adressen.append(eintrag)
    
    # Adresse aufteilen in Liste mit Nutzernamen und Liste mit Domain
    nutzername = []
    domain = []
    
    for eintrag in adressen:
        at = eintrag.find('@')
        if eintrag[:at] not in nutzername:
            nutzername.append(eintrag[:at])
        if eintrag[at+1:] not in domain:
            domain.append(eintrag[at+1:])
    
    return adressen, nutzername, domain

#adressen,nutzername, domain=finde_mailadressen(text)

def finde_links(text):
    '''
    Die Funktion findet sämtliche Links in dem Text und gibt sie in einer Liste zurück.
    
    '''
    # Leere Liste initialisieren
    links = []
    
    # Bibliothek für REs importieren
    import re
    
    # Alle gfundenen Übereinstimmungen in Liste: "matches" abspeichern
    matches = re.findall(r"(?:http[s]?:\S\S+)|\s(?:www\S+)", text)
    
    # die Liste matches wird durchsucht, die Leerzeichen, Tabs etc. werden entfernt und die Liste mit Links wird gefüllt
    # jeder Link jeweil einmal
    for eintrag in matches:
        eintrag = eintrag.strip()
        if eintrag in links:
            continue
        else:
            links.append(eintrag)
    
    return links

#links=finde_links(text)

def chemische_elemente(text):
    '''
    Die Funktion findet sämtliche Chemischen Elemente in dem Text.
    Es kann entweder eine Tabelle mit den Chemischen Elementen und deren Chemischen Eigeschaften wiedergegeben werden 
    oder ein Balkendiagramm mit Angabe der Häufigkeit.    
    
    '''
    
    # Bibliothek für Reguläre Ausdrücke importieren. 
    import re

    def artikel_loeschen(text):
        ''' Die Artiekl werden aus dem Text gelöscht, weil sie oft fälschlicherweise als 
            chemische Elemente erkannt werden      

        '''
        meta = parsed["metadata"]
        if meta['language'] == 'EN':
            text = re.sub('[Tt]he','',text)
        elif meta['language'] == 'DE':
            text = re.sub('[Dd](er|ie|as)','',text)
        elif meta['language'] == 'FR':
            text = re.sub('[Ll](e|a)','',text)

        return text
    
    text = artikel_loeschen(text)
    
    # Alle gfundenen Übereinstimmungen in Liste: "matches" abspeichern
    #matches = re.findall(r"[A-Z][a-z]?\d*|\((?:[^()]*(?:\(.*\))?[^()]*)+\)\d+", parsed["content"])
    # matches = re.findall(r"\b[A-Z][a-z]?\d*|\([^)]+\)\d*\b", parsed["content"])
    #matches = re.findall(r"\s[0-9]*[0-9]*(?:[A-Z][a-z]?)[^a-z]|\s[0-9]*[0-9]*[A-Z][a-z]?[0-9]*(?:[A-Z][a-z]*)",text)
    matches = re.findall(r"\s[0-9]*[0-9]*(?:[A-Z][a-z]?)[^a-z]",text)
    
    #matches = re.findall(r"\b[A-Z][a-z]?\d*|\([^)]+\)\d*\b", text)
    print(matches)
    
    # Bibliothek für Eigenschaften chemischer Elemente importieren    
    from chempy.util import periodic 

    # Periodensystem nach Ordnungszahl in Tuple: "perodicttabele" abspeichern    
    periodictable = periodic.symbols
        
    def sortieren_dict(woerterbuch):
        ''' Die einträge eines Dictionarys werden nach Häufigkeit sortiert. 
            Das Dictionary wird in eine Liste mit enthaltenen Tuplen umgewandelt. In den Tupeln sind zwei Einträge enthalten.
            Der erste Eintag des Tupels enthält die Elementhäufigkeit und der zweite Eintrag das Periodensymbol.
        '''
        
        # Initialisieren einer Liste, weil diese sortierbar ist. In dieser Liste werden die einträge des Dictionarys als Tuple gespeichert
        l = list()
        for key, val in woerterbuch.items():
            l.append((val, key))
    
        # Sortieren der Liste von Tupeln in Absteigender Reihenfolge.
        l.sort(reverse = True)
        
        return l

    def tabelle(lst):    
        ''' Die einträge einer sortierten Liste werden als Tabelle ausgegeben. 
        
        '''
        
        #colums = ['frequency','Atomic No.','Name','Mass']
        index =[]
        colums = ['frequency']
        
        
        # Spalten initialisieren
        frequency = []
        atomic_no = []
        name = []
        mass = []
        
        
        # In der Schleife werden die vorbereiteten Spalten sowie der Index für das DataFrame gefüllt
        for eintrag in lst:
            
            nr = 0
            
            #Es wird das Periodensystem durchschlaufen um die Positon des Eintrags in der Variablen: nr abzuspeichern
            for i in range(len(periodictable)):
                if periodictable[i] == eintrag[1]:
                    nr = i
            
            # der zugehörige Eintrag wird mit den Eigenschaften der Bibliothek chempy.util gefüllt
            index.append(periodic.symbols[nr])
            
            frequency.append(eintrag[0])
            atomic_no.append(nr)
            name.append(periodic.names[nr])
            mass.append(periodic.relative_atomic_masses[nr])
            
            df = pd.DataFrame(frequency, index, colums)
       
        # dem Dataframe werden die erzeugten Listen als weitere Zeilen hinzugefügt
        df['Atomic No.']=atomic_no
        df['Name']=name
        df['Mass']=mass
            
        
        # Ausgabe der Ergebnisse
        print(df.head(10))
        #print(df['Atomic No.'])
        #print(df.loc[['C','Na']])
        
    def balkendiagramm(lst,number):    
        ''' Die häufigsten Einträge einer Liste werden als Balkendiagramm dargestellt.
            Die gewünschte Anzahl der Einträge kann in der Variable number mitgegeben werden        
        '''
    
        # matplotlib für grafische Darstellung importieren
        import matplotlib.pyplot as plt


        # Fenstergröße festlegen: Breite, Höhe
        plt.figure(figsize=(30,5)) 

        x = range(number)
        
        # Liste von Y-Werten mit der Anzahl der Einträgen erzeugen
        y = []
        for i in range(number):
            y.append(lst[i][0])
        
        # Liste von Punkten auf der X-Achse mit den Einträgen der Liste erzeugen
        x_ticks = []
        for i in range(number):
            x_ticks.append(lst[i][1])

        plt.bar(x, y, align='center')
        plt.xticks(x, x_ticks, rotation=0, fontsize=18)
        plt.show()
        # Ergebnisbild speichern
        # plt.savefig('balkendiagramm.png')        
    
    # Initialisierung eines Dictionarys zum Abspeichern der Chemischen Elemente und ihrer Häufigkeit    
    formulars =  {}

    # Initialisierung einer Liste für eine Träge, die nicht zu den chemischen Elementen gehören (Häufigkeit uninteressant, deshlab Liste anstatt dictionary)
    nonformulars = []

    # Schleife durchsucht die Liste: "matches" nach regulären Ausdrücken für einen Grußbuchstaben gefolgt von einem Kleinbuchstaben und speichert sie in die Liste: "elems"
    for m in matches:
        elems = re.findall(r"[A-Z][a-z]?", m)
       
        # Schleife durchläuft die Liste elems. Wenn die Einträge nicht im Periodensystem enthalten sind, werden die Ausdrücke in der Variablen nonformulars abgespeichert, 
        # die boolsche Varible: test auf "False" gesetzt und der Schleifendurchgang abgebrochen
        test = True
        for e in elems:
            if e not in periodictable:
                nonformulars.append(m)
                test = False
                break
        # Wenn die boolsche Variable "Test" noch auf "True" steht, ist der gefundende Ausdruck im Periodensystem enthalten und wird in dem Dictionary Formulars abgespeichert.
        if test:                         
            if e in formulars:
                formulars[e] += 1
            else:
                formulars[e] = 1
        
    #print(pd.Series(formulars))
    #print(pd.Series(nonformulars))

    # Aufruf der Funktionen
    elemente = sortieren_dict(formulars)
    #tabelle(elemente)
    balkendiagramm(elemente,10)
    
    return formulars

#x = chemische_elemente(text)

def chemische_formeln(text):
    '''
    Die Funktion findet sämtliche Chemischen Formel in dem Text.
    Es wird eine Tabelle mit den Chemischen Eigeschaften wiedergegeben.
    
    '''
    # Bibliothek für REs importieren
    import re
    
    from chempy.util import periodic
    from chempy import Substance
    
    # Alle gfundenen Übereinstimmungen in Liste: "matches" abspeichern
    matches = re.findall(r"([0-9]*[A-Z][a-z]{0,1}[0-9]*[A-Z]*[a-z]*[0-9]*)", text)
    #matches = re.findall(r"[0-9]*[A-Z][a-z]{0,1}[A-Z]*[a-z]*[0-9]*", text)
    
    chem_for = []
    
    for element in matches:
        if len(element) > 2 and element[1].islower() and element[2].islower():
            continue
        elif len(element) > 2 and element.isupper():
            continue
        elif len(element) == 1 or element[:2] =='Mc':
            continue
        elif len(element) <= 2:
            continue
        elif element in chem_for:
            continue
        else:
            chem_for.append(element)
    
    for formel in chem_for:
        try:
            analyse = Substance.from_formula(formel)
            print(formel, end = '-->')
            print(analyse.unicode_name, end = "\t")
            print(analyse.latex_name, end = "\t")
            print(analyse.html_name, end = "\t")
            print('%.3f' % analyse.mass)
        
        except:
            continue

    return chem_for    

#x=chemische_formeln(text)

def wort_haeufigkeiten(text):
    ''' 
    Die funktion findet sämtliche Worte indem Text und gibt die 10 häufigsten Wörter aus. 
    Stopword wie z.B. A, In, and, the etc. werden rausgefiltet.
    Sonderzeichne werden rausgefiltet.
    
    '''    
    import re

    worte1 = re.findall('([A-ZÄÖÜ]?[a-zäöü][a-zäöü]+)',text)

    d_worte = {} # Dictionary initialisieren
    
    # Dictionary füllen
    for wort in worte1:
        d_worte[wort] = d_worte.get(wort,0) + 1

    # Ermittlung der Häugigsten Wörter 
    l = list()
    for key, val in d_worte.items():
        l.append((val, key))

    # Abspeichern der gefundenen Wörter in einer Liste von Tupeln, nach häufigkeit sortieren
    l.sort(reverse = True)

    x_data = []
    y_data = []

    print("Auflistung der 10 häufigsten Worte: ")
    for i in range(10):
        print(f'Das Wort: "{l[i][1]}" wurde {l[i][0]} mal im Text gefunden.')
        x_data.append(l[i][0])
        y_data.append(l[i][1])

    
    fig, ax = plt.subplots()
    ax.barh(y_data, x_data)
    
#wort_haeufigkeiten(text)

def worte(text):
    
    # Leerzeichen und Tabs am Ende und am Anfang des textes entfernen
    text = text.strip()
    
    # Der gesamte Text wird in Kleinbuchstaben umgewandelt
    text = text.lower()
    
    # Satz- und Sonderzeichen aus dem gesamten Text löschen
    import string
    text = text.translate(text.maketrans('','',string.punctuation))
    
    # Liste mit einzelnen Worten anlegen
    worte1 = text.split(' ')
    
    d_worte = {} # Dictionary initialisieren
    
    def find_stopwords():
        ''' Stop words oder Stoppwörter sind sind häufig verwendete Wörter, die keine
        oder nur geringe Inhalteliche Informationen enthalten. 
        Diese Funkttion soll lädt die Stopwörter in der jeweiligen Landessprache und gibt diese in einer Variablen vom Typ nltk.set zurück.
        '''
        # importieren der Bibliothek nltk davon eine Bibliothek mit Stopwords
        import nltk
        #nltk.download('stopwords')
        from nltk.corpus import stopwords
        
        
        meta = parsed["metadata"]
        
        if meta['language'] == 'EN':
            sprache = 'english'
        elif meta['language'] == 'DE':
            sprache = 'german'
        elif meta['language'] == 'FR':
            sprache = 'french'
        
        # Speichern der engliscchen Stopwörter in einer Variablen
        st_wo = set(stopwords.words(sprache))
        
        lst = list(st_wo)
    
        return lst

    # Findet Stopwörter der jeweiligen Sprache und speichert sie in eine Liste
    filterliste = find_stopwords()
    filterliste.append(chemische_formeln(text))
    filterliste.append(finde_links(text))
    
    filtered = [] # Liste initialisieren
    # Aus der gefunden Woertliste werden die Stopwörter, die Chemischen Formeln und die einezelnen Elemente und Buchstaben rausgefiltert
    for wort in worte1:
        if wort not in filterliste and len(wort)>2 and len(wort)<20:
            filtered.append(wort)

    d_worte = {} # Dictionary initialisieren
    # Dictionary füllen
    for wort in filtered:
        d_worte[wort] = d_worte.get(wort,0) + 1          
        
    print(d_worte)
    

    # Ermittlung der Häugigsten Wörter 
    l = list()
    for key, val in d_worte.items():
        l.append((val, key))

    # Abspeichern der gefundenen Wörter in einer Liste von Tupeln, nach häufigkeit sortieren
    l.sort(reverse = True)

    x_data = []
    y_data = []

    print("Auflistung der 10 häufigsten Worte: ")
    for i in range(10):
        print(f'Das Wort: "{l[i][1]}" wurde {l[i][0]} mal im Text gefunden.')
        x_data.append(l[i][0])
        y_data.append(l[i][1])

    fig, ax = plt.subplots()
    ax.barh(y_data, x_data)
    
# worte(text)

def analyse(text):
    
    saetze = nltk.tokenize.sent_tokenize(inhalt)
    woerter = nltk.tokenize.word_tokenize(inhalt)    
    
#analyse(text)



def get_metadata(paper):
    with open(paper, 'rb') as f:
        pdf = PdfFileReader(f)
        info = pdf.getDocumentInfo()
        anzahl_seiten = pdf.getNumPages()

    print("\n")
    print(info)
    print("\n")
    autor = info.author
    ersteller = info.creator
    produzent = info.producer
    thematik = info.subject
    titel = info.title

    print("Titel: "+ titel)
    print("Autor: "+ autor)
    print("Creator: "+ersteller)
    print("Producer: "+produzent)
    print("Subject: "+thematik)
    print("Anzahl Seiten: "+ str(anzahl_seiten))


#get_metadata(paper)
