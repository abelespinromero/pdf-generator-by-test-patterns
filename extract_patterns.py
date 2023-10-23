from pdfminer.high_level import extract_text
import regex as re
import string
import random
from datetime import datetime, timedelta

# FUNCTIONS TO EXTRACT PATTERN OF PDF TYPE 1:

# Function to generate the last element based on specific rules
def generate_last_element(previous_last_element):
    new_element = ""
    for i, char in enumerate(previous_last_element):
        # Positions where the character is incremented: 0, 1, 2, 3, 4, 9, 10, 11, 14, 19
        if i in [0, 1, 2, 3, 4, 9, 10, 11, 14, 19]:
            if char.isdigit():
                new_char = str((int(char) + 1) % 10)  # Increment the number by 1, wrap around to 0 if it's 9
            elif char.isalpha():
                new_char = chr(((ord(char) - ord('A') + 1) % 26) + ord('A'))  # Increment the letter by 1, wrap around to 'A' if it's 'Z'
        # Position where a random letter is generated: 5
        elif i == 5:
            new_char = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        # Positions where the character is kept as is: 6, 7, 8, 12, 13, 15, 16, 17, 18, 20, 21
        elif i in [6, 7, 8, 12, 13, 15, 16, 17, 18, 20, 21]:
            new_char = char
        else:
            new_char = char  # Keep the character as is if it's not a special case
        new_element += new_char
    return new_element


# Function toi infer alphanumeric case
def infer_segment_type(segment1, segment2):
    if segment1.isdigit() and segment2.isdigit():
            increment = (int(segment2) - int(segment1)) % 10  # Module 10 to handle the reset at 9
            return {"type": "incremental_number_reset_9", "increment": increment}
    elif segment1.isalpha() and segment2.isalpha() and len(segment1) == len(segment2) == 1:
        if segment1 != segment2:
            return {"type": "incremental_alpha", "increment": ord(segment2) - ord(segment1)}
        else:
            return {"type": "fixed", "value": segment1}
    elif segment1 == segment2:
        return {"type": "fixed", "value": segment1}
    elif segment1.isalpha() and segment2.isalpha() and segment1 != segment2:
        return {"type": "random_alpha"}
    else:
        return {"type": "unknown"}

# Function to generate a new segment based on its type
def generate_segment(segment_type, previous_value):
    if segment_type["type"] == "incremental_number_reset_9":
        new_value = (int(previous_value) + segment_type["increment"]) % 10  # Module 10 to handle the reset at 9
        return str(new_value)
    if segment_type["type"] == "incremental_number":
        new_value = (int(previous_value) + segment_type["increment"]) % 10  # Handling overflow
        return str(new_value)
    elif segment_type["type"] == "incremental_alpha":
        new_value = chr((ord(previous_value) - ord('A') + segment_type["increment"]) % 26 + ord('A'))  # Handling overflow
        return new_value
    elif segment_type["type"] == "fixed":
        return segment_type["value"]
    elif segment_type["type"] == "random_alpha":
        return random.choice(string.ascii_uppercase)  # Using uppercase letters
    else:
        return "unknown"
    
# Function to infer the type of an element
def infer_type(element_1, element_2):
    if element_1.isdigit() and element_2.isdigit():
        return {"type": "incremental_number", "increment": int(element_2) - int(element_1)}
    elif re.search(r'\d{1,2} \w+ \d{4}', element_1) and re.search(r'\d{1,2} \w+ \d{4}', element_2):
        return {"type": "incremental_date"}
    elif element_1.isalpha() and element_2.isalpha():
        return {"type": "incremental_alpha", "increment": ord(element_2[-1]) - ord(element_1[-1])}
    else:
        # Divide the element into alphabetic and numeric segments
        segments_1 = re.findall(r'\d+|\D+', element_1)
        segments_2 = re.findall(r'\d+|\D+', element_2)
        
        if len(segments_1) != len(segments_2):
            return {"type": "unknown"}
        
        inferred_segments = []
        for seg1, seg2 in zip(segments_1, segments_2):
            inferred_segments.append(infer_segment_type(seg1, seg2))
        
        return {"type": "mixed", "segments": inferred_segments}

# Function to extract the pattern from two example PDFs of type 1
def extract_pattern_type1():
    tests_paths = ['test_files/TestDoc1A.pdf', 'test_files/TestDoc1B.pdf']
    tests_lists = []
    for test in tests_paths:
        # Extract text from a pdf.
        text = extract_text(test)

        text = text.replace("\n", "")

        text = text.replace(" ", "")

        TEMPLATE_TYPE1 = [10, 8, 13, 8, 13, 22]

        # Variable initialization
        test_list = []
        last_e = 0
        act_e = 0

        # Proceso de segmentación
        for i,e in enumerate(TEMPLATE_TYPE1):
            act_e += e  # We update act_e by adding e
            segment = text[last_e:act_e]  # We get the text segment from last_e to act_e
            
            if i==2 or i==4:
                # Initialize an empty output string
                segment_tmp = ""
                # Initialize the previous character type to None
                prev_char_type = None

                # Iterate through each character in the input string
                for char in segment:
                    # Determine the current character type (digit or not)
                    curr_char_type = "digit" if char.isdigit() else "non-digit"
                    
                    # If the current and previous character types are different, add a space to the output string
                    if prev_char_type and curr_char_type != prev_char_type:
                        segment_tmp += " "
                    
                    # Add the current character to the output string
                    segment_tmp += char
                    
                    # Update the previous character type for the next iteration
                    prev_char_type = curr_char_type
                
                segment = segment_tmp

            test_list.append(segment)  # Add the segment to test_list
            last_e = act_e  # Update last_e for next iteration


        tests_lists.append(test_list)


    test_list_1 = tests_lists[0]
    test_list_2 = tests_lists[1]


    # Initialize an empty list to store the template
    template = []

    # Iterate over the elements from the first test list
    for index, element_1 in enumerate(test_list_1):
        # Get the corresponding element from the second test list
        element_2 = test_list_2[index]
        
        # Check if the elements are the same in both test lists
        if element_1 == element_2:
            # If they are the same, use the element as a fixed value in the template
            template.append({"type": "fixed", "value": element_1})
        else:
            # If they are different, infer the type and increment for generating values
            template.append(infer_type(element_1, element_2))

    previous_previous_list = test_list_1
    previous_list = test_list_2

    return template, previous_previous_list, previous_list


# Translated months eng->nl (English to Dutch)
month_translation = {
    'January': 'januari',
    'February': 'februari',
    'March': 'maart',
    'April': 'april',
    'May': 'mei',
    'June': 'juni',
    'July': 'juli',
    'August': 'augustus',
    'September': 'september',
    'October': 'oktober',
    'November': 'november',
    'December': 'december'
}

# Translate month dutch to english
def translate_month_dl_to_en(date_str):
    for english, german in month_translation.items():
        date_str = date_str.replace(german, english)
    return date_str

# Translate month english to germany
def translate_month_en_to_dl(date_str):
    for english, german in month_translation.items():
        date_str = date_str.replace(english, german)
    return date_str


# Function to generate a new element based on the template and a previous element
def generate_element_type1(template_item, previous_element=None, is_last=False):
    if is_last:
            return generate_last_element(previous_element)
    element_type = template_item.get("type")
    if element_type == "fixed":
        return template_item.get("value")
    elif element_type == "incremental_number":
        increment = template_item.get("increment", 0)
        return str(int(previous_element) + increment)
    elif element_type == "incremental_date":
        # Assuming the date format is "day month year"
        date_format = "%d %B %Y"
        translated_previous_element = translate_month_dl_to_en(previous_element)
        previous_date = datetime.strptime(translated_previous_element, date_format)
        new_date = previous_date + timedelta(days=1)  # Incrementing by one day as an example
        new_date_str = new_date.strftime(date_format)
        translated_new_date = translate_month_en_to_dl(new_date_str)
        return translated_new_date
    
    elif element_type == "mixed":
        segments = template_item.get("segments", [])
        prev_segments = re.findall(r'\d+|\D+', previous_element)
        new_segments = []
        for i, segment in enumerate(segments):
            new_segments.append(generate_segment(segment, prev_segments[i]))
        return "".join(new_segments)
    else:
        return "unknown"


###################################################################################################################################################

# FUNCTIONS TO EXTRACT PATTERN OF PDF TYPE 2:

# Function to extract the pattern from two example PDFs of type 2
def extract_pattern_type2():
    tests_paths = ['test_files/TestDoc2A.pdf', 'test_files/TestDoc2B.pdf']
    tests_lists = []
    for test in tests_paths:
        # Extract text content from a PDF file.
        text = extract_text(test)
        # Remove newline characters and spaces.
        text = text.replace("\n", "")
        text = text.replace(" ", "")
        
        # Define the template structure for type 2 documents.
        TEMPLATE_TYPE2 = [2, 1, 6, 1, 2, 1, 4, 1, 2]

        # Initialize variables
        test_list = []
        last_e = 0
        act_e = 0

        # Segment extraction process
        for i,e in enumerate(TEMPLATE_TYPE2):
            act_e += e  # Update act_e by adding e
            segment = text[last_e:act_e]  # Extract the segment from text from last_e to act_e

            test_list.append(segment) # Add the extracted segment to the test_list
            last_e = act_e  # Update last_e for the next iteration

        # Append this test_list to the collection
        tests_lists.append(test_list)

    # Extract the lists from the tests
    test_list_1 = tests_lists[0]
    test_list_2 = tests_lists[1]


    # Initialize an empty list to store the template
    template = []

    # Iterate over the elements from the first test list
    for index, element_1 in enumerate(test_list_1):
        # Get the corresponding element from the second test list
        element_2 = test_list_2[index]
        
        # Check if the elements are the same in both test lists
        if element_1 == element_2:
            # If they are the same, use the element as a fixed value in the template
            template.append({"type": "fixed", "value": element_1})
        else:
            # If they are different, infer the type and increment for generating values
            template.append(infer_type(element_1, element_2))
    
    # Define the lists to be used as previous lists in future iterations
    previous_previous_list =  test_list_1
    previous_list = test_list_2

    return template, previous_previous_list, previous_list

# Function call to extract pattern type 2
template, previous_previous_list, previous_list = extract_pattern_type2()


# Function to generate a new element based on the template and a previous element
def generate_element_type2(template_item, previous_element=None):
    element_type = template_item.get("type")
    if element_type == "fixed":
        return template_item.get("value")
    elif element_type == "incremental_number":
        increment = template_item.get("increment", 0)
        return str(int(previous_element) + increment)
    else:
        return "unknown"

