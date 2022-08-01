# From https://riot-watcher.readthedocs.io/en/latest/
from riotwatcher import LolWatcher, ApiError
import os

api_key = os.environ.get("RIOT_API_KEY")

lol_watcher = LolWatcher(api_key)

queue = 'RANKED_SOLO_5x5'

def lowest(reg: str):
    try:
        challengers = lol_watcher.league.challenger_by_queue(reg, queue)['entries']
        min_lp = min(int(x['leaguePoints']) for x in challengers)
        for y in challengers:
            if int(y['leaguePoints']) == min_lp:
                name = y['summonerName']
        return(f"Lowest LP in Challenger in {reg} is {name} at {min_lp} LP")

    except ApiError as err:
        if err.response.status_code == 429:
            return('We should retry in {} seconds.'.format(err.headers['Retry-After']))
        elif err.response.status_code == 404:
            return('404 Error')
        else:
            raise
