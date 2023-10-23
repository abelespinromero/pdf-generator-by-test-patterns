from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
import random
import os
import string
import locale


########################################################################################################################################
#TYPE 1 PDFS GENERATOR FUNCTIONS:

# Register the OpenSans font (make sure the TTF file is in your directory or specify the full path)
pdfmetrics.registerFont(TTFont('OpenSans-Regular', 'styles/OpenSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Arial-BoldMT', 'styles/Arial-BoldMT.ttf'))


# Generate PDF of type1
def generate_pdf_type1(pdf_path, data):

    texts_to_find = ["1065392204", "30180280", "21oktober2023", "76242835", "21oktober2023", "E55EYVE0218300CC5E5100"]

    coordinates = find_coordinates_type1("test_files/TestDoc1A.pdf", texts_to_find)

    replace_text_with_coordinates_type1("test_files/TestDoc1A.pdf", pdf_path, coordinates, texts_to_find, data)

######################################################################################################
#TYPE 2 PDFS GENERATOR FUNCTIONS:


# Generate PDF with positioned text for Type 2
def generate_pdf_type2(pdf_path, data):
    texts_to_find = ["SP-182697-23-0193-00", "SP-182697-23-0193-00", "SP-182697-23-0193-00", "SP-182697-23-0193-00", "SP-182697-23-0193-00"]

    coordinates = find_coordinates_type2("test_files/TestDoc2A.pdf", texts_to_find)

    replace_text_with_coordinates_type2("test_files/TestDoc2A.pdf", pdf_path, coordinates, texts_to_find, data)

########################################################################################


import PyPDF2
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

# Function to find the coordinates of the texts to replace in PDF1
def find_coordinates_type1(input_pdf_path, texts_to_find):
    coordinates = []
    pdf_reader = PyPDF2.PdfFileReader(input_pdf_path)
    page_height = pdf_reader.getPage(0).mediaBox[3]
    
    for page_num in range(pdf_reader.numPages):
        with pdfplumber.open(input_pdf_path) as pdf:
            pdf_page = pdf.pages[page_num]
            
            for idx1, text_to_find in enumerate(texts_to_find):
                for idx2, word in enumerate(pdf_page.extract_words()):
                    if word['text'] == text_to_find[0] and pdf_page.extract_words()[idx2+1]['text'] == text_to_find[1]:
                        if idx1 != 4 or pdf_page.extract_words()[idx2 + 12]['text'] == texts_to_find[idx1 + 1][0]:
                            x = word['x0']
                            y = page_height - word['bottom']
                            coordinates.append((x, y))
                            break
    return coordinates

# Function to replace texts using the found coordinates in PDF1
def replace_text_with_coordinates_type1(input_pdf_path, output_pdf_path, coordinates, texts_to_find, replacements_text):
    pdf_reader = PyPDF2.PdfFileReader(input_pdf_path)
    pdf_writer = PyPDF2.PdfFileWriter()
    
    for page_num in range(pdf_reader.numPages):
        page = pdf_reader.getPage(page_num)
        
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        # Create a white "mask" to cover all the content of the page
        can.setFillColor(colors.white)
        can.rect(0, 0, letter[0]+100, letter[1]+100, fill=1, stroke=0)

        # Set the font and size here extracted from extract_styles.py
        font_name = "OpenSans-Regular"
        font_size = 8
        can.setFont(font_name, font_size)
        
        for idx, (text_to_replace, text_to_find) in enumerate(zip(replacements_text, texts_to_find)):
            x, y = coordinates[idx]
            if x is not None and y is not None:


                # Draw the new text
                can.setFillColor(colors.black)
                can.drawString(x, y, text_to_replace)

        
        can.save()
        packet.seek(0)
        new_pdf = PyPDF2.PdfFileReader(packet)
        page.mergePage(new_pdf.getPage(0))
        pdf_writer.addPage(page)
        
    with open(output_pdf_path, "wb") as out_pdf:
        pdf_writer.write(out_pdf)


# Function to find the coordinates of the texts to replace in PDF2
def find_coordinates_type2(input_pdf_path, texts_to_find):
    coordinates = []
    pdf_reader = PyPDF2.PdfFileReader(input_pdf_path)
    page_height = pdf_reader.getPage(0).mediaBox[3]
    
    for page_num in range(pdf_reader.numPages):
        with pdfplumber.open(input_pdf_path) as pdf:
            pdf_page = pdf.pages[page_num]
            
            for idx1, text_to_find in enumerate(texts_to_find):
                for idx2, word in enumerate(pdf_page.extract_words()):
                    if text_to_find[0] in word['text']:
                            x = word['x0']
                            y = page_height - word['bottom']
                            coord = (x,y)
                            if coord not in coordinates:
                                coordinates.append((x, y))
                                break
                            else:
                                continue
    return coordinates

# Function to replace texts using the found coordinates in PDF2
def replace_text_with_coordinates_type2(input_pdf_path, output_pdf_path, coordinates, texts_to_find, replacement_text):
    pdf_reader = PyPDF2.PdfFileReader(input_pdf_path)
    pdf_writer = PyPDF2.PdfFileWriter()
    
    for page_num in range(pdf_reader.numPages):
        page = pdf_reader.getPage(page_num)
        
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        # Create a white "mask" to cover all the content of the page
        can.setFillColor(colors.white)
        can.rect(0, 0, letter[0]+100, letter[1]+100, fill=1, stroke=0)

        for idx, text_to_find in enumerate(texts_to_find):
            x, y = coordinates[idx]
            if x is not None and y is not None:

                # Draw the new text
                if idx==0:
                    font_name = "Arial-BoldMT"
                    font_size = 12.77929973602295
                else:
                    font_name = "Helvetica"
                    font_size = 7

                can.setFont(font_name, font_size)
                can.setFillColor(colors.black)
                can.drawString(x, y, replacement_text)

        
        can.save()
        packet.seek(0)
        new_pdf = PyPDF2.PdfFileReader(packet)
        page.mergePage(new_pdf.getPage(0))
        pdf_writer.addPage(page)
        
    with open(output_pdf_path, "wb") as out_pdf:
        pdf_writer.write(out_pdf)




