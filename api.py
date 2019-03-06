import json
import config
from flask import Flask, request, Response, jsonify, render_template
from flask_cors import CORS, cross_origin
# to make third part request to pubgAPI
import requests as R

from sklearn.externals import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)
##############3 DEFINE CONSTANTS #################
BASE_URL = 'https://api.pubg.com/shards/';

## Your pubg api key here
PUBG_API_KEY = config.api_key
## Your pubg model here
FILE_NAME = "model/lgb.pkl"

PLAYER_ID = 'jmjkh'
PLATFORM_NAME = ''
##################### HANDLE 404 ERROR #############################
@app.errorhandler(404)
@cross_origin()
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    #resp.headers['Access-Control-Allow-Origin'] = '*'
    #resp.headers['Content-Type'] = 'application/json'
    resp.status_code = 404

    return resp

##################### GET MATCHID FOR GIVEN PLAYER ##################

def getMatchIdOfPlayer(player_name):
    # call the pubgAPI to get player info
    global PLAYER_ID
    print(' ######################## get match id of player ######################## ')
    url = BASE_URL + PLATFORM_NAME + '/players?filter[playerNames]=' + player_name
    print('url= {}'.format(url))
    headers = {
        "Authorization" : PUBG_API_KEY,
        "Accept" : "application/vnd.api+json",
        "Accept-Encoding":"gzip"
    }
    r = R.get(url,headers=headers)

    if r.status_code == 200:
        print('data returned from pubg api')
        r = json.loads(r.text)
        data = r["data"][0]
        #print('id=',data['id'])
        PLAYER_ID = data['id']
        print('storing player id ',PLAYER_ID)
        matches = data['relationships']['matches']['data']
        # this will set the match_id as last id of the last match
        return matches
        #for match in matches:
        #    match_id = match['id']
        #return (player_id,match_id)
    else:
        return None

##################### GET PLAYER LIFETIME STATS ##################
def lifetimeStats():
    

##################### GET MATCH INFO FOR GIVEN MATCHID ##################

def getMatchInfoForPlayer(match_id):
    print(' ######################## get match info for player #################')
    url = BASE_URL + PLATFORM_NAME + '/matches/' + match_id
    print('get match info url = {}'.format(url))
    headers ={
        "Authorization" : PUBG_API_KEY,
        "Accept" : "application/vnd.api+json",
        "Accept-Encoding":"gzip"
    }
    match_info = {}

    r= R.get(url,headers=headers)
    print(r.status_code)
    if r.status_code == 200:
        r = json.loads(r.text)
        match_info['attributes'] = r["data"]["attributes"]
        data = r["included"]
        for obj in data:
            if (obj["type"] == "participant"):
                if (obj["attributes"]["stats"]["playerId"] == PLAYER_ID):
                    match_info['stats'] = obj["attributes"]["stats"]
                    return match_info
    else:
        return None

##################### PREPROCESS THE DATA BEFORE FEEDING TO MODEL ##################

def data_processing(match_info,match_type):
    drop_features = ['deathType', 'killPointsDelta', 'lastKillPoints', 'lastWinPoints', 'mostDamage', 'name', 'playerId', 'timeSurvived', 'winPointsDelta', 'winPlace']

    final_pos = match_info['stats']['winPlace']

    #create a copy to modify
    stats =  match_info['stats']
    # reomove extra keys in match_info
    for x in drop_features:
        if x in stats:
            del stats[x]


    #feature engineering

    return stats

##################### PREDICT THE OUTPUT ##################

def predict(stats):
    model = joblib.load(FILE_NAME)
    print('Model Loaded')
    model_columns = joblib.load('model/lgb_model_columns.pkl')
    print('Model Columns Loaded')
    ## generate X as dataframe from stats from PUBG api
    stats_df = pd.get_dummies(pd.DataFrame(stats,index=[0]))
    X = stats_df.reindex(columns = model_columns)
    print(X.columns)
    X.drop(['Id','matchId','groupId','matchType','winPlacePerc'],axis = 1, inplace=True)
    preds = model.predict(X)
    print('WINNING PROBABILITY:',preds,type(preds))
    if(preds>1):
         return 1
    return preds.astype(int)


@app.route("/",methods=['GET'])
@cross_origin()
def index():
    return render_template('index.html')


@app.route("/predict",methods=['POST','OPTIONS'])
@cross_origin()
def prediction():
    print('################ STARTING PREDICTION ###################')
    print('The request \n method: {} \n Type JSON: {} \n Content-Type: {}'.format(request.method,request.is_json,request.headers['Content-Type']))

    resp = {}

    if request.method == 'POST':
        match_id = request.get_json()
        print('HERE',PLAYER_ID,match_id)
        #get match information from match_id for player_id
        if match_id is not None and PLAYER_ID is not None:
            match_info = getMatchInfoForPlayer(match_id)
            print('returned match info',match_info)
            #print('match info=',match_info)
            match_type = match_info['attributes']['gameMode']
            ## performing pre-processing on match_info data
            stats = data_processing(match_info,match_type)
            #  TODO: use this match info to predict the outcome
            output = predict(stats)
            print(output,type(output))
            output = np.round(output,decimals=4)*100
            resp['matchInfo'] = match_info['attributes']
            resp['stats'] = stats
            print(output)
            resp['output'] = output.item()
            return jsonify(resp)
    else:
        return not_found()


@app.route("/",methods=['POST','OPTIONS'])
@cross_origin()
def api():
    global PLATFORM_NAME
    #print('The request \n method: {} \n Type JSON: {} \n Content-Type: {}'.format(request.method,request.is_json,request.headers['Content-Type']))
    if request.method == 'POST':
        json = request.get_json()
        PLATFORM_NAME = json['platform-name']
        player_name = json['player-name']
        print(PLATFORM_NAME,player_name)
        # get all matches id of the given player
        matches = getMatchIdOfPlayer(player_name)
        print('MATCHES => ',matches)
        return jsonify(matches)
    else:
        return not_found()

if __name__ == '__main__':
    app.run(debug=True,port=5000)
