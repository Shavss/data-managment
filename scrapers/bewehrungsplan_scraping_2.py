import functions as f
import re
import pandas as pd
import os


"""

2.1_Bewehrungsplan

    Code reads reinforcement plans and extract reinforcement information into a dataframe.
    Pricesily it is scraping the table visible on the plans.
    It filles out the table called "Stabliste - Biegeformen table" in the database.

"""

def process_pdf_file(pdf_path):

    regex = r'Biegeform\n([\s\S]*)'
    lines = f.extract_matched_data(pdf_path, regex)

    file_name = os.path.basename(pdf_path)
    formatted_numbers = []

    keys = ['Pos.', 'Stck', 'Gesamt Lange [m]', 'Masse [kg]', 'Einzel Lange [m]', 'Diameter [mm]']

    for line in lines:
        numbers = re.findall(r'\b\d+\.\d+|\b\d+\b', line)
        if len(numbers) == len(keys):
            formatted_numbers.append(numbers)

    df = pd.DataFrame(formatted_numbers, columns=keys)

    # Remove the rows where 'Pos.', 'Stck', and 'Diameter [mm]' columns are not integers and
    # 'Gesamt Lange', 'Masse', 'Einzel Lange' are integers
    if not df.empty:
        df = df[
            df['Pos.'].astype(str).str.isdigit() & 
            df['Stck'].astype(str).str.isdigit() & 
            df['Diameter [mm]'].astype(str).str.isdigit() & 
            ~df['Gesamt Lange [m]'].astype(str).str.isdigit() & 
            ~df['Masse [kg]'].astype(str).str.isdigit() & 
            ~df['Einzel Lange [m]'].astype(str).str.isdigit()
        ]
    
        df['plan_id'] = None
        df['file_name'] = file_name

        # Order of columns
        df = df[['plan_id', 'file_name', 'Pos.', 'Stck', 'Gesamt Lange [m]', 'Masse [kg]', 'Einzel Lange [m]', 'Diameter [mm]']]
        df.tableName = "Stabliste - Biegeformen table"
  
    
        total_lines = int(df['Pos.'].iloc[-1]) - int(df['Pos.'].iloc[0])+1
        success_percentage = (len(df) / total_lines) * 100
        print(f"Success Percentage: {success_percentage:.2f}%")
    else:
        print("No matches found in the PDF file.")
        
    pd.set_option('display.max_columns', None)
    print(f"\nDataFrame for {pdf_path}:\n{df}")
    
    return df
    