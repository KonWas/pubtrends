from flask import Blueprint, request, jsonify
import json
from app.utils.data_retrieval import get_geo_data_for_pmids

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

        return jsonify({
            'datasets': datasets,
            'pmid_associations': pmid_associations
        })

    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500