from Topic_collection_module import TopicCollection
import xlrd
from bs4 import BeautifulSoup
import re
import sys

def ArrangeDatabase(file):
    #Determine the database of which the system is going to use the templates.
    #The database is determined by whether the team won, tied or lost
    soup = BeautifulSoup(open(file, 'rb'), "lxml")
    windb, tiedb, lossdb, neutraldb = ('Databases/Templates GoalgetterWin.xlsx', 'Databases/Templates GoalgetterTie.xlsx', 'Databases/Templates GoalgetterLoss.xlsx', 'Databases/Templates GoalgetterNeutral.xlsx')
    #Get all goals scored by the home team and the away team to determine if and which one has won
    homegoals = int(soup.find('highlights').find('home').find('finalgoals').text)
    awaygoals = int(soup.find('highlights').find('away').find('finalgoals').text)
    #More homegoals means the home team has won
    if homegoals > awaygoals:
        #So the hometeam uses the win database and the away team the loss database
        homedb = windb
        awaydb = lossdb
    if homegoals < awaygoals:
        homedb = lossdb
        awaydb = windb
    if homegoals == awaygoals:
        homedb = tiedb
        awaydb = tiedb
    return (homedb, 'home'), (awaydb, 'away'), (neutraldb, 'neutral')

def ConvertWorkbook(db):
    workbook = xlrd.open_workbook(db)
    worksheets = workbook.sheet_names()[0]
    legend = []
    templates = []
    # Open the excel file
    worksheet = workbook.sheet_by_name(worksheets)
    #Get all the columns
    for col in range(worksheet.ncols):
        #Append the first value to get the type of template
        legend.append(worksheet.cell_value(0, col))
        #Append the non-empty values after the first value to get the templates
        newcol = worksheet.col_values(col)
        temp = []
        for idx, val in enumerate(newcol):
            if (idx != 0) and (val != ''):
                temp.append(val)
        templates.append(temp)

    return legend, templates

def GeneralTemplates(type, homelegend, hometemplates, awaylegend, awaytemplates, neutrallegend, neutraltemplates):
    #Collect all templates (and categories) for titles
    if type == 'title':
        possiblelegendhome = []
        possibletemplateshome = []
        possiblelegendaway = []
        possibletemplatesaway = []
        possiblelegendneutral = []
        possibletemplatesneutral = []
        #For the home report first
        for idx, val in enumerate(homelegend):
            if re.search(r'^Title\s', val):
                possiblelegendhome.append(homelegend[idx])
                possibletemplateshome.append(hometemplates[idx])
        #And then for the away report
        for idx, val in enumerate(awaylegend):
            if re.search(r'^Title\s', val):
                possiblelegendaway.append(awaylegend[idx])
                possibletemplatesaway.append(awaytemplates[idx])
        # And then for the neutral report
        for idx, val in enumerate(neutrallegend):
            if re.search(r'^Title\s', val):
                possiblelegendneutral.append(neutrallegend[idx])
                possibletemplatesneutral.append(neutraltemplates[idx])
        return possiblelegendhome, possibletemplateshome, possiblelegendaway, possibletemplatesaway, possiblelegendneutral, possibletemplatesneutral
    # Collect all templates (and categories) for the win/tie/loss sentence
    if type == 'general':
        possiblelegendhome = []
        possibletemplateshome = []
        possiblelegendaway = []
        possibletemplatesaway = []
        possiblelegendneutral = []
        possibletemplatesneutral = []
        # For the home report first
        for idx, val in enumerate(homelegend):
            if (re.search(r'^General\,\swin\/tie\/loss', val)) and not (re.search(r'^General\,\swin\/tie\/loss\s\(final\sscore\)', val)):
                possiblelegendhome.append(homelegend[idx])
                possibletemplateshome.append(hometemplates[idx])
        # And then for the away report
        for idx, val in enumerate(awaylegend):
            if (re.search(r'^General\,\swin\/tie\/loss', val)) and not (re.search(r'^General\,\swin\/tie\/loss\s\(final\sscore\)', val)):
                possiblelegendaway.append(awaylegend[idx])
                possibletemplatesaway.append(awaytemplates[idx])
        #And then for the neutral report
        for idx, val in enumerate(neutrallegend):
            if (re.search(r'^General\,\swin\/tie\/loss', val)) and not (re.search(r'^General\,\swin\/tie\/loss\s\(final\sscore\)', val)):
                possiblelegendneutral.append(neutrallegend[idx])
                possibletemplatesneutral.append(neutraltemplates[idx])
        return possiblelegendhome, possibletemplateshome, possiblelegendaway, possibletemplatesaway, possiblelegendneutral, possibletemplatesneutral
    # Collect all templates (and categories) for the final score sentence
    if type == 'final_score':
        possiblelegendhome = []
        possibletemplateshome = []
        possiblelegendaway = []
        possibletemplatesaway = []
        possiblelegendneutral = []
        possibletemplatesneutral = []
        # For the home report first
        for idx, val in enumerate(homelegend):
            if re.search(r'^General\,\swin\/tie\/loss\s\(final\sscore\)', val):
                possiblelegendhome.append(homelegend[idx])
                possibletemplateshome.append(hometemplates[idx])
        # And then for the away report
        for idx, val in enumerate(awaylegend):
            if re.search(r'^General\,\swin\/tie\/loss\s\(final\sscore\)', val):
                possiblelegendaway.append(awaylegend[idx])
                possibletemplatesaway.append(awaytemplates[idx])
        # And then for the neutral report
        for idx, val in enumerate(neutrallegend):
            if re.search(r'^General\,\swin\/tie\/loss\s\(final\sscore\)', val):
                possiblelegendneutral.append(neutrallegend[idx])
                possibletemplatesneutral.append(neutraltemplates[idx])
        return possiblelegendhome, possibletemplateshome, possiblelegendaway, possibletemplatesaway, possiblelegendneutral, possibletemplatesneutral

def GameCourseTemplates(gamecoursetopic, homelegend, hometemplates, awaylegend, awaytemplates, neutrallegend, neutraltemplates):
    #Four types of events are reported on: regular goals, missed penalties, own goals, and penalty goals, furthermore all these topics can be
    # reported on from the perspective in favor of the focus team or against the focus team, so 4x2 variations total

    def TemplateFilter(query1, query2, query3):
        possiblelegendhome = []
        possibletemplateshome = []
        possiblelegendaway = []
        possibletemplatesaway = []
        possiblelegendneutral = []
        possibletemplatesneutral = []
        # Templates for event from the perspective of the home team
        for idx, val in enumerate(homelegend):
            if re.search(query1, val):
                possiblelegendhome.append(homelegend[idx])
                possibletemplateshome.append(hometemplates[idx])
        # Templates for event from the perspective of the away team
        for idx, val in enumerate(awaylegend):
            if re.search(query2, val):
                possiblelegendaway.append(awaylegend[idx])
                possibletemplatesaway.append(awaytemplates[idx])
        # Templates for event from the perspective of the away team
        for idx, val in enumerate(neutrallegend):
            if re.search(query3, val):
                possiblelegendneutral.append(neutrallegend[idx])
                possibletemplatesneutral.append(neutraltemplates[idx])
        return possiblelegendhome, possibletemplateshome, possiblelegendaway, possibletemplatesaway, possiblelegendneutral, possibletemplatesneutral

    #First, let's work with a goal for the home team (goal for the focus team if the focus team is the home team)
    if (gamecoursetopic['event'] == 'regular goal') and (gamecoursetopic['team'] == 'home'):
        return TemplateFilter(r'^Game\scourse\,\sregular\sgoal\sfocus\steam', r'^Game\scourse\,\sregular\sgoal\sother\steam', r'^Game\scourse\,\sregular\sgoal')
    # Second, let's work with a goal for the away team (goal against the focus team if the focus team is the home team)
    if (gamecoursetopic['event'] == 'regular goal') and (gamecoursetopic['team'] == 'away'):
        return TemplateFilter(r'^Game\scourse\,\sregular\sgoal\sother\steam', r'^Game\scourse\,\sregular\sgoal\sfocus\steam', r'^Game\scourse\,\sregular\sgoal')
    #Onto the own goals, an own goal scored by a player of the home team is in favor of the away team, so keep that in mind...
    if (gamecoursetopic['event'] == 'own goal') and (gamecoursetopic['team'] == 'home'):
        return TemplateFilter(r'^Game\scourse\,\sown goal\sfocus\steam', r'^Game\scourse\,\sown goal\sother\steam', r'^Game\scourse\,\sown goal')
    #Own goals scored by a player of the away team
    if (gamecoursetopic['event'] == 'own goal') and (gamecoursetopic['team'] == 'away'):
        return TemplateFilter(r'^Game\scourse\,\sown goal\sother\steam', r'^Game\scourse\,\sown goal\sfocus\steam', r'^Game\scourse\,\sown goal')
    # Penalty goals for the home team (penalty goal for the focus team if the focus team is the home team)
    if (gamecoursetopic['event'] == 'penalty goal') and (gamecoursetopic['team'] == 'home'):
        return TemplateFilter(r'^Game\scourse\,\sgoal\sfrom\spenalty\sfocus\steam', r'^Game\scourse\,\sgoal\sfrom\spenalty\sother\steam', r'^Game\scourse\,\sgoal\sfrom\spenalty')
    # Penalty goals for the away team (penalty goal for the focus team if the focus team is the away team)
    if (gamecoursetopic['event'] == 'penalty goal') and (gamecoursetopic['team'] == 'away'):
        return TemplateFilter(r'^Game\scourse\,\sgoal\sfrom\spenalty\sother\steam', r'^Game\scourse\,\sgoal\sfrom\spenalty\sfocus\steam', r'^Game\scourse\,\sgoal\sfrom\spenalty')
    # Penalty misses for the home team (penalty miss for the focus team if the focus team is the home team)
    if (gamecoursetopic['event'] == 'missed penalty') and (gamecoursetopic['team'] == 'home'):
        return TemplateFilter(r'^Game\scourse\,\spenalty\smiss\sfocus\steam', r'^Game\scourse\,\spenalty\smiss\sother\steam', r'^Game\scourse\,\spenalty\smiss')
    # Penalty misses for the away team (penalty miss for the focus team if the focus team is the away team)
    if (gamecoursetopic['event'] == 'missed penalty') and (gamecoursetopic['team'] == 'away'):
        return TemplateFilter(r'^Game\scourse\,\spenalty\smiss\sother\steam', r'^Game\scourse\,\spenalty\smiss\sfocus\steam', r'^Game\scourse\,\spenalty\smiss')

def GameStatisticsTemplates(gamestatisticstopic, homelegend, hometemplates, awaylegend, awaytemplates, neutrallegend, neutraltemplates):
    #Three types of events are reported on: yellow cards, twice yellow, direct red, no query difference between teams
    def TemplateFilter(query1):
        possiblelegendhome = []
        possibletemplateshome = []
        possiblelegendaway = []
        possibletemplatesaway = []
        possiblelegendneutral = []
        possibletemplatesneutral = []
        # Templates for event from the perspective of the home team
        for idx, val in enumerate(homelegend):
            if re.search(query1, val):
                possiblelegendhome.append(homelegend[idx])
                possibletemplateshome.append(hometemplates[idx])
        # Templates for event from the perspective of the away team
        for idx, val in enumerate(awaylegend):
            if re.search(query1, val):
                possiblelegendaway.append(awaylegend[idx])
                possibletemplatesaway.append(awaytemplates[idx])
        # Templates for the neutral perspective
        for idx, val in enumerate(neutrallegend):
            if re.search(query1, val):
                possiblelegendneutral.append(neutrallegend[idx])
                possibletemplatesneutral.append(neutraltemplates[idx])
        return possiblelegendhome, possibletemplateshome, possiblelegendaway, possibletemplatesaway, possiblelegendneutral, possibletemplatesneutral
    if gamestatisticstopic['event'] == None:
        return TemplateFilter(r'Game\sstatistics\,\syellow\scards\s\(none\)')
    if gamestatisticstopic['event'] == 'yellow card':
        return TemplateFilter(r'^Game\sstatistics\,\syellow\scards')
    if gamestatisticstopic['event'] == 'twice yellow':
        return TemplateFilter(r'^Game\sstatistics\,\stwice\syellow')
    if gamestatisticstopic['event'] == 'red card':
        return TemplateFilter(r'^Game\sstatistics\,\sred\scards')