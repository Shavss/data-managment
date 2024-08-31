
import pandas as pd
import PyPDF2
import os
import re
import fitz


#Describe the function here

def extract_first_page(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
    
        pdf_text = ""
    
        page = reader.pages[0]
        pdf_text = page.extract_text()
        lines = pdf_text.split('\n')
        print(lines)
  
                 
    return lines


#Describe the function here    

def extract_matched_data(pdf_path, regex):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
    
        text = ""
        lines = []
        content = ""
        pattern = re.compile(regex)
        max_pages_without_match = 20
        consecutive_pages_without_match = 0 
    
        if len(reader.pages) == 1:
            page = reader.pages[0]
            text = page.extract_text()
            matches = pattern.findall(text)
            if matches:
                content = matches[0]
                lines = content.split('\n')
        
        else:
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                matches = pattern.findall(text)
        
                if matches:
                    # Append the matched lines to pdf_text
                    content += '\n'.join(matches) + '\n'
                    # Reset consecutive_pages_without_match counter
                    consecutive_pages_without_match = 0
                else:
                    consecutive_pages_without_match += 1
                
                if consecutive_pages_without_match >= max_pages_without_match:
                    break
          
            lines = content.strip().split('\n') if content else []
    return lines


#Describe the function here
    
def extract_data_from_coordinates_list(pdf_path, coordinates):
    with fitz.open(pdf_path) as pdf_file:
        page = pdf_file[0]
        extracted_data_list = []
    
        for coord in coordinates:
            x1, y1, x2, y2 = coord
            rect = fitz.Rect(x1, y1, x2, y2)
            extracted_data = page.get_text("text", clip=rect).strip()
            extracted_data_list.extend(extracted_data.split('\n'))
            #print(extracted_data_list)

    return extracted_data_list



def extract_data_from_coordinates_list_all(pdf_path, coordinates):
    with fitz.open(pdf_path) as pdf_file:
        extracted_data_list = []

        for page_number in range(pdf_file.page_count):
            page = pdf_file[page_number]
            for coord in coordinates:
                x1, y1, x2, y2 = coord
                rect = fitz.Rect(x1, y1, x2, y2)
                extracted_data = page.get_text("text", clip=rect).strip()
                extracted_data_list.extend(extracted_data.split('\n'))

    return extracted_data_list

#Describe the function here
   
def find_and_print_coordinates(pdf_path, target_string):
    with fitz.open(pdf_path) as pdf_document:
        page = pdf_document[0] 

        words = page.get_text("words")
        coordinates_list = []
    
        for word in words:
             y1, x2, y2, x1, text = word[:5]
        
             if target_string in text:
                print(f"Coordinates: ({y1}, {x2}, {y2}, {x1}), Text: {text}")
                coordinates_list.append((y1, x2, y2, x1, text))
            
    return coordinates_list



def find_and_print_coordinates_all_pages(pdf_path, target_string):
    coordinates_list = []
    
    with fitz.open(pdf_path) as pdf_document:
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]

            words = page.get_text("words")
        
            for word in words:
                y1, x2, y2, x1, text = word[:5]
        
                if target_string in text:
                    # print(f"Page {page_number + 1}, Coordinates: ({y1}, {x2}, {y2}, {x1}), Text: {text}")
                    coordinates_list.append((page_number + 1, y1, x2, y2, x1, text))
            
    return coordinates_list


def get_annotation_coordinates(pdf_path):
    coordinates = []
    annotations = []
    page_numbers = []
    with fitz.open(pdf_path) as pdf_file:
        for page_number in range(pdf_file.page_count):
            page = pdf_file[page_number]
            annotations_page = page.annots()
            
            if annotations_page:
                for annot in annotations_page:
                    # Get the annotation's rectangle and content
                    annot_rect = annot.rect
                    annot_content = annot.info.get("content", "")
                    coordinates.append((annot_rect.x0, annot_rect.y0, annot_rect.x1, annot_rect.y1))
                    annotations.append(annot_content)
                    page_numbers.append(page_number)
                    print(f'Page: {page_number+1}')
                    print(f'Annotation Coordinates: {annot_rect}')
                    print(f'Annotation Content: {annot_content}')
                    print('\n' + '='*50 + '\n')

    return [coordinates, annotations, page_numbers]
