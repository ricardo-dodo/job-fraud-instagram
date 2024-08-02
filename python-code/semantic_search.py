import pandas as pd
import spacy
import re

class SemanticSearch:
    def __init__(self):
        self.nlp_multilang = spacy.load('xx_sent_ud_sm')  # For multilingual
        self.nlp_english = spacy.load('en_core_web_trf')  # For English
        self.df = None

    def load_data(self, file_path):
        self.df = pd.read_csv(file_path)

    @staticmethod
    def is_valid_email(email):
        return re.match(r'\b[\w.-]+@[\w.-]+\.\w{2,}\b', email) and not email.startswith('@')

    def extract_company_names(self, doc):
        return {ent.text for ent in doc.ents if ent.label_ == "ORG"}

    def extract_company_from_email_or_text(self, text):
        emails = re.findall(r'\b[\w.-]+@[\w.-]+\.\w{2,}\b', text)
        extracted_names = set()

        # Try using multilingual and English models
        doc_multilang = self.nlp_multilang(text)
        extracted_names.update(self.extract_company_names(doc_multilang))

        doc_english = self.nlp_english(text)
        extracted_names.update(self.extract_company_names(doc_english))

        # If no company names found, extract from email username and domain
        if not extracted_names:
            for email in emails:
                if self.is_valid_email(email):
                    parts = email.split('@')
                    username = parts[0]
                    domain = parts[1].split('.')[0]
                    extracted_names.add(username.capitalize())
                    extracted_names.add(domain.capitalize())

        return ", ".join(sorted(extracted_names))

    def process_data(self):
        self.df['Extracted_Companies'] = self.df['OCR_Text'].apply(self.extract_company_from_email_or_text)

    def save_results(self, csv_path, excel_path):
        self.df.to_csv(csv_path, index=False)
        self.df.to_excel(excel_path, index=False)

    def run(self, input_file, csv_output, excel_output):
        self.load_data(input_file)
        self.process_data()
        self.save_results(csv_output, excel_output)
        print("Processing complete. Results saved to CSV and Excel files.")

if __name__ == "__main__":
    semantic_search = SemanticSearch()
    semantic_search.run('labeled.csv', 'semantic_search_.csv', 'semantic_search.xlsx')