from bs4 import BeautifulSoup

def TextCollection(templatelist, soup, homeaway, generallen, gamecourselen, gamestatisticslen):
    team = soup.find('highlights').find(homeaway).find('team').text
    team2 = 'Verslag voor de achterban van ' + team
    general = templatelist[:generallen]
    gamecourse = templatelist[generallen:generallen+gamecourselen]
    gamestatistics = templatelist[generallen+gamecourselen:generallen+gamecourselen+gamestatisticslen]
    if generallen != generallen + gamecourselen:
        allstring = team2 + '\n' + general[0] + '\n' + ' '.join(general[1:]) + '\n' + ' '.join(gamecourse) + '\n' + ' '.join(gamestatistics)
    else:
        allstring = team2 + '\n' + general[0] + '\n' + ' '.join(general[1:]) + '\n' + ' '.join(gamestatistics)

    #Add a dictionary for the web implementation

    paragraphdict = {'title_' + team: general[0], 'general_' + team: ' '.join(general[1:]), 'gamecourse_' + team: ' '.join(gamecourse), 'gamestatistics_' + team: ' '.join(gamestatistics)}

    return allstring, paragraphdict