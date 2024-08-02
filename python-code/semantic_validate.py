import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt

class SemanticValidator:
    def __init__(self, semantic_search_file, company_ratings_file):
        self.semantic_search = pd.read_csv(semantic_search_file)
        self.company_ratings = pd.read_csv(company_ratings_file)
        self.data = None
        self.vectorizer = TfidfVectorizer()

    def preprocess_data(self):
        self.semantic_search['Extracted_Companies'].fillna('', inplace=True)
        self.company_ratings['Company Name'].fillna('', inplace=True)

    def vectorize_companies(self):
        all_companies = pd.concat([self.semantic_search['Extracted_Companies'], self.company_ratings['Company Name']], ignore_index=True)
        self.vectorizer.fit(all_companies)
        semantic_vecs = self.vectorizer.transform(self.semantic_search['Extracted_Companies'])
        company_vecs = self.vectorizer.transform(self.company_ratings['Company Name'])
        return semantic_vecs, company_vecs

    def calculate_similarity(self, semantic_vecs, company_vecs):
        similarity_matrix = cosine_similarity(semantic_vecs, company_vecs)
        return similarity_matrix

    def map_companies(self, similarity_matrix, threshold=0.5):
        self.semantic_search['semantic_validate'] = [
            self.company_ratings['Company Name'][sim.argmax()] if max(sim) >= threshold else ''
            for sim in similarity_matrix
        ]

    def convert_to_float(self, s):
        try:
            return float(str(s).replace(',', '.'))
        except ValueError:
            return None

    def process_data(self):
        self.data = self.semantic_search.copy()
        columns_to_check = self.data.columns[4:11]
        for col in columns_to_check:
            self.data[col] = self.data[col].apply(self.convert_to_float)

    def update_company_info(self):
        for index, row in self.data.iterrows():
            if row['Perusahaan tidak jelas atau tidak ada informasi valid (40%)'] == 0.0:
                if pd.isna(row['semantic_validate']):
                    self.data.at[index, 'Perusahaan tidak jelas atau tidak ada informasi valid (40%)'] = 0.4

    def calculate_total_and_label(self):
        self.data['Total'] = self.data[self.data.columns[4:10]].sum(axis=1)
        self.data['Label'] = self.data['Total'].apply(lambda x: 'Fraud' if x > 0.7 else 'Not-Fraud')

    def plot_label_distribution(self):
        label_counts = self.data['Label'].value_counts()
        plt.figure(figsize=(8, 6))
        ax = label_counts.plot(kind='bar', color=['green', 'red'])
        plt.title('Comparison of Fraud and Not-Fraud Labels')
        plt.xlabel('Label')
        plt.ylabel('Count')
        plt.xticks(rotation=0)

        for p in ax.patches:
            ax.annotate(str(p.get_height()), 
                        (p.get_x() + p.get_width() / 2., p.get_height() / 2), 
                        ha='center', va='center', 
                        fontsize=16, color='white')

        plt.show()

    def save_results(self, output_file):
        self.data.to_csv(output_file, index=False)

    def run(self):
        self.preprocess_data()
        semantic_vecs, company_vecs = self.vectorize_companies()
        similarity_matrix = self.calculate_similarity(semantic_vecs, company_vecs)
        self.map_companies(similarity_matrix)
        self.process_data()
        self.update_company_info()
        self.calculate_total_and_label()
        self.plot_label_distribution()
        self.save_results('Merged_data.csv')

if __name__ == "__main__":
    validator = SemanticValidator('semantic_search.csv', 'company_ratings.csv')
    validator.run()