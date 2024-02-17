import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\sraad\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
import re
# Load the image from file
image_path = r"C:\Users\sraad\Downloads\Screenshot 2024-02-16 235331.png"
image = Image.open(image_path)

text = pytesseract.image_to_string(image, lang='eng+tam')

# Split the text by lines
lines = text.split('\n')

# Filter out any empty lines
lines = [line for line in lines if line.strip() != '']


# Initialize variables to store the extracted information
dob = None
gender = None
aadhar_number = None
name = None

# Define regex patterns
dob_pattern = r'\d{2}/\d{2}/\d{4}'
gender_pattern = r'Male|Female'
aadhar_number_pattern = r'\d{4}\s\d{4}\s\d{4}'

# Extract information
for i, line in enumerate(lines):
    if re.search(dob_pattern, line):
        dob = re.search(dob_pattern, line).group()
        # Since name is always the previous index of dob
        if i > 0:  # To ensure there is a previous line
            name = lines[i-1]  # Get the previous line as name
    if re.search(gender_pattern, line, re.IGNORECASE):
        gender = re.search(gender_pattern, line, re.IGNORECASE).group()
    if re.search(aadhar_number_pattern, line):
        aadhar_number = re.search(aadhar_number_pattern, line).group().replace(" ", "")

# Print extracted information
print(f"Name: {name}")
print(f"DOB: {dob}")
print(f"Gender: {gender}")
print(f"Aadhar Number: {aadhar_number}")

