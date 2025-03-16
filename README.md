# GEO Dataset Clustering

A web service that takes a list of PubMed IDs (PMIDs), retrieves corresponding GEO datasets, and visualizes dataset clusters based on TF-IDF vectors.

## Project Overview

This project:
1. Retrieves GEO dataset information for PubMed IDs using the NCBI E-utilities API
2. Extracts text fields: Title, Experiment type, Summary, Organism, Overall design
3. Creates TF-IDF vector representations of these fields
4. Performs clustering based on text similarity
5. Visualizes the clusters and associations between datasets and PMIDs

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/geo-dataset-clustering.git
cd geo-dataset-clustering

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt