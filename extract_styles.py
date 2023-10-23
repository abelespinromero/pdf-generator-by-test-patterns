import fitz

def extract_styles(keyword, filePath):
    results = [] # list of tuples that store the information as (text, font size, font name) 
    pdf = fitz.open(filePath) # filePath is a string that contains the path to the pdf
    for page in pdf:
        dict = page.get_text("dict")
        blocks = dict["blocks"]
        for block in blocks:
            if "lines" in block.keys():
                spans = block['lines']
                for span in spans:
                    data = span['spans']
                    for lines in data:
                        if keyword in lines['text'].lower(): # only store font information of a specific keyword
                            results.append((lines['text'], lines['size'], lines['font']))
                            # lines['text'] -> string, lines['size'] -> font size, lines['font'] -> font name
    pdf.close()
    return results


# Get style and size of the texts of each PDF
results1 = extract_styles("", "test_files/TestDoc1A.pdf")
print("Fonts for PDF type 1:\n", results1, "\n")
    # -> font: OpenSans-Regular, size: 8

results2 = extract_styles("", "test_files/TestDoc2A.pdf")
print("\nFonts for PDF type 2:\n", results2, "\n")
    # -> Big code: font: Arial-BoldMT, size: 12.77929973602295
    # -> Small codes: font: Helvetica, size: 7