# Fraud Detection in Job Postings

This project aims to detect fraudulent job postings using machine learning techniques. It includes several steps from data collection to model training and evaluation.

## Project Structure

The project consists of several Jupyter notebooks, each focusing on a specific task:

1. [Data Scraping](#1-data-scraping)
2. [OCR Processing](#2-ocr-processing)
3. [Semantic Search](#3-semantic-search)
4. [Semantic Validation](#4-semantic-validation)
5. [Data Preprocessing](#5-data-preprocessing)
6. [Model Training and Evaluation](#6-model-training-and-evaluation)

### 1. Data Scraping

File: `1.scraping_ig.ipynb`

This notebook contains code for scraping job postings from Instagram. It uses Selenium for web automation and includes functions for:
- Logging into Instagram
- Navigating to specific accounts
- Extracting post information
- Downloading images

### 2. OCR Processing

File: `3.ocr.ipynb`

This notebook processes the images collected from Instagram using Optical Character Recognition (OCR). It uses the EasyOCR library to extract text from images.

### 3. Semantic Search

File: `4.Semantic_Search.ipynb`

This notebook implements semantic search functionality, likely to find similar job postings or to validate the content of the posts.

### 4. Semantic Validation

File: `5.semantic_validate.ipynb`

This notebook focuses on validating the semantic content of the job postings, possibly to identify suspicious or fraudulent content.

### 5. Data Preprocessing

File: `6. Preprocessing.ipynb`

This notebook handles data preprocessing tasks, including:
- Text cleaning
- Tokenization
- Lemmatization
- Language detection

### 6. Model Training and Evaluation

File: `7. model.ipynb`

This notebook contains the core of the fraud detection model:
- Model architecture using BERT
- Hyperparameter tuning with Optuna
- Training process
- Evaluation metrics and visualization

## Main Model

The main fraud detection model is implemented in the `FraudDetectionModel` class. Key features include:

- Use of IndoBERT for sequence classification
- Sliding window tokenization for long texts
- Hyperparameter optimization
- Evaluation metrics including accuracy, F1 score, precision, and recall

## Requirements

The project uses several Python libraries, including:
- pandas
- numpy
- torch
- transformers
- scikit-learn
- optuna
- matplotlib
- nltk
- Sastrawi
- langdetect

## Usage

To run the project:

1. Install the required dependencies
2. Execute the notebooks in order from 1 to 7
3. The final model and results will be available in the `7. model.ipynb` notebook

## Note

This project is designed to work with Indonesian language job postings. Adjustments may be needed for other languages or datasets.