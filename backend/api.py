import json
import config
from flask import Flask, request, Response, jsonify
from flask_cors import CORS, cross_origin
# to make third part request to pubgAPI
import requests as R

app = Flask(__name__)
CORS(app)

BASE_URL = 'https://api.pubg.com/shards/';

## Your pubg api key here
PUBG_API_KEY = config.api_key

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


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
        data = r["included"]
        for obj in data:
            if (obj["type"] == "participant") and (obj["attributes"]["stats"]["playerId"] == player_id):
                match_info = obj["attributes"]["stats"]
                return match_info
    else:
        return None

@app.route("/",methods=['GET','POST'])
@cross_origin()
def api():
    #print('The request \n method: {} \n Type JSON: {} \n Content-Type: {}'.format(request.method,request.is_json,request.headers['Content-Type']))
    if request.method == "POST" and request.is_json:
        print('here {}'.format(request.json))
        data = request.json

        platform_name = data['platform-name']
        player_name = data['player-name']

        # get match id of the given player
        player_id, match_id = getMatchIdOfPlayer(platform_name,player_name)
        #print(player_id,match_id)

        #get match information from match_id for player_id
        if match_id is not None and player_id is not None:
            match_info = getMatchInfoForPlayer(platform_name,match_id,player_id)
            #print('match info=',match_info)


        #  TODO: use this match info to predict the outcome

        resp = jsonify(match_info)
        resp.status_code = 200
        return resp
    else:
        return not_found()

if __name__ == '__main__':
    app.run(debug=True,port=5000)
