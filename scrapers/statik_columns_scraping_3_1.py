import pandas as pd
import PyPDF2
import os
import re
import fitz
import functions as f



"""

3.1.1_Statik_Columns  ( this is for the first type of pdf columns document )

    Code reads statik - columns pdfs, 
    finds tables that contains each column with its calculations.
    The dataframe then is stored in the table "Stutzentablle_1",
    The shape column should be entered manually by changing the variable
    df['shape'] here or directly in the table.

"""


def process_pdf_file(pdf_path):
    regex = r'Gk[^\n]*([\s\S]*)'
    project_name = f.extract_first_page(pdf_path)[0]
    pdf_text = f.extract_matched_data(pdf_path, regex)
   

    keys = ['Stutzen', 'Lasten - Gk [kN]', 'Lasten - Qk [kN]', 'Lasten - Ned [kN]', 'Abmessungen - b [cm]', 'Abmessungen - h[cm]', 'Bewehrung - As [cm2]', 'Bewehrung - gew.', 'Druck-NW - NRd [kN]', 'Druck-NW - Eta', 'Stabilitat - NRd [kN]', 'Stabilitat - Eta', 'Typ']
    elements_list = []
  
    data_list = []
    id_counter = 0

    # Split the text into lines and process each line
    for line in pdf_text:
        line = line.replace('*)', '')
        # Split the line into values
        values = re.split(r'\s+', line.strip())
        if len(values) == len(keys):
   
            data_dict = dict(zip(keys, values))
            data_list.append(data_dict)

    df = pd.DataFrame(data_list)
    df['shape'] = None
    df.tableName = "Stutzentablle_1"
    
    return df


