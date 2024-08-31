# -*- coding: latin-1 -*-

import logging
from tkinter import W
import positionplan_scraping_1 as pp_scraping
import bewehrungsplan_scraping_2 as bwp_scraping
import bewehrungsplan_walls_scraping_2 as bwp_w_scraping
import bewerungsplan_reinforcement_scraping_2 as bwp_r_scraping
import statik_columns_scraping_3_1 as c_scraping
import statik_columns_types_scraping_3_1 as ct_scraping
import statik_columns_scraping_3_2 as c2_scraping
import statik_slabs_scraping_3 as s_scraping
import statik_walls_scraping_3 as w_scraping
import os
import sqlalchemy as db
import pandas as pd
import pyodbc

# Set up logging
logging.basicConfig(filename='output_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_all_pdfs(parser, pdf_folder, connection_string):
    # Establish connection 
    engine = db.create_engine(connection_string)
    try:
        for filename in os.listdir(pdf_folder):
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(pdf_folder, filename)
                df = parser.process_pdf_file(pdf_path)
                
                # Check if the dataframe is empty
                if df.empty:
                    logging.info(f"No data found in {filename}, skipping.")
                    continue
                
                table_name = df.tableName
                insert_into_database(df, engine, table_name)
    finally:
        engine.dispose()

def insert_into_database(df, engine, table_name):
    try:
        # Use the to_sql() method to insert the dataframe into the database
        df.to_sql(table_name, con=engine, if_exists='append', index=False)
        logging.info(f"Data inserted successfully into table {table_name}.")
    except Exception as e:
        logging.error("Error:", exc_info=True)

if __name__ == '__main__':
    # Sensitive data is hidden using environment variables
    pdf_folder = os.getenv('PDF_FOLDER_PATH')
    parser = c2_scraping
    
    # Connection string to the local database
    connection_string = os.getenv('LOCAL_DB_CONNECTION_STRING')

    # Connection string to the Azure SQL Server
    connection_string2 = os.getenv('AZURE_DB_CONNECTION_STRING')

    process_all_pdfs(parser, pdf_folder, connection_string2)