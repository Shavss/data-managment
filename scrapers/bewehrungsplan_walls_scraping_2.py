# -*- coding: latin-1 -*-

import functions as f
import os
import pandas as pd
import re

"""

2.2_Bewehrungsplan

    Code reads reinforcement plans and shows the source (file) 
    for more detailed reinforcement information of each wall.
    It filles out the table called "Wandbewehrungstabelle" in the database.

    for example UWL_5_TWP_B_E0_W_202_A.pdf - W-B'/8'-12

"""


def process_pdf_file(pdf_path):
    data = []


    file_name = os.path.basename(pdf_path)
    lines = f.extract_first_page(pdf_path)
        
    # Process lines with "Ansicht"
    lines_with_ansicht = [line for line in lines if "Ansicht" in line]
    extracted_data_ansicht = [line.split(', ')[1] for line in lines_with_ansicht if ', ' in line]
        
    # Append extracted data with "Ansicht" along with the filename
    for line in extracted_data_ansicht:
        data.append({'Filename': file_name, 'Data': line})
        

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)
    df.tableName = "Wandbewehrungstabelle"

    pd.set_option('display.max_rows', None)

    print(df)
    return df
