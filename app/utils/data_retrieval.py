import requests
import xml.etree.ElementTree as ET
import time
import logging
from typing import List, Dict, Optional, Tuple
from app.utils.cache import cached_result, get_from_cache, add_to_cache, pmid_cache, geo_cache

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EUtilsClient:
    """Client for interacting with NCBI E-Utilities API."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    ELINK_URL = f"{BASE_URL}elink.fcgi"
    ESUMMARY_URL = f"{BASE_URL}esummary.fcgi"

    def __init__(self, email: str, tool: str = "geo-dataset-clustering", delay: float = 0.34):
        """
        Initialize the E-Utilities client.

        Args:
            email: User email for NCBI API
            tool: Tool name for NCBI API
            delay: Delay between API requests in seconds (NCBI allows 3 requests per second)
        """
        self.email = email
        self.tool = tool
        self.delay = delay
        self.last_request_time = 0

    def _respect_rate_limit(self):
        """Enforce the NCBI API rate limit."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.delay:
            time.sleep(self.delay - time_since_last_request)

        self.last_request_time = time.time()

    def get_geo_ids_for_pmid(self, pmid: str) -> List[str]:
        """
        Get GEO dataset IDs linked to a PubMed ID.

        Args:
            pmid: PubMed ID

        Returns:
            List of GEO dataset IDs (GSE IDs)
        """
        # Check cache first
        cached = get_from_cache(pmid_cache, pmid)
        if cached is not None:
            logger.info(f"Using cached GEO IDs for PMID {pmid}")
            return cached

        self._respect_rate_limit()

        params = {
            "dbfrom": "pubmed",
            "db": "gds",
            "linkname": "pubmed_gds",
            "id": pmid,
            "retmode": "xml",
            "tool": self.tool,
            "email": self.email
        }

        try:
            response = requests.get(self.ELINK_URL, params=params)
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.text)

            # Extract GEO IDs
            geo_ids = []
            link_set = root.find("LinkSet")

            if link_set is not None:
                link_set_dbs = link_set.findall("LinkSetDb")

                for link_set_db in link_set_dbs:
                    if link_set_db.find("LinkName").text == "pubmed_gds":
                        links = link_set_db.findall("Link")
                        for link in links:
                            geo_id = link.find("Id").text
                            geo_ids.append(geo_id)

            logger.info(f"Found {len(geo_ids)} GEO datasets for PMID {pmid}")

            # Add to cache before returning
            add_to_cache(pmid_cache, pmid, geo_ids)
            return geo_ids

        except requests.exceptions.RequestException as e:
            logger.error(f"Error retrieving GEO IDs for PMID {pmid}: {e}")
            return []

    def get_geo_dataset_details(self, geo_id: str) -> Optional[Dict]:
        """
        Get details for a GEO dataset.

        Args:
            geo_id: GEO dataset ID

        Returns:
            Dictionary containing dataset details
        """
        # Check cache first
        cached = get_from_cache(geo_cache, geo_id)
        if cached is not None:
            logger.info(f"Using cached details for GEO dataset {geo_id}")
            return cached

        self._respect_rate_limit()

        params = {
            "db": "gds",
            "id": geo_id,
            "retmode": "xml",
            "tool": self.tool,
            "email": self.email
        }

        try:
            response = requests.get(self.ESUMMARY_URL, params=params)
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.text)

            # Extract dataset details
            doc_sum = root.find(".//DocSum")
            if doc_sum is None:
                logger.warning(f"No details found for GEO ID {geo_id}")
                return None

            # Initialize dataset details dictionary
            dataset = {
                "geo_id": geo_id,
                "title": "",
                "experiment_type": "",
                "summary": "",
                "organism": "",
                "overall_design": ""
            }

            # Extract item values
            items = doc_sum.findall("Item")
            for item in items:
                item_name = item.get("Name")
                if item_name == "title":
                    dataset["title"] = item.text or ""
                elif item_name == "summary":
                    dataset["summary"] = item.text or ""
                elif item_name == "gdsType":
                    dataset["experiment_type"] = item.text or ""
                elif item_name == "taxon":
                    dataset["organism"] = item.text or ""
                elif item_name == "gdsSubset":
                    sub_items = item.findall("Item")
                    for sub_item in sub_items:
                        if sub_item.get("Name") == "description" and "design" in (sub_item.text or "").lower():
                            dataset["overall_design"] = sub_item.text or ""

            logger.info(f"Retrieved details for GEO dataset {geo_id}")

            # Add to cache before returning
            add_to_cache(geo_cache, geo_id, dataset)

            return dataset

        except requests.exceptions.RequestException as e:
            logger.error(f"Error retrieving details for GEO ID {geo_id}: {e}")
            return None


def get_geo_data_for_pmids(pmids: List[str], email: str) -> Tuple[List[Dict], Dict[str, List[str]]]:
    """
    Get GEO dataset information for a list of PMIDs.

    Args:
        pmids: List of PubMed IDs
        email: User email for NCBI API

    Returns:
        Tuple containing:
        - List of GEO dataset details
        - Dictionary mapping PMIDs to GEO dataset IDs
    """
    client = EUtilsClient(email=email)
    datasets = []
    pmid_to_geo_ids = {}

    for pmid in pmids:
        logger.info(f"Processing PMID: {pmid}")

        # Get GEO IDs for the PMID
        geo_ids = client.get_geo_ids_for_pmid(pmid)

        if geo_ids:
            pmid_to_geo_ids[pmid] = geo_ids

            # Get details for each GEO dataset
            for geo_id in geo_ids:
                dataset = client.get_geo_dataset_details(geo_id)

                if dataset:
                    # Add PMID association
                    dataset["pmid"] = pmid
                    datasets.append(dataset)

    logger.info(f"Retrieved {len(datasets)} GEO datasets for {len(pmids)} PMIDs")
    return datasets, pmid_to_geo_ids