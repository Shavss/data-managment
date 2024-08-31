# -*- coding: latin-1 -*-
import functions as f
import fitz  
import re
import pandas as pd



"""

2.3_Bewehrungsplan

    Code reads reinforcement plans and extracts more detailed information
    about reinforcement of each element. For the code to work properly you 
    need to open each reinforcement plan you are intrested in and draw 
    a rectangle annotation box around each element's detail.
    Make sure you annotate the box with the right element name eg. "K1-W3".
    The code works but still needs to be checked afterwards for the corectness.
    It filles out the table called "Bewehrung_detailed" in the database.

"""

def process_pdf_file(pdf_path):
    def extract_data_from_coordinates_list_all(pdf_path, coordinates, annotations):
    
        def merge_lines(data_list):
            merged_data = []
            skip_next = False

            for i in range(len(data_list) - 1):
                if skip_next:
                    skip_next = False
                    continue
            
                current_line = data_list[i].strip()
                next_line = data_list[i + 1].strip()

                if re.match(r"^\d+$", current_line) and re.search(r"ø", next_line):
                    merged_line = f"{current_line} {next_line}"
                    merged_data.append(merged_line)
                    skip_next = True
                else:
                    merged_data.append(current_line)
        
            # Add the last line if it hasn't been merged
            if not skip_next and data_list:
                merged_data.append(data_list[-1].strip())

            return merged_data

        def filter_lines_with_oe(data_list):
            return [line for line in data_list if 'ø' in line]

        def switch_elements(line):
            elements = line.split()
            if len(elements) > 1 and 'ø' in elements[0]:
                elements[0], elements[1] = elements[1], elements[0]
            return ' '.join(elements)

        def process_lines(data_list):
            filtered_lines = filter_lines_with_oe(data_list)
            processed_lines = [switch_elements(line) for line in filtered_lines]
            return processed_lines

        extracted_data_list = []
        data = []

        with fitz.open(pdf_path) as pdf_file:
            for page_number in range(pdf_file.page_count):
                page = pdf_file[page_number]
                for i, coord in enumerate(coordinates):
                    x1, y1, x2, y2 = coord
                    rect = fitz.Rect(x1, y1, x2, y2)
                    extracted_data = page.get_text("text", clip=rect).strip()
                    data_lines = extracted_data.split('\n')
                    merged_lines = merge_lines(data_lines)
                    processed_lines = process_lines(merged_lines)
                
                    for line in processed_lines:
                        elements = line.split(' ', 1)
                        if len(elements) == 2:
                            data.append({
                                'filename': pdf_path,
                                'element': annotations[i],
                                'pos.': elements[0],
                                'stck + ø': elements[1]
                            })

        df = pd.DataFrame(data)
        df.tableName = "Bewehrung_detailed"
        return df


    annotation_coordinates, annotation_contents, page_numbers = f.get_annotation_coordinates(pdf_path)
    df = extract_data_from_coordinates_list_all(pdf_path, annotation_coordinates, annotation_contents)
    pd.set_option('display.max_rows', None)

    print(df)
    return df
   


