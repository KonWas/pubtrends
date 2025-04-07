import unittest
import json
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from app import create_app


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_api_endpoint_validation(self):
        # Test missing fields
        response = self.client.post('/api/fetch-geo-data',
                                    json={})
        self.assertEqual(response.status_code, 400)

        # Test invalid PMID format
        response = self.client.post('/api/fetch-geo-data',
                                    json={'pmids': 'not-a-list', 'email': 'test@example.com'})
        self.assertEqual(response.status_code, 400)

    def test_api_endpoint_with_valid_data(self):
        # This test makes real API calls, so it's slow
        # You might want to mock the external API calls in a real test suite
        response = self.client.post('/api/fetch-geo-data',
                                    json={'pmids': ['25404168'], 'email': 'test@example.com'})

        # Check if response is valid JSON
        data = json.loads(response.data)

        # Verify the response structure
        self.assertIn('datasets', data)
        self.assertIn('pmid_associations', data)
        self.assertIn('visualization', data)


if __name__ == '__main__':
    unittest.main()