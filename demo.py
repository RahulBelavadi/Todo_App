import os
import re
import fitz  # PyMuPDF
import pandas as pd
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, font
from datetime import datetime
from collections import defaultdict

class PatientDataProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Patient Data Processor")
        self.root.geometry("1000x700")
        
        # Variables
        self.pdf_directory = tk.StringVar()
        self.excel_path = tk.StringVar(value="de.xlsx")
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Frame for input controls
        input_frame = tk.LabelFrame(self.root, text="Input Parameters", padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # PDF Directory
        tk.Label(input_frame, text="PDF Directory:").grid(row=0, column=0, sticky=tk.W)
        tk.Entry(input_frame, textvariable=self.pdf_directory, width=50).grid(row=0, column=1)
        tk.Button(input_frame, text="Browse", command=self.browse_pdf_directory).grid(row=0, column=2)
        
        # Excel File
        tk.Label(input_frame, text="Excel File:").grid(row=1, column=0, sticky=tk.W)
        tk.Entry(input_frame, textvariable=self.excel_path, width=50).grid(row=1, column=1)
        tk.Button(input_frame, text="Browse", command=self.browse_excel_file).grid(row=1, column=2)
        
        # Process Button
        tk.Button(input_frame, text="Process Files", command=self.process_files, 
                 bg="#4CAF50", fg="white").grid(row=2, column=1, pady=10)
        
        # Log Output
        log_frame = tk.LabelFrame(self.root, text="Processing Log", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=100, height=25)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags
        self.log_text.tag_config("red", foreground="red")
        self.log_text.tag_config("blue", foreground="blue")
        self.log_text.tag_config("purple", foreground="purple")
        
        # Clear Button
        tk.Button(self.root, text="Clear Log", command=self.clear_log).pack(side=tk.RIGHT, padx=10, pady=5)
    
    def browse_pdf_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.pdf_directory.set(directory)
    
    def browse_excel_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if filepath:
            self.excel_path.set(filepath)
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
    
    def log_message(self, message, tag=None):
        if tag:
            self.log_text.insert(tk.END, message + "\n", tag)
        else:
            self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def format_dob(self, dob_str):
        """Convert DOB formats to DD-MM-YYYY"""
        try:
            if "/" in dob_str:
                parts = dob_str.split("/")
                return f"{parts[1]}-{parts[0]}-{parts[2]}"  # DD-MM-YYYY
            elif "-" in dob_str:
                parts = dob_str.split("-")
                if len(parts[0]) == 4:  # YYYY-MM-DD
                    return f"{parts[2]}-{parts[1]}-{parts[0]}"  # Convert to DD-MM-YYYY
                return dob_str  # Already in DD-MM-YYYY
            elif len(dob_str) == 8:  # MMDDYYYY
                return f"{dob_str[2:4]}-{dob_str[:2]}-{dob_str[4:]}"
            return "Invalid Format"
        except:
            return "Invalid Format"
    
    def format_excel_date(self, date_val):
        """Convert Excel date to consistent format"""
        if pd.isna(date_val):
            return "Not Available"
        if isinstance(date_val, str):
            return date_val.split()[0]  # Remove time if present
        try:
            return date_val.strftime("%Y-%m-%d")  # Format as YYYY-MM-DD
        except:
            return str(date_val)
    
    def extract_patient_details(self, pdf_path):
        """Extract patient details from a single PDF using specified field names"""
        try:
            doc = fitz.open(pdf_path)
            text = "\n".join([page.get_text("text") for page in doc])

            patterns = {
                "First Name": (r"First\s*Name\s*[:]?\s*(\w+)", re.IGNORECASE),
                "Last Name": (r"Last\s*Name\s*[:]?\s*([^\n]+?)(?=\s*(?:Date of Birth|$))", re.IGNORECASE),
                "Date of Birth": (r"Date\s*of\s*Birth\s*[:]?\s*(\d{2}[/-]\d{2}[/-]\d{4})", re.IGNORECASE),
                "Email Address": (r"Email\s*Address\s*[:]?\s*([^\s]+@[^\s]+)", re.IGNORECASE),
                "Home Address": (r"Home\s*Address\s*[:]?\s*([^\n]+)", re.IGNORECASE),
                "Mobile Phone": (r"Mobile\s*Phone\s*#?\s*[:]?\s*(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})", re.IGNORECASE),
                "Work Phone": (r"Work\s*Phone\s*#?\s*[:]?\s*(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})", re.IGNORECASE),
                "Home Phone": (r"Home\s*Phone\s*#?\s*[:]?\s*(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})", re.IGNORECASE),
                "Social Security": (r"Social Security[:#\s]*\n?(\d{3}[-.\s]?\d{2}[-.\s]?\d{4}|\d{9})", re.IGNORECASE),
                "Insurance Policy": (r"Policy\s*(?:Number)?\s*[:]?\s*(.*?)\s*(?:Group|Tricare|$)", re.IGNORECASE),
                "Referring Physician Name": (r"Referring Physician Name\s*[:]?\s*([^\n:]+)(?=\s*(?:Physician's Address|$))", re.IGNORECASE),
            }

            extracted = {}
            for field, (pattern, flags) in patterns.items():
                match = re.search(pattern, text, flags)
                extracted[field] = match.group(1).strip() if match else "Not Found"
                if extracted.get("Referring Physician Name", "Not Found") not in ["Not Found", ""]:
                    self.log_message(f"Referring Physician Name: {extracted['Referring Physician Name']}")

            # Format Date of Birth
            if extracted["Date of Birth"] != "Not Found":
                extracted["Date of Birth"] = self.format_dob(extracted["Date of Birth"])
            elif "Referring Physician Name:" in text:
            # Case where label exists but no name
                self.log_message("Referring Physician Name: Not Specified")

                
            # Format Social Security Number
            if extracted["Social Security"] != "Not Found":
                ssn_clean = extracted["Social Security"].replace("-", "").replace(".", "").replace(" ", "")
                if len(ssn_clean) == 9:
                    extracted["Social Security"] = f"{ssn_clean[:3]}-{ssn_clean[3:5]}-{ssn_clean[5:]}"

            # Log policy value if found
            policy_value = extracted.get("Insurance Policy", "Not Found")
            if policy_value and policy_value != "Not Found":
                # self.log_message(f"Policy Value: ", None)
                self.log_text.insert(tk.END, policy_value.strip(), "purple")
                self.log_text.insert(tk.END, "\n")

            return extracted
        except Exception as e:
            self.log_message(f"Error processing {pdf_path}: {str(e)}")
            return None
    
    def create_name_index(self, df):
        """Create an alphabetical index for faster searching"""
        index = defaultdict(list)
        for _, row in df.iterrows():
            first_name = str(row['Patient First Name']).strip().lower()
            if first_name:
                first_letter = first_name[0]
                index[first_letter].append(row)
        return index
    
    def check_against_excel(self, extracted, name_index, filename):
        """Compare extracted data with Excel records using the index"""
        try:
            first_name = extracted.get("First Name", "").strip().lower()
            last_name = extracted.get("Last Name", "").strip().lower()

            if not first_name:
                self.log_message("\nNo first name found in PDF")
                return False

            # Get relevant rows based on first letter
            first_letter = first_name[0]
            potential_matches = name_index.get(first_letter, [])

            # Find exact match
            match = None
            for row in potential_matches:
                row_first = str(row['Patient First Name']).strip().lower()
                row_last = str(row['Patient Last Name']).strip().lower()
                
                if row_first == first_name and row_last == last_name:
                    match = row
                    break

            if match is None:
                self.log_message(f"\nNo match found in Excel for: {first_name.title()} {last_name.title()}")
                return False

            # Get patient details
            middle_initial = str(match.get('Patient Middle Initial', '')).strip()
            full_name = f"{match['Patient First Name']}{', ' + middle_initial if middle_initial else ''}, {match['Patient Last Name']}"
            account_no = match.get('Patient Acct No', 'Not Available')

            # Print patient info
            self.log_message(f"\nName: {full_name}")
            self.log_message(f"Account Number: {account_no}")
            
            # Display SSN if found (in blue)
            if extracted.get("Social Security", "Not Found") != "Not Found":
                self.log_message(f"Social Security Number: ", None)
                self.log_text.insert(tk.END, extracted["Social Security"], "blue")
                self.log_text.insert(tk.END, "\n")
                
            # Display Policy if found (in purple)
            if extracted.get("Insurance Policy", "Not Found") != "Not Found":
                self.log_message(f"Insurance Policy: ", None)
                self.log_text.insert(tk.END, extracted["Insurance Policy"], "purple")
                self.log_text.insert(tk.END, "\n")
                
            # Display Referring Physician if found
            if extracted.get("Referring Physician Name", "Not Found") != "Not Found":
                self.log_message(f"Referring Physician Name: {extracted['Referring Physician Name']}")

            # Field comparison - matches all Excel fields
            fields_to_compare = {
                'Patient First Name': 'First Name',
                'Patient Last Name': 'Last Name',
                'Patient DOB': 'Date of Birth',
                'Patient Email': 'Email Address',
                'Patient Address Line 1': 'Home Address',
                'Patient Cell Phone': 'Mobile Phone',
                'Patient Work Phone': 'Work Phone',
                'Patient Home Phone': 'Home Phone',
                'Demographics Referring Provider Name': 'Referring Physician Name',
                'SSN': 'Social Security',
                'Policy': 'Insurance Policy',
                'Refering Name': 'Referring Physician Name'
            }

            update_fields = []
            dob_mismatch = False
            ssn_mismatch = False

            for excel_col, pdf_key in fields_to_compare.items():
                excel_val = self.format_excel_date(match.get(excel_col)) if excel_col == 'Patient DOB' else str(match.get(excel_col, "")).strip()
                pdf_val = str(extracted.get(pdf_key, "")).strip()

                if excel_col == 'Patient DOB' and excel_val and pdf_val and excel_val != pdf_val:
                    dob_mismatch = True
                    self.log_message(f"\nDOB Mismatch:")
                    self.log_message(f"   Excel: {excel_val}")
                    self.log_message(f"   PDF: {pdf_val}")
                    self.log_message(f"   ⚠️ ACTION: Verify manually")
                elif excel_col == 'SSN' and excel_val and pdf_val and excel_val != pdf_val:
                    ssn_mismatch = True
                    self.log_message(f"\nSSN Mismatch:")
                    self.log_message(f"   Excel: {excel_val}")
                    self.log_message(f"   PDF: {pdf_val}", "blue")
                    self.log_message(f"   ⚠️ ACTION: Verify manually")
                elif not excel_val and pdf_val and pdf_val != "Not Found":
                    update_fields.append(excel_col.replace('Patient ', '').replace('Demographics ', ''))

            if update_fields:
                self.log_message(f"\n❌ Update needed: ", None)
                self.log_text.insert(tk.END, ", ".join(update_fields), "red")
                self.log_text.insert(tk.END, "\n")

            return True

        except Exception as e:
            self.log_message(f"\nError comparing with Excel: {str(e)}")
            return False
    
    def process_files(self):
        pdf_directory = self.pdf_directory.get()
        excel_path = self.excel_path.get()
        
        if not pdf_directory:
            messagebox.showerror("Error", "Please select a PDF directory")
            return
        
        if not excel_path:
            messagebox.showerror("Error", "Please select an Excel file")
            return
        
        self.log_message("\n" + "="*50)
        self.log_message(f"Starting processing of PDFs in: {pdf_directory}")
        self.log_message("="*50 + "\n")
        
        # Show scanning message
        self.log_message("Scanning...\n")
        self.root.update()
        
        # Load Excel data once and create index
        self.log_message("Loading Excel data...")
        try:
            df = pd.read_excel(excel_path).fillna("")
        except Exception as e:
            self.log_message(f"Error loading Excel file: {str(e)}")
            messagebox.showerror("Error", f"Failed to load Excel file: {str(e)}")
            return

        name_index = self.create_name_index(df)
        self.log_message(f"Created index for {len(df)} patients\n")

        processed_count = 0
        pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            self.log_message("No PDF files found in the directory.")
            messagebox.showwarning("Warning", "No PDF files found in the selected directory")
            return

        for filename in pdf_files:
            pdf_path = os.path.join(pdf_directory, filename)
            self.log_message("\n" + "="*30)
            self.log_message(f"Processing: {filename}")
            self.log_message("="*30)

            extracted_data = self.extract_patient_details(pdf_path)
            if extracted_data:
                self.check_against_excel(extracted_data, name_index, filename)
                processed_count += 1

        self.log_message(f"\nProcessing complete. {processed_count} PDFs processed out of {len(pdf_files)} found.")
        messagebox.showinfo("Complete", f"Processed {processed_count} PDF files")

if __name__ == "__main__":
    root = tk.Tk()
    app = PatientDataProcessor(root)
    root.mainloop()