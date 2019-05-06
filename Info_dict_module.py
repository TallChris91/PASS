from datetime import datetime
from Templatefillers import json_date_as_datetime

def InfoDict(jsongamedata):
    league = jsongamedata['MatchInfo'][0]['c_Competition']
    msjsontime = jsongamedata['MatchInfo'][0]['d_DateLocal']
    date = json_date_as_datetime(msjsontime) 
    finalscore = jsongamedata['MatchInfo'][0]['c_Score']
    hometeam = jsongamedata['MatchInfo'][0]['c_HomeTeam']
    awayteam = jsongamedata['MatchInfo'][0]['c_AwayTeam']

    infodict = {'league': league, 'match_date': date, 'final_score': finalscore, 'home_team': hometeam, 'away_team': awayteam}
    return infodict