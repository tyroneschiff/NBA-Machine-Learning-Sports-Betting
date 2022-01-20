import argparse
import requests
from datetime import datetime
import pytz


# Obtain the api key that was passed in from the command line
#parser = argparse.ArgumentParser(description='Sample V4')
#parser.add_argument('--api-key', type=str, default='')
#args = parser.parse_args()


# An api key is emailed to you when you sign up to a plan
# Get a free API key at https://api.the-odds-api.com/
API_KEY = 'e3ec04a4dbabcf0a1fb4b6fd661c7f9b'

SPORT = 'basketball_nba' # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports

REGIONS = 'us' # uk | us | eu | au. Multiple can be specified if comma delimited

MARKETS = 'h2h,totals' # h2h | spreads | totals. Multiple can be specified if comma delimited

ODDS_FORMAT = 'american' # decimal | american

DATE_FORMAT = 'unix' # iso | unix

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
# First get a list of in-season sports
#   The sport 'key' from the response can be used to get odds in the next request
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

sports_response = requests.get('https://api.the-odds-api.com/v4/sports', params={
    'api_key': API_KEY
})


if sports_response.status_code != 200:
    print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')

else:
    print('List of in season sports:', sports_response.json())



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
# Now get a list of live & upcoming games for the sport you want, along with odds for different bookmakers
# This will deduct from the usage quota
# The usage quota cost = [number of markets specified] x [number of regions specified]
# For examples of usage quota costs, see https://the-odds-api.com/liveapi/guides/v4/#usage-quota-costs
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def get_odds_response():
    odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds', params={
        'api_key': API_KEY,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': DATE_FORMAT,
        'sport': SPORT,
    })
    return odds_response

def format_odds(odds_response):
    odds_json = odds_response.json()
    print('Number of events:', len(odds_json))
    money_line_odds = {}
    ou_odds = {}
    for i in odds_json:
        commence_time = i['commence_time']
        utc_dt = datetime.utcfromtimestamp(commence_time).replace(tzinfo=pytz.utc)
        tz = pytz.timezone('America/New_York')
        dt = utc_dt.astimezone(tz)
        game_date = dt.strftime('%Y-%m-%d')
        now_without_timezone = datetime.now().replace(tzinfo=pytz.utc)
        now_with_timezone = now_without_timezone.astimezone(tz)
        todays_date = now_with_timezone.strftime('%Y-%m-%d')
        if todays_date == game_date:
            home_team = i['home_team']
            away_team = i['away_team']
            for x in i['bookmakers']:
                if x['key'] == 'draftkings':
                    money_line = x['markets'][0]
                    ou = x['markets'][1]
                    name1 = money_line['outcomes'][0]['name']
                    price1 = money_line['outcomes'][0]['price']
                    name2 = money_line['outcomes'][1]['name']
                    price2 = money_line['outcomes'][1]['price']
                    if name1 == home_team:
                        ht = name1
                        at = name2
                        ht_odds = price1
                        at_odds = price2
                    if name2 == home_team:
                        ht = name2
                        at = name1
                        ht_odds = price2
                        at_odds = price1
                    ou_points = ou['outcomes'][0]['point']
                    ou_name1 = ou['outcomes'][0]['name']
                    ou_price1 = ou['outcomes'][0]['price']
                    ou_name2 = ou['outcomes'][1]['name']
                    ou_price2 = ou['outcomes'][1]['price']
                    if ht == 'Los Angeles Clippers':
                        ht = 'LA Clippers'
                    if at == 'Los Angeles Clippers':
                        at = 'LA Clippers'
                    money_line_odds[ht] = ht_odds
                    money_line_odds[at] = at_odds
                    ou_odds[f'{ht}{at}'] = ou_points
    return money_line_odds, ou_odds

odds_response = get_odds_response()

if odds_response.status_code != 200:
    print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')

else:
    format_odds(odds_response)
    # Check the usage quota
    print('Remaining requests', odds_response.headers['x-requests-remaining'])
    print('Used requests', odds_response.headers['x-requests-used'])
