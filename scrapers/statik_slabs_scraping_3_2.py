# -*- coding: latin-1 -*-

import pandas as pd
import fitz  # PyMuPDF
import functions as f



def find_pages_with_word(pdf_path, search_word):
    doc = fitz.open(pdf_path)
    matching_pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if search_word in text:
            matching_pages.append((page_num + 1, text))
    return matching_pages

def should_exclude_line(line):
    exclude_lines = [
        "ZILCH + MÜLLER INGENIEURE GMBH",
        "SOFiSTiK 2022-2.0   WINGRAF - GRAFIK FUER FINITE ELEMENTE",
        "Interaktive Grafiken",
        "SOFiSTiK AG - www.sofistik.de",
        "Kapitel 5.3: Decke über EG",
        "Kapitel 5.3.4: EDV-Bemessung",
        "ZILCH + MÜLLER INGENIEURE",
        "Zilch + Müller Ingenieure GmbH"
    ]
    return any(exclude in line for exclude in exclude_lines)

def filter_lines(text):
    filtered_lines = []
    keep_all_lines = False
    bemessung_decke_line = None
    
    for line in text.split('\n'):
        if len(line.split()) > 1 and not should_exclude_line(line):
            if "Bemessung Decke" in line:
                keep_all_lines = True
                bemessung_decke_line = line
            if keep_all_lines:
                filtered_lines.append(line)
                
    return bemessung_decke_line, filtered_lines[1:] if len(filtered_lines) > 1 else None

def analyze_pdf(pdf_path, search_word):
    matching_pages = find_pages_with_word(pdf_path, search_word)
    data = {"Page": [], "Decke": [], "Comment": []}
    
    if matching_pages:
        for page_num, text in matching_pages:
            bemessung_decke_line, filtered_text = filter_lines(text)
            if bemessung_decke_line and filtered_text:
                data["Page"].append(page_num)
                data["Decke"].append(bemessung_decke_line)
                data["Comment"].append('\n'.join(filtered_text))
    
    df = pd.DataFrame(data)
    return df

pdf_path = "C:/Users/ryske/Documents/Data/M-214HB069/Statik/LP4_Abgabe_Teil2_Kap5_Decken.pdf"
search_word = 'Bemessung Decke'
df = analyze_pdf(pdf_path, search_word)
df.dropna(subset=['Comment'])
pd.set_option('display.max_rows', None)
#pd.set_option('display.max_colwidth', None)
print(df)


