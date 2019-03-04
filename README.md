#Backend

- [x] Develop a Flask API
- [x] Access the PUBG API from back-end to gather data for playerID/playerName passed.
- [x] Predict the output using the checkpoint file
- [ ] Enhance the model using Xgboost
- [ ] Use DBSCAN Clustering method

Check out the PUBG API [DOC](https://documentation.pubg.com/en/players-endpoint.html)
**Note**: My checkpoint file is named `randomForestModel.pkl`, however you can use your own model as well by replacing the `FILE_NAME` variable in `api.py` and upload the `FILE_NAME.pkl` file in the root directory

## Install and RUN

* To Install

`pip install requiremnets.txt`

* To RUN

`cd (folder-path)`
`python api.py`

Now the server is running on http://localhost:5000

## CHANGES IN CODE

* Create your own api key from this [link](#)
* Create a file called `config.py` in this folder
* Store your api key as follows
```python
api_key = "YOUR_KEY"
```


### Resource

<hr>

* [Using Cors](https://www.html5rocks.com/en/tutorials/cors/)
