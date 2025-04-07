import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def preprocess_datasets(datasets: List[Dict]) -> pd.DataFrame:
    """
   Convert dataset dictionaries to a DataFrame and prepare for TF-IDF processing.

   Args:
       datasets: List of dataset dictionaries

   Returns:
       DataFrame with combined text field
   """
    if not datasets:
        logger.warning("No datasets provided")
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(datasets)

    # Fill Nan values with empty strings
    text_columns = ['title', 'experiment_type', 'summary', 'organism', 'overall_design']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].fillna('')

    # Combine text fields
    df['combined_text'] = (
        df['title'] + ' ' +
        df['experiment_type'] + ' ' +
        df['summary'] + ' ' +
        df['organism'] + ' ' +
        df['overall_design']
    )

    logger.info(f"Preprocessed {len(df)} datasets")
    return df

def create_tfidf_vectors(dataframe: pd.DataFrame) -> Tuple[np.ndarray, List[str], TfidfVectorizer]:
    """
    Create TF-IDF vectors from dataset text.

    Args:
        dataframe: DataFrame with combined_text column

    Returns:
        Tuple containing:
        - TF-IDF matrix
        - List of feature names
        - TF-IDF vectorizer instance
    """
    if 'combined_text' not in dataframe.columns or dataframe.empty:
        logger.warning("No text data available")
        return np.array([]), [], TfidfVectorizer()

    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=5000,
        min_df=2,
        max_df=0.7,
        stop_words='english',
        ngram_range=(1, 2)
    )

    # Transform text data to TF-IDF vectors
    tfidf_matrix = vectorizer.fit_transform(dataframe['combined_text'])

    # Get feature names
    try:
        feature_names = vectorizer.get_feature_names_out()
    except AttributeError:
        feature_names = vectorizer.get_feature_names()

    logger.info(f"Created TF-IDF vectors with shape {tfidf_matrix.shape}")
    return tfidf_matrix, feature_names, vectorizer

def calculate_similarity_matrix(tfidf_matrix: np.ndarray) -> np.ndarray:
    """
    Calculate cosine similarity matrix from TF-IDF matrix.

    Args:
        tfidf_matrix: TF-IDF matrix

    Returns:
        Cosine similarity matrix
    """
    if tfidf_matrix.size == 0:
        logger.warning("No TF-IDF matrix provided")
        return np.array([])

    # Calculate cosine similarity
    similarity_matrix = cosine_similarity(tfidf_matrix)
    logger.info(f"Calculated {similarity_matrix.shape[0]}x{similarity_matrix.shape[1]} similarity matrix")
    return similarity_matrix
