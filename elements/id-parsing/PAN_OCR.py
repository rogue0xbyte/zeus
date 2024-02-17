#Importing Required Packages.
import cv2
import pytesseract
import re
import mysql.connector as mc
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class PAN_OCR:
    def __init__(self, img_path):
        self.user_pan_no = str()
        self.img_name = img_path
    
    def extract_data(self):
        # Reading the image, extracting text from it, and storing the text into a list.
        img = cv2.imread(self.img_name)
        text = pytesseract.image_to_string(img)
        all_text_list = re.split(r'[\n]', text)
        
        # Process the text list to remove all whitespace elements in the list.
        text_list = list()
        for i in all_text_list:
            if re.match(r'^(\s)+$', i) or i=='':
                continue
            else:
                text_list.append(i)

        # Extracting all the necessary details from the pruned text list.
        # 1) PAN Card No.
        pan_no_pat = r'Permanent Account Number Card|Permanent Account Number|Permanent Account|Permanent'
        pan_no = str()
        for i, text in enumerate(text_list):
            if re.match(pan_no_pat, text):
                pan_no = text_list[i+1]
            else:
                continue

        for i in pan_no:
            if i.isalnum():
                self.user_pan_no = self.user_pan_no + i
            else:
                continue
                
        return self.user_pan_no
    
    def commit_changes(self, pan_no):
        # Commit details to a mysql database
        # Change the 'database' attribute in the line below to match your database and make sure that the server is running before executing this code.
        mydb = mc.connect(host='localhost', user='root', passwd='root', database='fyp_pan')
        mycursor = mydb.cursor()

        # Make sure that the table, attribute names match the ones in your database.
        insert_query = "Insert into card_details(pan_no) values(%s)"
        card_details = (pan_no, )

        mycursor.execute(insert_query, card_details)

        mydb.commit()
