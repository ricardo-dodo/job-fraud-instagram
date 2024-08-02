import pandas as pd
import easyocr
import os

class OCRProcessor:
    def __init__(self, csv_file, image_directory):
        self.csv_file = csv_file
        self.image_directory = image_directory
        self.reader = easyocr.Reader(['id', 'en'])
        self.df = None

    def load_data(self):
        self.df = pd.read_csv(self.csv_file)
        if 'OCR_Text' not in self.df.columns:
            self.df['OCR_Text'] = ''

    def process_images(self):
        for index, row in self.df.iterrows():
            if pd.isna(row['OCR_Text']) or row['OCR_Text'] == '':
                image_path = os.path.join(self.image_directory, row['Filename'])
                if os.path.exists(image_path):
                    print(f'Memproses gambar: {row["Filename"]}')
                    result = self.reader.readtext(image_path)
                    self.df.at[index, 'OCR_Text'] = ' '.join([text[1] for text in result])
                    self.save_progress()
                else:
                    print(f'Gambar tidak ditemukan: {row["Filename"]}')
            else:
                print(f'Sudah diproses: {row["Filename"]}')

    def save_progress(self):
        self.df.to_csv('updated_ocr_unpreprocessed1.csv', index=False)

def main():
    csv_file = 'updated_ocr_unpreprocessed.csv'
    image_directory = 'downloaded_images/'
    
    processor = OCRProcessor(csv_file, image_directory)
    processor.load_data()
    processor.process_images()

