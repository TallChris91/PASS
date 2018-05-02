from bs4 import BeautifulSoup

def InfoDict(file):
    with open(file, 'rb') as f:
        soup = BeautifulSoup(f, "lxml")
    league = soup.find('highlights').find('league').text
    date = soup.find('highlights').find('startdate').text
    finalscore = soup.find('highlights').find('fulltimescore').text
    hometeam = soup.find('highlights').find('home').find('team').text
    awayteam = soup.find('highlights').find('away').find('team').text

    infodict = {'league': league, 'MatchDate': date, 'FinalScore': finalscore, 'HomeTeam': hometeam, 'AwayTeam': awayteam}
    return infodict