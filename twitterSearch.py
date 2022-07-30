import datetime
import json
import os

import requests

bearer_token = os.environ.get("BEARER_TOKEN")
player = ""

# Gets time for search parameter
startTime = datetime.datetime.utcnow() - datetime.timedelta(hours=2)
startTime = startTime.isoformat() + "z"


search_url = "https://api.twitter.com/2/tweets/search/recent"

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
query_params = {'query': '','expansions': 'attachments.media_keys', 'media.fields': 'url'}
query_params['start_time'] = startTime

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(f"Response Status Code: {response.status_code}")
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def search(player: str):
    query_params["query"] = "from: championsqueue " + player
    json_response = connect_to_endpoint(search_url, query_params)
    if (json_response['meta']['result_count'] == 0):
        return("Game could not be found.")
    twitter_variable = json_response['includes']['media'][0]['url']
    return(json.dumps(twitter_variable, indent=4, sort_keys=True))
