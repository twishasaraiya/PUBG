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

FILE_NAME = "model/lgb.pkl"

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

def getMatchIdOfPlayer(platform_name,player_name):
    # call the pubgAPI to get player info
    url = BASE_URL + platform_name + '/players?filter[playerNames]=' + player_name
    print('url= {}'.format(url))
    headers = {
        "Authorization" : PUBG_API_KEY,
        "Accept" : "application/vnd.api+json",
        "Accept-Encoding":"gzip"
    }
    r = R.get(url,headers=headers)

    if r.status_code == 200:
        r = json.loads(r.text)
        data = r["data"][0]
        #print('id=',data['id'])
        player_id = data['id']
        matches = data['relationships']['matches']['data']
        # this will set the match_id as last id of the last match
        for match in matches:
            match_id = match['id']
        return (player_id,match_id)
    else:
        return None


##################### GET MATCH INFO FOR GIVEN MATCHID ##################

def getMatchInfoForPlayer(platform_name,match_id,player_id):
    url = BASE_URL + platform_name + '/matches/' + match_id
    print('get match info url = {}'.format(url))
    headers ={
        "Authorization" : PUBG_API_KEY,
        "Accept" : "application/vnd.api+json",
        "Accept-Encoding":"gzip"
    }
    r= R.get(url,headers=headers)

    if r.status_code == 200:
        r = json.loads(r.text)
        match_type = r["data"]["attributes"]["gameMode"]
        data = r["included"]
        for obj in data:
            if (obj["type"] == "participant") and (obj["attributes"]["stats"]["playerId"] == player_id):
                match_info = obj["attributes"]["stats"]
                return match_info, match_type
    else:
        return None

##################### PREPROCESS THE DATA BEFORE FEEDING TO MODEL ##################

def data_processing(match_info,match_type):
    drop_features = ['deathType', 'killPointsDelta', 'lastKillPoints', 'lastWinPoints', 'mostDamage', 'name', 'playerId', 'timeSurvived', 'winPointsDelta', 'winPlace']

    final_pos = match_info['winPlace']

    #create a copy to modify
    stats =  match_info
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
    X = stats_df.reindex(columns = model_columns, fill_value = 0)
    X.drop(['Id','matchId','groupId','matchType','winPlacePerc'],axis = 1, inplace=True)
    preds = model.predict(X)
    print('WINNING PROBABILITY:',preds)
    return preds


@app.route("/",methods=['GET'])
@cross_origin()
def index():
    return render_template('index.html')


@app.route("/",methods=['POST'])
@cross_origin()
def api():
    print('The request \n method: {} \n Type JSON: {} \n Content-Type: {}'.format(request.method,request.is_json,request.headers['Content-Type']))
    if request.method == 'POST':
        print('HERE',request.form)
        data = request.form
        platform_name = 'xbox'
        player_name = data['player-name']
        print(platform_name,player_name)
        # get match id of the given player
        player_id, match_id = getMatchIdOfPlayer(platform_name,player_name)
        print(player_id,match_id)

        #get match information from match_id for player_id
        if match_id is not None and player_id is not None:
            match_info, match_type = getMatchInfoForPlayer(platform_name,match_id,player_id)
            #print('match info=',match_info)

        ## performing pre-processing on match_info data
        stats = data_processing(match_info,match_type)
        #  TODO: use this match info to predict the outcome
        output = predict(stats)
        print('Returning Response')
        #resp = jsonify(winning_prob = output[0])
        #resp.headers['Content-Type'] = 'application/json'
        #resp.status_code = 200

        output = np.round(output,decimals=4)*100
        return render_template('index.html',stats= match_info, prediction=output[0])
    else:
        return not_found()

if __name__ == '__main__':
    app.run(debug=True,port=5000)
