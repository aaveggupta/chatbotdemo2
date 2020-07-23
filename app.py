import numpy as np
from flask import Flask, request, make_response
import json
import pickle
from flask_cors import cross_origin
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

app = Flask(__name__)
model = pickle.load(open('rf.pkl', 'rb'))

@app.route('/')
def hello():
    return 'Hello World'

# geting and sending response to dialogflow
@app.route('/webhook', methods=['POST'])
@cross_origin()
def webhook():

    req = request.get_json(silent=True, force=True)

    #print("Request:")
    #print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    #print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


# processing the request from dialogflow
def processRequest(req):

    #sessionID=req.get('responseId')
    result = req.get("queryResult")
    #user_says=result.get("queryText")
    #log.write_log(sessionID, "User Says: "+user_says)
    parameters = result.get("parameters")
    user_symptoms_list = parameters.get("Disease")
	
    symptom=np.zeros([526],dtype=float)
    finaldataset=pd.read_csv('finaldataset.csv')
    labels=finaldataset['prognosis']
    fdc=finaldataset
    fdc.drop('prognosis',axis=1,inplace=True)
    x_train,x_test,y_train,y_test=train_test_split(fdc,labels,test_size=0.25,random_state=20)
    model=MultinomialNB()
    model.fit(x_train,y_train)
    Alldiseases=model.classes_.tolist()
    
    indexes=[]
    for i in range(len(model_symptoms)):
        if model_symptoms[i] in user_symptoms:
            indexes.append(i)
    for i in indexes:
        symptom[i]=1
    top3=[]
    probab=model.predict_proba([symptom]).tolist()  
    for j in range(3):
        max=-10000000000
        h=0
        for i in range(len(probab[0])):
            if probab[0][i]>max:
                max=probab[0][i]
                h=i 
    k=[]
    k.append(Alldiseases[h])
    k.append(probab[0][h])
    top3.append(k)
    probab[0][h]=-1

    result=""
    for i in Top3diseasepred:
        result+="Probability of "+str(i[0])+"is "+"{:2.3f}".format((i[1]*100))+'%'+'\n'
       
    fulfillmentText= result
    #log.write_log(sessionID, "Bot Says: "+fulfillmentText)
    return {
            "fulfillmentText": fulfillmentText
     }
    #else:
    #    log.write_log(sessionID, "Bot Says: " + result.fulfillmentText)

if __name__ == '__main__':
    app.run()
#if __name__ == '__main__':
#    port = int(os.getenv('PORT', 5000))
#    print("Starting app on port %d" % port)
#    app.run(debug=False, port=port, host='0.0.0.0')
