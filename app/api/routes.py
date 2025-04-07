from flask import Blueprint, request, jsonify, render_template
import json
from app.utils.data_retrieval import get_geo_data_for_pmids
from app.utils.text_processing import preprocess_datasets, create_tfidf_vectors, calculate_similarity_matrix
from app.utils.clustering import perform_clustering, reduce_dimensions, prepare_visualization_data
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/fetch-geo-data', methods=['POST'])
def fetch_geo_data():
    """
    Endpoint to fetch GEO dataset information for a list of PMIDs.

    Expects JSON with:
    - pmids: List of PubMed IDs
    - email: User email for NCBI API

    Returns:
    - datasets: GEO dataset details
    - pmid_associations: Mapping of PMIDs to GEO dataset IDs
    """
    try:
        data = request.get_json()

        if not data or 'pmids' not in data or 'email' not in data:
            return jsonify({
                'error': 'Invalid request. Please provide pmids and email.'
            }), 400

        pmids = data['pmids']
        email = data['email']

        if not isinstance(pmids, list) or not all(isinstance(pmid, str) for pmid in pmids):
            return jsonify({
                'error': 'PMIDs must be provided as a list of strings.'
            }), 400

        # Get GEO dataset information
        datasets, pmid_associations = get_geo_data_for_pmids(pmids, email)

        if not datasets:
            return jsonify({
                'error': 'No GEO datasets found for the provided PMIDs.'
            }), 404

        # Preprocess datasets
        df = preprocess_datasets(datasets)

        # Create TF-IDF vectors
        tfidf_matrix, feature_names, vectorizer = create_tfidf_vectors(df)

        # Calculate similarity matrix
        similarity_matrix = calculate_similarity_matrix(tfidf_matrix)

        # Perform clustering
        cluster_labels, n_clusters = perform_clustering(tfidf_matrix, similarity_matrix)

        # Reduce dimensions for visualization
        reduced_vectors = reduce_dimensions(tfidf_matrix)

        # Prepare visualization data
        visualization_data = prepare_visualization_data(df, reduced_vectors, cluster_labels, pmid_associations)

        # Add cluster information to datasets
        for i, dataset in enumerate(datasets):
            if i < len(cluster_labels):
                dataset['cluster'] = int(cluster_labels[i])

        return jsonify({
            'datasets': datasets,
            'pmid_associations': pmid_associations,
            'visualization': visualization_data,
            'n_clusters': int(n_clusters)
        })

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500


@api_bp.route('/cluster-info', methods=['GET'])
def cluster_info():
    """
    Get information about a specific cluster.

    Expects query parameters:
    - cluster_id: Cluster ID

    Returns:
    - Details about the cluster
    """
    try:
        cluster_id = request.args.get('cluster_id')

        if not cluster_id:
            return jsonify({
                'error': 'Please provide a cluster_id.'
            }), 400

        # This is a placeholder - in a real implementation, you would
        # store cluster information in a database or cache
        return jsonify({
            'message': f'Cluster information not implemented yet. Requested cluster: {cluster_id}'
        })

    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500