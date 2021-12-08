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
paper = "paper-01.pdf"

# Überprüfen, ob eine Datei in der Variablen paper vorhanden ist. Wenn nicht, variable "Papper" lehr ist, Datei von URL abrufen und in paper speicher 
if not os.path.isfile(paper):
     request.urlretrieve(url, paper)

# Extrahieren des Dateiinhaltes und in der Variablen parsed abspeichern
parsed = tika.parser.from_file(paper)


# druckbaren Zeichenfolge der pdf-Datei in die Variable Text speichern
import string
text = ''.join(filter(lambda x:x in string.printable, parsed["content"]))


# metadaten
# meta = parsed["metadata"]

# for key in meta:
#     print(f"{key}: --> {meta[key]} ")

# df = pd.DataFrame(list(meta.items()),columns=['Keys','Values'])
# print(df)    


def finde_links(text):
    
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
    matches = re.findall(r"\b[A-Z][a-z]?\d*|\([^)]+\)\d*\b", text)
    
    #for m in matches:
    #    print(m, end=', ')
    
    # Periodensystem nach Ordnungszahl in Tuple: "perodicttabele" abspeichern    
    from chempy.util import periodic 
    periodictable = periodic.symbols


        
        
    def element_haeufigkeiten(matches):    
        
        # matplotlib für grafische Darstellung importieren
        import matplotlib.pyplot as plt
        
        elemente = {} 

        # Schleife durchsucht die Liste: "matches" nach regulären Ausdrücken für einen Grußbuchstaben gefolgt von einem Kleinbuchstaben und speichert sie in die Variable: "elems"
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
            # Wenn die boolsche Variable "Test" noch auf "True" steht, ist der gefundende Ausdruck im Periodensystem enthalten und wird in der Liste: Formulars abgespeichert.
            if test:                         
                if e in elemente:
                    elemente[e] += 1
                else:
                    elemente[e] = 1
        

        # Ermittlung der Häugigsten Wörter 
        l = list()
        for key, val in elemente.items():
            l.append((val, key))
    
        # Abspeichern der gefundenen Wörter in einer Liste von Tupeln, nach häufigkeit sortieren
        l.sort(reverse = True)
    
        print("Auflistung der 10 häufigsten Elemente: ")
        for i in range(10):
            print(f'Das Element: "{l[i][1]}" wurde {l[i][0]} mal im Text gefunden.')
    
        plt.figure(figsize=(30,5)) 
        
        x = range(len(elemente))
        y = list(elemente.values())
        x_ticks = list(elemente.keys())
        plt.bar(x, y, align='center')
        plt.xticks(x, x_ticks, rotation=0, fontsize=18)
        plt.show()
        
        for i in range(len(elemente)): 
          
            
            print(i, end = "\t\t") 
          
            
            if len(periodic.names[i]) > 7: 
                print(periodic.names[i], end = "\t") 
            else: 
                print(periodic.names[i], end = "\t\t") 
          
            
            print(periodic.symbols[i], end = "\t\t") 
          
            
            print(periodic.relative_atomic_masses[i]) 
        
        return elemente
            
    formulars =  []
    nonformulars =  []
        
    formulars = element_haeufigkeiten(matches)
    
    print("Atomic No.\tName\t\tSymbol\t\tMass") 
      
    
    
    
    return formulars



x = chemische_elemente(text)


print(x)

def chemische_formeln(text):
    
    # Bibliothek für REs importieren
    import re
    
    from chempy.util import periodic
    
    # Alle gfundenen Übereinstimmungen in Liste: "matches" abspeichern
    matches = re.findall(r"[0-9]*[A-Z][a-z]{0,1}[0-9]*[A-Z]*[a-z]*[0-9]*", text)
    #matches = re.findall(r"[0-9]*[A-Z][a-z]{0,1}[A-Z]*[a-z]*[0-9]*", text)
    
    print(len(matches))
    # for i in matches:
    #     print(i, end='-->')
    
chemische_formeln(text)    

def wort_haeufigkeiten(text):
    
    import re

    worte1 = re.findall('([A-ZÄÖÜ]?[a-zäöü][a-zäöü]+)',text)

    worte = {} # Dictionarry implementieren
        
    wort = '' # Variable wort implementieren
        
    for wort in worte1:
            
        if wort in worte:
            worte[wort] += 1
        else:
            worte[wort] = 1

    # Ermittlung der Häugigsten Wörter 
    l = list()
    for key, val in worte.items():
        l.append((val, key))

    # Abspeichern der gefundenen Wörter in einer Liste von Tupeln, nach häufigkeit sortieren
    l.sort(reverse = True)

    print("Auflistung der 10 häufigsten Worte: ")
    for i in range(10):
        print(f'Das Wort: "{l[i][1]}" wurde {l[i][0]} mal im Text gefunden.')

#wort_haeufigkeiten(text)

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
