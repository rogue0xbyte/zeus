import pytesseract
from PIL import Image
import re
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\sraad\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
class Aadhar_OCR:
    def __init__(self, image_path):
        self.image_path = image_path

    def extract_data(self):
        try:
            image = Image.open(self.image_path)
            text = pytesseract.image_to_string(image, lang='eng+tam')
            dob_pattern = r'\d{2}/\d{2}/\d{4}'
            gender_pattern = r'Male|Female'
            aadhar_number_pattern = r'\d{4}\s\d{4}\s\d{4}'
            dob = None
            gender = None
            aadhar_number = None
            name = None
            lines = text.split('\n')
            lines = [line for line in lines if line.strip() != '']
            for i, line in enumerate(lines):
                if re.search(dob_pattern, line):
                    dob = re.search(dob_pattern, line).group()
                    if i > 0: 
                        name = lines[i-1]
                if re.search(gender_pattern, line, re.IGNORECASE):
                    gender = re.search(gender_pattern, line, re.IGNORECASE).group()
                if re.search(aadhar_number_pattern, line):
                    aadhar_number = re.search(aadhar_number_pattern, line).group().replace(" ", "")
            if all([aadhar_number, gender, dob, name]):
                return [aadhar_number, gender, dob, name]
            else:
                return None
        except Exception as e:
            print(f"Error processing document: {e}")
            return None
