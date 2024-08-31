# -*- coding: latin-1 -*-

import functions as f
import fitz
import re
import pandas as pd




"""

3.1.2_Statik_Columns ( this is for the other type of pdf columns document )
    Code returns 2 dataframes:
    
    1. Dataframe:
        Code reads statik - columns pdfs, 
        finds tables that contain each column types for each floor eg. (0.1)
        together with its calculations. 
        The dataframe then is stored in the table "Stutzentypentabelle_2".
    
    2. Dataframe:
        Then manually each plan containing all the columns should be
        annotated with a rectangle making sure the annotation field 
        is filled with a string 'columns'. The code will scrape the columns
        visible on the plan, and then manually the column types have to be assigned
        to the right column in the database. There might be a case when the scraper
        scraped too many columns from the floor. 
        In case some columns don't have a type assigned to it, delete the row.
        The dataframe is stored in the table "Stutzentypentabelle_2". 
    
"""


def process_pdf_file(pdf_path):
    keys = ['Typ', 'maßg. Stutze', 'Abmessungen - b[cm]', 'Abmessungen - h[cm]', 'Knicklange [m]', 'Betongute', 'cnom [mm]', 'Belastung - FEd [kN]', 'Stabilitat - NRd [kN]', 'Stabilitat - n', 'vorh. As']
    
    def filter_elements_with_numbers(data):
        filtered_data = [element for element in data if re.search(r'[\d-]', element)]
        if len(filtered_data) % len(keys) != 0:
            filtered_data = filtered_data[:-1]
        return filtered_data

    def filter_column_elements(data):
        return [element for element in data if element.startswith('S') or element.startswith('F') or element.startswith('0')]

    data = f.get_annotation_coordinates(pdf_path)
    combined_df_table = pd.DataFrame()
    combined_df_columns  = pd.DataFrame()

    with fitz.open(pdf_path) as pdf_doc:
        for i in range(len(data[2])):
            page_number = data[2][i]
            page = pdf_doc[page_number]
            print(f"Processing page {page_number + 1}")
         
            coord = data[0][i]
            annot = data[1][i]
            x1, y1, x2, y2 = coord
            rect = fitz.Rect(x1, y1, x2, y2)
            extracted_data = page.get_text("text", clip=rect).strip()
            data_lines = extracted_data.split('\n')
            
            if annot != "columns":
                filtered_data = filter_elements_with_numbers(data_lines)
                print(len(filtered_data))
                
                def chunk_data(data, chunk_size):
                    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

                chunked_data = chunk_data(filtered_data, len(keys))
                df = pd.DataFrame(chunked_data, columns=keys)
                df['geschoss'] = annot
                pd.set_option('display.max_columns', None)
                combined_df_table = pd.concat([combined_df_table, df], ignore_index=True)
                combined_df_table.tableName = "Stutzentabelle_2"
            else:
                columns = filter_column_elements(data_lines)
                df = pd.DataFrame(columns, columns=['columns'])
                df['type'] = None
                df['shape'] = "square"
                df['geschoss'] = data[1][i-1]
                df = df.drop_duplicates(subset=['columns'], keep='first')
                combined_df_columns = pd.concat([combined_df_columns, df], ignore_index=True)
                combined_df_columns.tableName = "Stutzentypentabelle_2"
    
   # return [combined_df_table, combined_df_columns]
    return combined_df_columns