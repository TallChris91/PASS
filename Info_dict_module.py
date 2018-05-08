from bs4 import BeautifulSoup
from datetime import datetime

def InfoDict(file):
    with open(file, 'rb') as f:
        soup = BeautifulSoup(f, "lxml")
    league = soup.find('highlights').find('league').text
    date = soup.find('highlights').find('startdate').text
    date_object = datetime.strptime(date, '%B %d, %Y')
    date = date_object.isoformat()

    finalscore = soup.find('highlights').find('fulltimescore').text
    hometeam = soup.find('highlights').find('home').find('team').text
    awayteam = soup.find('highlights').find('away').find('team').text

    infodict = {'league': league, 'match_date': date, 'final_score': finalscore, 'home_team': hometeam, 'away_team': awayteam}
    return infodict