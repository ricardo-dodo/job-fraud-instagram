import pandas as pd
import numpy as np
import torch
import re
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score, accuracy_score, precision_recall_curve
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from torch.nn import CrossEntropyLoss
import optuna
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from langdetect import detect

class FraudDetectionModel:
    def __init__(self, data_file):
        self.data = pd.read_csv(data_file)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = BertTokenizer.from_pretrained('indolem/indobert-base-uncased')
        self.model = None
        self.best_params = None

    def preprocess_data(self):
        self.data['cleaned_OCR_text'] = self.data['OCR_Text'].apply(self.clean_text)
        self.data['tokenized_segments'] = self.data['cleaned_OCR_text'].apply(self.sliding_window_tokenize)
        self.data['processed_text'] = self.data['tokenized_segments'].apply(lambda segs: ' '.join([self.tokens_to_string(seg) for seg in segs]))

    def clean_text(self, text):
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        text = text.replace('\n', ' ').replace('\r', '')
        return text

    def sliding_window_tokenize(self, text, window_size=510, stride=100):
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        window_segments = []
        for i in range(0, len(tokens), stride):
            window = tokens[i:i+window_size]
            if len(window) < window_size:
                window = tokens[-window_size:]
            window_segments.append(window)
        return window_segments

    def tokens_to_string(self, tokens):
        return self.tokenizer.convert_tokens_to_string(self.tokenizer.convert_ids_to_tokens(tokens))

    def prepare_data(self):
        texts = self.data['processed_text'].tolist()
        labels = self.data['Label'].map({'Fraud': 1, 'Not-Fraud': 0}).tolist()
        return train_test_split(texts, labels, test_size=0.2, random_state=42)

    def objective(self, trial):
        learning_rate = trial.suggest_loguniform('learning_rate', 1e-5, 1e-3)
        num_train_epochs = trial.suggest_int('num_train_epochs', 1, 10)
        per_device_train_batch_size = trial.suggest_categorical('per_device_train_batch_size', [8, 16, 32])
        
        model = BertForSequenceClassification.from_pretrained('indolem/indobert-base-uncased', num_labels=2)
        model.to(self.device)
        
        training_args = TrainingArguments(
            output_dir='./results',
            num_train_epochs=num_train_epochs,
            per_device_train_batch_size=per_device_train_batch_size,
            per_device_eval_batch_size=32,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir='./logs',
            learning_rate=learning_rate,
        )
        
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.val_dataset,
            compute_metrics=self.compute_metrics
        )
        
        trainer.train()
        eval_result = trainer.evaluate()
        return eval_result['eval_f1']

    def train_model(self):
        train_texts, val_texts, train_labels, val_labels = self.prepare_data()
        
        self.train_dataset = self.tokenizer(train_texts, truncation=True, padding=True, max_length=512, return_tensors="pt")
        self.train_dataset = torch.utils.data.TensorDataset(self.train_dataset['input_ids'], self.train_dataset['attention_mask'], torch.tensor(train_labels))
        
        self.val_dataset = self.tokenizer(val_texts, truncation=True, padding=True, max_length=512, return_tensors="pt")
        self.val_dataset = torch.utils.data.TensorDataset(self.val_dataset['input_ids'], self.val_dataset['attention_mask'], torch.tensor(val_labels))
        
        study = optuna.create_study(direction='maximize')
        study.optimize(self.objective, n_trials=20)
        
        self.best_params = study.best_params
        print("Best parameters:", self.best_params)
        
        self.model = BertForSequenceClassification.from_pretrained('indolem/indobert-base-uncased', num_labels=2)
        self.model.to(self.device)
        
        training_args = TrainingArguments(
            output_dir='./results',
            num_train_epochs=self.best_params['num_train_epochs'],
            per_device_train_batch_size=self.best_params['per_device_train_batch_size'],
            per_device_eval_batch_size=32,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir='./logs',
            learning_rate=self.best_params['learning_rate'],
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.val_dataset,
            compute_metrics=self.compute_metrics
        )
        
        trainer.train()
        self.eval_result = trainer.evaluate()
        print("Evaluation results:", self.eval_result)

    def compute_metrics(self, pred):
        labels = pred.label_ids
        preds = pred.predictions.argmax(-1)
        precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
        acc = accuracy_score(labels, preds)
        return {
            'accuracy': acc,
            'f1': f1,
            'precision': precision,
            'recall': recall
        }

    def plot_results(self):
        # Implement plotting logic here
        pass

if __name__ == "__main__":
    model = FraudDetectionModel('processed.csv')
    model.preprocess_data()
    model.train_model()
    model.plot_results()