
import pandas as pd
import PyPDF2
import fitz
import functions as f




"""

3.2_Statik_Slabs 

    Code reads statik -slabs pdfs, 
    finds annotated 

"""

def process_pdf_file2(pdf_file):
    
    def get_pages(pdf_path):
        pages_with_wingraf = []

        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
        
            # Iterate through each page to find "WinGraf"
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
            
                # Check if "WinGraf" is in the text of the page
                if "WinGraf" in text:
                    #print(f"Page {page_num + 1} contains 'WinGraf'")
                    pages_with_wingraf.append(page_num + 1)

        return pages_with_wingraf


    def extract_all_annotations(pdf_path, pages):
        # Open the PDF file
        document = fitz.open(pdf_path)
    
        annotations = []
    
        # Iterate through specified pages
        for page_num in pages:
            page = document[page_num - 1]  # fitz uses 0-based indexing
            # Extract annotations from the page
            annot = page.first_annot
            while annot:
                annot_type = annot.type[0]
                # Skip annotation type 3
                if annot_type == 3:
                    annot = annot.next
                    continue
                annot_text = annot.info.get("content", "")
                annotations.append({
                    'page': page_num,
                    'type': annot_type,
                    'text': annot_text
                })
                annot = annot.next
    
        return annotations

    # Example usage
    #pdf_path = "C:/Users/ryske/Documents/PDFs_3/5.1_Decke_UG_zP.pdf"

    # Step 1: Get pages with "WinGraf"
    pages_with_wingraf = get_pages(pdf_path)

    # Step 2: Extract annotations from those pages
    annotations = extract_all_annotations(pdf_path, pages_with_wingraf)

    # Step 3: Extract the floor name
    lines = f.extract_first_page(pdf_path)
    filtered_lines = [line for line in lines if "Decke" in line]
    floor_name = filtered_lines[0] if filtered_lines else "Unknown"

    # Step 4: Create DataFrame with floor name, comment, and page number
    data = []

    for annotation in annotations:
        data.append({
            'Floor Name': floor_name,
            'Comment': annotation['text'],
            'Page Number': annotation['page']
        })

    df = pd.DataFrame(data)
    df.tableName = "Deckentabelle"
    print(df)
    return df


pdf_path = "C:/Users/ryske/Documents/Data/M-214HB069/Statik/LP4_Abgabe_Teil2_Kap5_Decken.pdf"
process_pdf_file2(pdf_path)
