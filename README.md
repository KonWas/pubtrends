# GEO Dataset Clustering

A web service that takes a list of PubMed IDs (PMIDs), retrieves corresponding GEO datasets, and visualizes dataset clusters based on TF-IDF vectors.

## Project Overview

This project:
1. Retrieves GEO dataset information for PubMed IDs using the NCBI E-utilities API
2. Extracts text fields: Title, Experiment type, Summary, Organism, Overall design
3. Creates TF-IDF vector representations of these fields
4. Performs clustering based on text similarity
5. Visualizes the clusters and associations between datasets and PMIDs

## Features

- **Data Retrieval**: Fetches GEO dataset information associated with PMIDs from NCBI's E-utilities API
- **Text Processing**: Combines and processes text fields to create TF-IDF vectors
- **Clustering**: Automatically determines optimal number of clusters and performs hierarchical clustering
- **Visualization**: Interactive force-directed graph showing dataset clusters and PMID associations
- **Web Interface**: Simple interface for inputting PMIDs and viewing results

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

# Run the application
python app.py
```
Open your browser and navigate to http://localhost:5000

## Usage
1. Enter one or more PubMed IDs (PMIDs) in the text area, one per line.
    - Example PMIDs: 25404168, 28263301, 27980096
2. Enter your email address (required by NCBI API for usage tracking).
3. Click "Process PMIDs" to start the retrieval and analysis.
4. View the results:
   - The visualization shows datasets as circles colored by cluster
   - PMIDs are shown as orange circles
   - Lines connect related elements
   - Hover over elements to see more details
   - You can zoom and pan the visualization

## Troubleshooting
- If you encounter API rate limits, wait a few minutes before trying again
- For large numbers of PMIDs, the process may take several minutes
- If no clusters appear, try different PMIDs as some may not have associated GEO datasets
