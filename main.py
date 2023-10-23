from extract_patterns import extract_pattern_type1, generate_element_type1, extract_pattern_type2, generate_element_type2
from gen_pdfs import generate_pdf_type1, generate_pdf_type2
import os
import datetime



#MAIN PROGRAM

# Generate 100 random PDFs based on the template 1
output_dir1 = 'generated_pdfs1/'
os.makedirs(output_dir1, exist_ok=True)

# Extract template and previous list:
template, previous_previous_list, previous_list = extract_pattern_type1()

# Generate 100 random PDFs based on the template
for i in range(100):

    #PDFS TYPE 1:
    output_path1 = os.path.join(output_dir1, f'RandomPDF1_{i+1}.pdf')

    # Generate a new list based on the template and the previous list
    new_data = []
    for i in range(len(template)):
        is_last = (i == len(template) - 1)
        new_data.append(generate_element_type1(template[i], previous_list[i], is_last))

    
    generate_pdf_type1(output_path1, new_data)


    previous_list = new_data

#####

# Generate 100 random PDFs based on the template 2
output_dir2 = 'generated_pdfs2/'
os.makedirs(output_dir2, exist_ok=True)

# Extract template and previous list:
template, previous_previous_list, previous_list = extract_pattern_type2()

# Generate 100 random PDFs based on the template
for i in range(100):

    #PDFS TYPE 1:
    output_path2 = os.path.join(output_dir2, f'RandomPDF2_{i+1}.pdf')

    # Generate a new list based on the template and the previous list
    new_data = []
    for i in range(len(template)):
        new_data.append(generate_element_type2(template[i], previous_list[i]))
    
    previous_list = new_data.copy()

    new_data = "".join(new_data)
    
    generate_pdf_type2(output_path2, new_data)

