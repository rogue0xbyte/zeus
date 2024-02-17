import os
from PIL import Image

# Assuming Aadhar_OCR and PAN_OCR are implemented in separate files and contain methods as per the initial code
from Aadhar_OCR import Aadhar_OCR
#from PAN_OCR import PAN_OCR

def process_aadhar_card(img_path):
    # Simulating the Aadhar OCR process
    aadhar_ocr = Aadhar_OCR(img_path)
    #user_aadhar_no, user_gender, user_dob, user_name = aadhar_ocr.extract_data()
    
    # Display extracted data for user verification
    #print("Extracted Aadhar Details:")
    #print(f"Aadhar No: {user_aadhar_no}\nGender: {user_gender}\nDOB: {user_dob}\nName: {user_name}")
    
    # Verify and commit changes (Simulation)
    input("Press Enter to confirm and commit these details (simulated)...")

def process_pan_card(img_path):
    # Simulating the PAN OCR process
    pan_ocr = PAN_OCR(img_path)
    user_pan_no = pan_ocr.extract_data()
    
    # Display extracted data for user verification
    print("Extracted PAN Details:")
    print(f"PAN No: {user_pan_no}")
    
    # Verify and commit changes (Simulation)
    input("Press Enter to confirm and commit these details (simulated)...")

def main():
    while True:
        # Main menu
        print("Choose the card type to upload:")
        print("1. Aadhar Card")
        print("2. PAN Card")
        print("3. Exit")
        choice = input("Enter your choice (1/2/3): ")
        
        if choice == '1':
            img_path = input("Enter the path of the Aadhar card image: ")
            if os.path.exists(img_path):
                process_aadhar_card(img_path)
            else:
                print("File does not exist. Please check the path.")
                
        elif choice == '2':
            img_path = input("Enter the path of the PAN card image: ")
            if os.path.exists(img_path):
                process_pan_card(img_path)
            else:
                print("File does not exist. Please check the path.")
                
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
