# -*- coding: latin-1 -*-

import tabula
import functions as f
import pandas as pd
import re

#file = "C:/Users/ryske/Documents/PDFs_3/07_Wande.pdf"


"""

3.3_Statik_Walls

"""

def process_pdf_file(pdf_path):
    material_tables = []
    system_tables = []
    qnr_tables = []
    loads_tables = []
    loads2_tables = []
    forces_tables = []
    combo_tables = []
    forces2_tables = []
    deformations_tables = []


    regex = r'(SOFiSTiK.*COLUMN(?:.*\n.*)*)'
    project_name = f.extract_first_page(pdf_path)[0]
    pdf_text = f.extract_matched_data(pdf_path, regex)

    coordinatess = [(56.640045166015625, 58.37398147583008, 71.1240463256836, 70.57510375976562)]
    textif = f.extract_data_from_coordinates_list_all(pdf_path,coordinatess )

    extracted_data_list_filtered = [data for data in textif if 'W' in data]

    #Remove duplicates
    unique_list = []
    for item in extracted_data_list_filtered:
        if item not in unique_list:
            unique_list.append(item)
    wall_names = unique_list


    data = {'type': 'Wand', 'name': wall_names, 'project_id': None,  'project_name': [project_name] * len(wall_names)}
    elements_df = pd.DataFrame(data)
    elements_df.tableName = "Elementen Table"
   

    tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
    # Process each table
    j = 0
    for i, table in enumerate(tables):
        table = table.fillna(0)
        cleaned_table_string = table.to_string().replace('\n', ' ')
    
        # 1) Material
        if "Bezeichnung" in cleaned_table_string:
            print(cleaned_table_string)


            material_df = pd.DataFrame(table.iloc[:, :2]) #first 2 columns
            print(material_df)
            material_df = material_df.rename(columns={'Bezeichnun4g.110': 'Bezeichnung'})
            material_df['MNr'] = material_df['MNr Art'].apply(lambda x: x.split()[0] if len(x.split()) > 1 else None) 
            material_df['Art'] = material_df['MNr Art'].apply(lambda x: x.split()[1] if len(x.split()) > 1 else None) 
            material_df['Wall_Name'] = elements_df['name'][j]
            material_df = material_df.drop(['MNr Art'], axis=1)
            material_df['element_id'] = None
        
            material_df = material_df[['Wall_Name', 'MNr', 'Art', 'Bezeichnung']]
            #j = j + 1


            material_tables.append(material_df)
        
        # 2) Cross Section
        if "Bewehrungsanordnung" in cleaned_table_string:
            print(cleaned_table_string)
            qnr_df = pd.DataFrame(table.iloc[1:3, :])
            new_columns = ['QNr_t', 'Form_t', 'b', 'a', 'Bewehrungsanordnung']
            qnr_df.columns = new_columns
            qnr_df['QNr'] = qnr_df['QNr_t'].apply(lambda x: x.split()[0] if len(x.split()) > 1 else None)
            qnr_df['Form'] = qnr_df['QNr_t'].apply(lambda x: x.split()[1] if len(x.split()) > 1 else None)
            try:
                qnr_df['b'] = qnr_df['QNr_t'].apply(lambda x: x.split()[2] if len(x.split()) > 1 else None)
            except IndexError:
                qnr_df['b'] = '0'
            qnr_df['h'] = qnr_df['Form_t'].apply(lambda x: x.split()[0] if len(x.split()) > 1 else None)
            qnr_df['a'] = qnr_df['Form_t'].apply(lambda x: x.split()[1] if len(x.split()) > 1 else None)
            try:
                qnr_df['Bewehrungsanordnung'] = qnr_df['Form_t'].apply(lambda x: x.split()[2] if len(x.split()) > 1 else None)
            except IndexError:
                qnr_df['Bewehrungsanordnung'] = '0'
            
            qnr_df = qnr_df.drop(['QNr_t', 'Form_t'], axis=1)
            qnr_df['Wall_Name'] = elements_df['name'][j]
        
            qnr_df_combined = qnr_df[['Wall_Name', 'QNr', 'Form', 'b', 'h',  'a', 'Bewehrungsanordnung']]
            qnr_tables.append(qnr_df_combined)

      
        
        # 3) System  
        if "Achse" in cleaned_table_string and "fest" in  cleaned_table_string:
            system_df = pd.DataFrame(table.iloc[[1 ,2], :])
            system_df = system_df.rename(columns={'Stab  QNrAchse': 'Label', 'Kote  KNr': 'Kote', 'Unnamed: 1': 'u-x', 'Festhaltungen': 'u-y', '...': 'phi-x'}).drop(columns=['Exzentrizität', 'Unnamed: 0'])
            default_value = 'default' 
            system_df['Label'] = system_df['Label'].replace('11', default_value)
            system_df['KNr'] = system_df['Kote'].astype(str).str[-1]
            system_df['Kote'] = system_df['Kote'].astype(str).str[:-1]
            system_df['Wall_Name'] = elements_df['name'][j]
            system_df = system_df[['Wall_Name', 'Label', 'Länge', 'Kote', 'KNr', 'u-x', 'u-y', 'phi-x']]
       
            #system_df_filtered = system_df.iloc[[1 ,2], :]
            pd.set_option('display.max_columns', None)
            #print(system_df_filtered.columns)
            system_tables.append(system_df)
        
        # 4) Einzellasten
        if "Einw" in cleaned_table_string and "Stab" in  cleaned_table_string:
            loads_df = pd.DataFrame(table.iloc[[1, 2], :])
            loads_df['Wall_Name'] = elements_df['name'][j]
            loads_df['Einw'] = loads_df['Einw Typ'].apply(lambda x: x.split()[0] if len(x.split()) > 1 else None) 
            loads_df['Typ'] = loads_df['Einw Typ'].apply(lambda x: x.split()[1] if len(x.split()) > 1 else None) 
            loads_df = loads_df.drop(['Einw Typ'], axis=1)
            j = j + 1
        
            loads_df = loads_df[['Wall_Name', 'Einw', 'Typ', 'Stab', 'Kote', 'Pz', 'ex', 'ey', 'Hx', 'Hy', 'Mx', 'My']]
            loads_tables.append(loads_df)
        
        # 5) Streckenlasten
        if "LF" in cleaned_table_string and "Stab" in  cleaned_table_string:
            loads2_df = pd.DataFrame(table.iloc[[1, 2], :])
            loads2_df['Wall_Name'] = elements_df['name'][j-1]
        
            loads2_df['LF'] = loads2_df['LF Typ'].apply(lambda x: x.split()[0] if len(x.split()) > 1 else None) 
            loads2_df['Typ'] = loads2_df['LF Typ'].apply(lambda x: x.split()[1] if len(x.split()) > 1 else None) 
            loads2_df = loads2_df.drop(['LF Typ'], axis=1)
            #j = j + 1
            loads2_df = loads2_df[['Wall_Name', 'LF', 'Typ', 'Stab', 'a', 'L', 'pxo', 'pxu', 'pxo.1', 'pyu', 'pzo', 'pzu']]
            loads2_tables.append(loads2_df)
        
        # 6) Support Forces at the base of the column
        if "Lastfall" in cleaned_table_string and "PX" in  cleaned_table_string:
            forces_df = pd.DataFrame(table.iloc[[1, 2], :])
            desired_column_names = ['Stab', 'Lastfall', 'PX', 'PY', 'PZ', 'MX', 'MY']
        
            while len(forces_df.columns) < len(desired_column_names):
                forces_df[chr(ord('A') + len(forces_df.columns))] = None  # Add a new column with default value None
    
            # Rename columns to desired names
            forces_df.columns = desired_column_names
            i = 0
            number_of_columns = len(forces_df.columns)
            for i in range(len(forces_df.columns) - 1, 0, -1):
                # Shift values from the current column to the next column
                forces_df[forces_df.columns[i]] = forces_df[forces_df.columns[i - 1]]

            # Set the first column to None or any default value
            forces_df[forces_df.columns[0]] = None
            forces_df.at[1, 'Stab'] = 1
            
            for index, row in forces_df.iterrows():
                py_values = row['PY'].split("-")
                # Check if 'PY' column has 2 values
                if len(py_values) == 2:
                    forces_df.at[index, 'PZ'] = float("-"+py_values[1])
                    forces_df.at[index, 'PY'] = float(py_values[0])
                    
            forces_df['Lastfall'] = forces_df['Lastfall'].str.extract(r'([A-Z])')
            forces_df['Wall_Name'] = elements_df['name'][j-1]
  
            forces_tables.append(forces_df)

        # 7) Analyzed combinations
        if "Kombination" in cleaned_table_string:
            combo_df = pd.DataFrame(table)
            combo_df['Wall_Name'] = elements_df['name'][j-1]
            combo_df['(D)'] = combo_df['(D) Kombination'].apply(lambda x: x.split()[0] if len(x.split()) > 1 else None)
            combo_df['Kombination'] = combo_df['(D) Kombination'].apply(lambda x: ' '.join(x.split()[1:]) if len(x.split()) > 1 else None)
            combo_df = combo_df.drop(["(D) Kombination", "..."], axis=1)
            combo_tables.append(combo_df)
        
        # 8) Shear forces and reinforcement
        if "Lastfall" in cleaned_table_string and "My" in cleaned_table_string:
             forces2_df = pd.DataFrame(table.iloc[1 : 13, :])
             value = forces2_df['Lastfall  StabKote'][1]
             parts = value.split('(D)')
             part1 = parts[0] + '(D)' + parts[1][0]
             part2 = parts[1][1:]  
             part3 = part1[-1]
             part1 = part1[:-1]
             forces2_df['Lastfall'] = part1
             forces2_df['Stab'] = part3
             forces2_df.loc[1, 'Lastfall  StabKote'] = part2
             forces2_df = forces2_df.rename(columns={'Lastfall  StabKote': 'Kote'})
             forces2_df['Kote'] = pd.to_numeric(forces2_df['Kote'], errors='coerce')
             forces2_df = forces2_df.dropna(subset=['Kote'])
             forces2_df['Kote'] = forces2_df['Kote'].astype(str).str[-5:]
             forces2_df = forces2_df.drop(['x'], axis=1)
             forces2_df = forces2_df.rename(columns={'Unnamed: 0': 'x'})
             forces2_df['Wall_Name'] = elements_df['name'][j-1]
             forces2_df = forces2_df[forces2_df['N'] != 0]
             forces2_df = forces2_df[['Wall_Name', 'Lastfall', 'Stab' ,'Kote', 'x', 'N', 'Vz', 'My', 'As', 'As-v']]
             forces2_df = forces2_df.reset_index(drop=True)
             forces2_tables.append(forces2_df)
         
        # 8) Deformations
        if "Lastfall" in cleaned_table_string and "ei-X" in cleaned_table_string:
            deformations_df = pd.DataFrame(table.iloc[1 : 12, :])
            value = deformations_df['Lastfall  StabKote'][1]
            parts = value.split('(D)')
            part1 = parts[0] + '(D)' + parts[1][0]
            part2 = parts[1][1:]  
            part3 = part1[-1]
            part1 = part1[:-1]
            deformations_df['Lastfall'] = part1
            deformations_df['Stab'] = part3
            deformations_df.loc[1, 'Lastfall  StabKote'] = part2
            deformations_df = deformations_df.rename(columns={'Lastfall  StabKote': 'Kote'})
            deformations_df = deformations_df.drop(['Unnamed: 0'], axis=1)
            deformations_df['Wall_Name'] = elements_df['name'][j-1]
            deformations_df = deformations_df[['Wall_Name', 'Lastfall', 'Stab' ,'Kote', 'x', 'ei-X', 'u-X', 'u-Z']]
        
            deformations_df = deformations_df.reset_index(drop=True)
            deformations_tables.append(deformations_df)
   
    
        # 9) Reinforcment (Unfinished)
        if "Achse" in cleaned_table_string and "MzRd" in cleaned_table_string:
            reinforcment_df = pd.DataFrame(table.iloc[1 : 2, :])
            reinforcment_df = reinforcment_df.reset_index(drop=True) 
            #print(reinforcment_df.columns)
            #print(reinforcment_df)



        
   
    combined_material_table = pd.concat(material_tables, ignore_index=True)     
    combined_material_table.tableName = "Materialen Table"
    combined_system_table = pd.concat(system_tables, ignore_index=True) 
    combined_system_table.tableName = "System Table"
    combined_qnr_table = pd.concat(qnr_tables, ignore_index=True)
    combined_qnr_table.tableName = "Querschnitte Table"
    combined_loads_table = pd.concat(loads_tables, ignore_index=True) 
    combined_loads_table.tableName = "Einzellasten Table"
    combined_loads2_table = pd.concat(loads2_tables, ignore_index=True)
    combined_loads2_table.tableName = "Streckenlasten Table"
    combined_forces_table = pd.concat(forces_tables, ignore_index=True) 
    combined_forces_table.tableName =  "Auflagerkräfte am Stützenfuß"
    combined_combo_table = pd.concat(combo_tables, ignore_index=True) 
    combined_combo_table.tableName = "Untersuchte Kombinationen Table"
    combined_forces2_table = pd.concat(forces2_tables, ignore_index=True)
    combined_forces2_table.tableName = "Schnittgrossen und Bewehrung Table"
    combined_deformations_table = pd.concat(deformations_tables, ignore_index=True)
    combined_deformations_table.tableName = "Verformungen Table"
     
    return [combined_material_table, combined_qnr_table,
            combined_system_table, combined_loads_table,
            combined_loads2_table, combined_forces_table,
            combined_combo_table, combined_forces2_table,
            combined_deformations_table]

#pdf_path = r"C:/Users/ryske/Documents/Data/M-214HB069/Statik/07_Waende.pdf"
#process_pdf_file(pdf_path)