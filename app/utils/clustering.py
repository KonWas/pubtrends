import numpy as np
from sklearn.cluster import AgglomerativeClustering, KMeans, DBSCAN
from sklearn.manifold import TSNE
import pandas as pd
from typing import List, Dict, Tuple, Any
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def estimate_optimal_clusters(similarity_matrix: np.ndarray, max_clusters: int = 10) -> int:
    """
    Estimate the optimal number of clusters using the silhouette score.

    Args:
        similarity_matrix: Cosine similarity matrix
        max_clusters: Maximum number of clusters to consider

    Returns:
        Estimated optimal number of clusters
    """
    from sklearn.metrics import silhouette_score

    distance_matrix = 1 - similarity_matrix

    # If there are too few samples, return a small number
    if distance_matrix.shape[0] < 2:
        return 1

    max_clusters = min(max_clusters, distance_matrix.shape[0] - 1)
    if max_clusters <= 1:
        return 1

    # Try different numbers of clusters
    silhouette_scores = []
    for n_clusters in range(2, max_clusters + 1):
        if similarity_matrix.shape[0] < n_clusters:
            continue

        # Perform clustering
        clustering = AgglomerativeClustering(
            n_clusters=n_clusters,
            linkage='average'
        ).fit(distance_matrix)

        # Skip if all samples are in the same cluster
        if len(set(clustering.labels_)) == 1:
            continue

        # Compute the silhouette score
        try:
            score = silhouette_score(distance_matrix, clustering.labels_, metric='precomputed')
            silhouette_scores.append((n_clusters, score))
        except ValueError as e:
            logger.warning(f"Error computing silhouette score for {n_clusters} clusters: {e}")

    if not silhouette_scores:
        return min(3, similarity_matrix.shape[0] - 1) if similarity_matrix.shape[0] > 1 else 1

    # Return the number of clusters with the highest silhouette score
    optimal_clusters = max(silhouette_scores, key=lambda x: x[1])[0]
    logger.info(f"Estimated optimal number of clusters: {optimal_clusters}")
    return optimal_clusters

def perform_clustering(tfidf_matrix: np.ndarray, similarity_matrix: np.ndarray) -> Tuple[np.ndarray, int]:
    """
    Perform hierarchical clustering on datasets based on similarity.

    Args:
        tfidf_matrix: TF-IDF matrix
        similarity_matrix: Cosine similarity matrix

    Returns:
        Tuple containing:
        - Cluster labels
        - Number of clusters
    """
    if tfidf_matrix.shape[0] <= 1:
        logger.warning("Not enough samples for clustering")
        return np.zeros(tfidf_matrix.shape[0], dtype=int), 1

    # Estimate the optimal number of clusters
    n_clusters = estimate_optimal_clusters(similarity_matrix)

    # Convert similarity matrix to distance matrix
    distance_matrix = 1 - similarity_matrix

    # Perform hierarchical clustering
    clustering = AgglomerativeClustering(
        n_clusters=n_clusters,
        linkage='average'
    ).fit(distance_matrix)

    labels = clustering.labels_
    logger.info(f"Performed clustering with {n_clusters} clusters")
    return labels, n_clusters


def reduce_dimensions(tfidf_matrix: np.ndarray, n_components: int = 2) -> np.ndarray:
    """
    Reduce dimensions of TF-IDF vectors for visualization.

    Args:
        tfidf_matrix: TF-IDF matrix
        n_components: Number of dimensions to reduce to

    Returns:
        Reduced dimensionality matrix
    """
    if tfidf_matrix.shape[0] <= 1:
        logger.warning("Not enough samples for dimension reduction")
        if tfidf_matrix.shape[0] == 1:
            return np.zeros((1, n_components))
        return np.array([])

    # Apply t-SNE for dimensionality reduction
    tsne = TSNE(
        n_components=n_components,
        perplexity=min(30, max(3, tfidf_matrix.shape[0] // 5)),
        random_state=42
    )

    # Handle small datasets
    if tfidf_matrix.shape[0] < 4:
        logger.warning("Too few samples for t-SNE, using random positions")
        return np.random.rand(tfidf_matrix.shape[0], n_components)

    try:
        reduced_vectors = tsne.fit_transform(tfidf_matrix.toarray())
        logger.info(f"Reduced dimensions to {n_components}D")
        return reduced_vectors
    except Exception as e:
        logger.error(f"Error reducing dimensions: {e}")
        return np.random.rand(tfidf_matrix.shape[0], n_components)


def prepare_visualization_data(
        df: pd.DataFrame,
        reduced_vectors: np.ndarray,
        cluster_labels: np.ndarray,
        pmid_to_geo_ids: Dict[str, List[str]]
) -> Dict[str, Any]:
    """
    Prepare data for visualization.

    Args:
        df: DataFrame with dataset information
        reduced_vectors: Reduced dimensionality vectors
        cluster_labels: Cluster labels
        pmid_to_geo_ids: Mapping of PMIDs to GEO dataset IDs

    Returns:
        Dictionary with visualization data
    """
    if df.empty or len(reduced_vectors) == 0:
        logger.warning("No data available for visualization")
        return {
            "nodes": [],
            "links": [],
            "clusters": []
        }

    # Create nodes for datasets
    nodes = []
    for i, row in df.iterrows():
        if i >= len(reduced_vectors) or i >= len(cluster_labels):
            continue

        nodes.append({
            "id": row["geo_id"],
            "type": "dataset",
            "title": row["title"],
            "experiment_type": row["experiment_type"],
            "organism": row["organism"],
            "pmid": row["pmid"],
            "x": float(reduced_vectors[i][0]),
            "y": float(reduced_vectors[i][1]),
            "cluster": int(cluster_labels[i])
        })

    # Create nodes for PMIDs
    pmid_nodes = []
    for pmid in pmid_to_geo_ids:
        # Calculate average position of related datasets
        related_datasets = [
            node for node in nodes
            if node["pmid"] == pmid
        ]

        if not related_datasets:
            continue

        avg_x = sum(node["x"] for node in related_datasets) / len(related_datasets)
        avg_y = sum(node["y"] for node in related_datasets) / len(related_datasets)

        pmid_nodes.append({
            "id": pmid,
            "type": "pmid",
            "x": avg_x,
            "y": avg_y,
            "cluster": -1  # PMIDs are not clustered
        })

    # Combine all nodes
    all_nodes = nodes + pmid_nodes

    # Create links between PMIDs and datasets
    links = []
    for pmid, geo_ids in pmid_to_geo_ids.items():
        for geo_id in geo_ids:
            links.append({
                "source": pmid,
                "target": geo_id,
                "type": "pmid_to_dataset"
            })

    # Create links between datasets in the same cluster
    for i, node1 in enumerate(nodes):
        for node2 in nodes[i + 1:]:
            if node1["cluster"] == node2["cluster"]:
                links.append({
                    "source": node1["id"],
                    "target": node2["id"],
                    "type": "same_cluster"
                })

    # Get cluster information
    clusters = []
    for cluster_id in range(max(cluster_labels) + 1):
        cluster_nodes = [node for node in nodes if node["cluster"] == cluster_id]
        if cluster_nodes:
            clusters.append({
                "id": cluster_id,
                "size": len(cluster_nodes),
                "datasets": [node["id"] for node in cluster_nodes]
            })

    visualization_data = {
        "nodes": all_nodes,
        "links": links,
        "clusters": clusters
    }

    logger.info(f"Prepared visualization data with {len(all_nodes)} nodes and {len(links)} links")
    return visualization_data