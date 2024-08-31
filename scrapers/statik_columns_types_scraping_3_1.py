


# -*- coding: latin-1 -*-
import functions as f
import fitz
import re
import pandas as pd




"""

3.1.1_Statik_Columns  ( this is for the first type of pdf columns document )

    Code reads statik - columns pdfs, 
    finds tables that contains each column types (S35-1) for each floor
    together with its calculations.
    The dataframe then is stored in the table "Stutzentypentabelle_1"

"""


def process_pdf_file(pdf_path):
    keys = ['Stützen', 'Querschnitt - bxh[cm]1', 'Querschnitt - bxh[cm]2', 'Knicklänge - L[m]', 'Beton', 'Bewehrung - As,l [cm2]', 'Bewehrung - gew.', 'Bemessungslast - NRd [kN]']
    
    def filter_elements_with_numbers(data):
        filtered_data = [element for element in data if re.search(r'[\d*-]', element)]
        if len(filtered_data) % len(keys) != 0:
            filtered_data = filtered_data[:-1]
        return filtered_data

    def split_elements(data):
        split_data = []
        for element in data:
            split_data.extend(element.split())
        return split_data

    data = f.get_annotation_coordinates(pdf_path)
    combined_df_table = pd.DataFrame()

    with fitz.open(pdf_path) as pdf_doc:
        for i in range(len(data[2])):
            page_number = data[2][i]
            page = pdf_doc[page_number]
            print(f"Processing page {page_number + 1}")
         
            coord = data[0][i]
            annot = data[1][i]
            if annot != "":
                x1, y1, x2, y2 = coord
                rect = fitz.Rect(x1, y1, x2, y2)
                extracted_data = page.get_text("text", clip=rect).strip()
                data_lines = extracted_data.split('\n')
            
                filtered_data = filter_elements_with_numbers(data_lines)
                print(len(filtered_data))

                # Preprocess the filtered data to ensure single elements
                preprocessed_data = split_elements(filtered_data)

                def chunk_data(data, chunk_size):
                    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

                chunked_data = chunk_data(preprocessed_data, len(keys))
                df = pd.DataFrame(chunked_data, columns=keys)
                df['geschoss'] = annot
                pd.set_option('display.max_columns', None)
                combined_df_table = pd.concat([combined_df_table, df], ignore_index=True)
                combined_df_table.tableName = "Stutzentypentabelle_1"
    
    return combined_df_table
