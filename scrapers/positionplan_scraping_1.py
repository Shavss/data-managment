


import pandas as pd
import PyPDF2
import os
import re
import fitz
import sys
# Get the absolute path of the directory containing the current script
#script_dir = os.path.dirname(os.path.abspath(__file__))

# Add the scrapers directory to the Python path
#sys.path.append(script_dir)

import functions as f  # Now it should find the module

"""

1.1_Positionplannen

    Code reads position plans and extract elements 
    that each floor plan includes. (columns, walls, slabs etc...) into a dataframe.
    Pricesily it is scraping the table from the plans.
    It filles out the table called "Bauelementetabelle" in the database.

"""

def process_pdf_file(pdf_path):
    regex = r'klasse\n([\s\S]*)'
    pdf_text = f.extract_matched_data(pdf_path, regex)

    coordinates_positionplan = [(3007, 2110, 3200, 2127)]
    coordinates_projektnummer = [(3167, 2327, 3220, 2340)]
    coordinates_plannummer = [(3167, 2356, 3275, 2368)]

    grundriss = f.extract_data_from_coordinates_list(pdf_path, coordinates_positionplan)
    projektnummer = f.extract_data_from_coordinates_list(pdf_path, coordinates_projektnummer)
    plannummer = f.extract_data_from_coordinates_list(pdf_path, coordinates_plannummer)
    file_name = os.path.basename(pdf_path)
  
  
    keys = ['Position', 'Bauteil', 'Abmessungen', 'Baustoffe', 'Expositions klasse', 'Key6', 'Key7']
    dfs = []
    
    success_count = 0
    total_lines = len(pdf_text)

    for i, line in enumerate(pdf_text):
        data = [line.split()]
    
        #some lines are longer so lets mannage the Errors like this for now
        try:
            df = pd.DataFrame(data, columns = keys)

            # Join 'Key6' and 'Key7' columns and assign the result to a new column 'NewKey'
            df['Baustoffe'] = df['Expositions klasse']
            df['Expositions klasse'] = df['Key6'] + ' ' + df['Key7']

            df = df.drop(['Key6', 'Key7'], axis=1)
            df['plannummer'] = plannummer
            df['file_name'] =  file_name
            df['grundriss'] = grundriss
            df['plan_id'] = None

            dfs.append(df)
            success_count += 1
        except Exception as e:
            print(f"Error processing line {i + 1}: {e}")
            print(f"Line content: {line}")
                    
    if dfs:
        
        pd.set_option('display.max_columns', None)
        df_final = pd.concat(dfs, ignore_index=True)
        df_final.tableName = "Bauelementetabelle"
        pd.set_option('display.expand_frame_repr', False)
        #print(f"\nDataFrame for {pdf_path}:\n{df_final}")
        
        success_percentage = (success_count / total_lines) * 100
        #print(f"Success Percentage: {success_percentage:.2f}%") 

        
    return  df_final



   

    




      