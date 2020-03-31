from flask import Flask, request, jsonify
from flask_restplus import Api
import numpy as np
import pandas as pd
import joblib
import json
import argparse

app = Flask(__name__)
api = Api(
    app, 
    version="v1.0",
    title="BreastCancerDetector",
    description = 'Predict malignancy based on features of biopsied breast cells')
    
def load_model():
    # load model & vectorizer
    classifier  = joblib.load('Model/clf_1.sav')
    return classifier
    
@app.route('/', methods = ['POST'])       
def result():
    # check request format
    if request.method != 'POST':
        return('Error: Wrong input format. Please refer to README for sample query format.')
        
    # setup features 
    requiredFeatures = ['ID', 'Bland Chromatin', 'Bare Nuclei']
    interchangeableFeatures = ['Uniformity of Cell Size', 'Uniformity of Cell Shape']
    optionalFeatures = ['Clump Thickness', 'Marginal Adhesion', 
                        'Single Epithelial Cell Size', 'Normal Nucleoli', 'Mitoses']
    cellFeatures = dict.fromkeys(requiredFeatures + optionalFeatures + interchangeableFeatures, 0)
    
    # check format of the input query
    try: 
        user_query = request.get_json(force=True)
    except: 
        return 'Error : wrong data format. Please refer to README for example data format.'
    
    # check for requiredFeatures    
    for feature in requiredFeatures: 
        try:  
            cellFeatures[feature]  = user_query[feature]
        except:  
            return 'Error: please provide the following features: ID, Bland Chromatin, Bare Nuclei'
    
    # check if the at least one of the two interchangeableFeatures are present
    present = 0 
    for feature in interchangeableFeatures:
        if feature in user_query.keys():
            cellFeatures[feature] = user_query[feature]
            present +=1
    if not present: 
        return 'Error: Need to provide either Uniformity of Cell Size or Uniformity of Cell Shape'
     
    # check optional features 
    for feature in optionalFeatures: 
        try:
            cellFeatures[feature] =user_query[feature]
        except:
            pass
           
    # convert input data into model input
    orderedList = ['Clump Thickness', 'Marginal Adhesion','Single Epithelial Cell Size', 'Bare Nuclei',
                    'Bland Chromatin', 'Normal Nucleoli', 'Mitoses']  
    if user_query['Uniformity of Cell Size']:
        orderedList.append('Uniformity of Cell Size')
    else:
        orderedList.append('Uniformity of Cell Shape')
    input_para= np.array([cellFeatures[i] for i in orderedList]).reshape(1, -1)
    
    # make a prediction
    prediction = int(classifier.predict(input_para))
    confidence = classifier.predict_proba(input_para)[prediction]
    print(prediction)
    
    # format output
    output_result =  {}
    output_result['Prediction']= ['Benign','Malignant'][prediction]
    output_result['Confidence'] = round(confidence[prediction],2)
    
    # save, name file after ID      
    out_path = 'Output/predictions_'+str(cellFeatures['ID'])+'.json'
    json.dump(output_result, open(out_path, 'w'))
    return output_result
    
    
if __name__ == '__main__':
    # make it optional to define the port
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", action="store", default="5000")
    args = parser.parse_args()
    port = int(args.port)
    
    print('Loading the classifier model...')
    classifier = load_model() # load the model first
    app.run(debug=True, host = '127.0.0.1', port=port)