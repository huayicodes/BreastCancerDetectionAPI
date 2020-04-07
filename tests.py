from api import app
import unittest
import json

class BasicTests(unittest.TestCase):
    def test_app(self):
        app.config['TESTING'] = True
        self.assertEqual(app.testing, True)
        
    def test_post_basic(self):
        self.client = app.test_client()
        response = self.client.post('/') 
        self.assertEqual(response.status_code, 200)
    
    def test_sample_data_prediction(self): 
        self.client = app.test_client()
        test_data = {"ID": 752904, "Clump Thickness": 10, 
            "Uniformity of Cell Size": 1, "Uniformity of Cell Shape": 1, 
            "Marginal Adhesion": 1, "Single Epithelial Cell Size": 2,
            "Bare Nuclei": 10, "Bland Chromatin": 5, "Normal Nucleoli": 4, "Mitoses": 1 }
        expected_result = b'{"Confidence":0.98,"Prediction":"Benign"}'
        response = self.client.post(data = json.dumps(test_data),content_type='application/json')
        self.assertEqual(expected_result,response.data.strip())
        
    def test_missing_one_required_features(self): 
        self.client = app.test_client()
        test_data = {"Clump Thickness": 10, 
            "Uniformity of Cell Size": 1, "Uniformity of Cell Shape": 1, 
            "Marginal Adhesion": 1, "Single Epithelial Cell Size": 2,
            "Bare Nuclei": 10, "Bland Chromatin": 5, "Normal Nucleoli": 4, "Mitoses": 1 }
        expected_result = b'Error: please provide the following features: ID, Bland Chromatin, Bare Nuclei'
        response = self.client.post(data = json.dumps(test_data),content_type='application/json')
        self.assertEqual(expected_result,response.data.strip())
    
    def test_missing_both_interchangeable_features(self): 
        self.client = app.test_client()
        test_data = {"ID": 752904, "Clump Thickness": 10, 
            "Marginal Adhesion": 1, "Single Epithelial Cell Size": 2,
            "Bare Nuclei": 10, "Bland Chromatin": 5, "Normal Nucleoli": 4, "Mitoses": 1 }
        expected_result = b'Error: Need to provide either Uniformity of Cell Size or Uniformity of Cell Shape'
        response = self.client.post(data = json.dumps(test_data),content_type='application/json')
        self.assertEqual(expected_result,response.data.strip())
    
    def test_missing_one_interchangeable_features(self): 
        self.client = app.test_client()
        test_data = {"ID": 752904, "Clump Thickness": 10, 
            "Uniformity of Cell Shape": 1, 
            "Marginal Adhesion": 1, "Single Epithelial Cell Size": 2,
            "Bare Nuclei": 10, "Bland Chromatin": 5, "Normal Nucleoli": 4, "Mitoses": 1 }
        expected_result = b'{"Confidence":0.98,"Prediction":"Benign"}'
        response = self.client.post(data = json.dumps(test_data),content_type='application/json')
        self.assertEqual(expected_result,response.data.strip())
        
    def test_missing_all_optional_features(self): 
        self.client = app.test_client()
        test_data = {"ID": 752904,  
            "Uniformity of Cell Size": 1, "Uniformity of Cell Size": 2, 
            "Bare Nuclei": 10, "Bland Chromatin": 5 }
        expected_result = b'{"Confidence":0.74,"Prediction":"Malignant"}'
        response = self.client.post(data = json.dumps(test_data),content_type='application/json')
        self.assertEqual(expected_result,response.data.strip())
        
if __name__ == "__main__":
    unittest.main()