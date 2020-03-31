from flask import Flask, request, jsonify
from flask_restplus import Api
import numpy as np
import pandas as pd
import joblib
import json

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
    if request.method == 'POST':
        # setup parameters 
        Clump_Thickness = 0; Marginal_Adhesion = 0; S_E_C_S = 0; 
        Normal_Nucleoli= 0; Mitoses = 0; U_C_Size = 0; U_C_Shape =0;
        # the following lines handle input exceptions
        try:
            user_query = request.get_json(force=True)
            ID = user_query['ID']
            Bland_Chromatin = user_query['Bland Chromatin']
            Bare_Nuclei= user_query['Bare Nuclei']
            # check either 'Uniformity of Cell Size' or 'Uniformity of Cell Shape' has been provided
            try:
                U_C_Size  = user_query['Uniformity of Cell Size']
            except:
                try:
                    U_C_Shape  = user_query['Uniformity of Cell Shape']
                except:
                    return 'Need to provide either Uniformity of Cell Size or Uniformity of Cell Shape'
        except:
            return 'Insufficient data. Please refer to README for example data format.'
        try:
            # parse out all the none-required data.
            Clump_Thickness = user_query['Clump Thickness'] 
            Marginal_Adhesion = user_query['Marginal Adhesion'] 
            S_E_C_S = user_query['Single Epithelial Cell Size']
            Normal_Nucleoli = user_query['Normal Nucleoli']
            Mitoses = user_query['Mitoses']
        except:  
            pass
            
        # convert input data into model input
        if U_C_Size:
            Uniformity = U_C_Size
        else:
            Uniformity = U_C_Shape        
        input_para= np.array([Clump_Thickness, Marginal_Adhesion, S_E_C_S, Bare_Nuclei, Bland_Chromatin, Normal_Nucleoli, Mitoses, Uniformity]).reshape(1, -1)
        # make a prediction
        prediction = classifier.predict(input_para)
        confidence = classifier.predict_proba(input_para)[int(prediction)]
        
        # format output
        output_result =  {}
        print(confidence)
        output_result['Prediction']= ['Benign','Malignant'][int(prediction[0])]
        output_result['Confidence'] = round(confidence[int(prediction[0])],2)
        
        # save, name file after ID      
        out_path = 'Output/predictions_'+str(ID)+'.json'
        json.dump(output_result, open(out_path, 'w'))
        return output_result
    else:
        return('Error: Wrong input format. Please refer to README for sample query format.')
        
if __name__ == '__main__':
    print('Loading the classifier model...')
    classifier = load_model() # load the model first
    app.run(debug=True, host = '127.0.0.1', port='5000')