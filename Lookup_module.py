from Topic_collection_module import TopicCollection
import xlrd
import re
import json
import sys

def ArrangeDatabase(jsongamedata):
    #Determine the database of which the system is going to use the templates.
    #The database is determined by whether the team won, tied or lost
    windb, tiedb, lossdb, neutraldb = ('Databases/TemplatesWin.json', 'Databases/TemplatesTie.json', 'Databases/TemplatesLoss.json', 'Databases/TemplatesNeutral.json')
    homegoals = jsongamedata['MatchInfo'][0]['n_HomeGoals']
    awaygoals = jsongamedata['MatchInfo'][0]['n_AwayGoals']
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

def ReadTemplates(db):
	with open(db, 'rb') as f:
		templatedata = json.load(f)
	return list(templatedata.keys()),list(templatedata.values())
	
def GeneralTemplates(type, legend, templates):
    #Collect all templates (and categories) for titles
    if type == 'title':
        possiblelegend = []
        possibletemplates = []
        for idx, val in enumerate(legend):
            if re.search(r'^Title\s', val):
                possiblelegend.append(legend[idx])
                possibletemplates.append(templates[idx])
        return possiblelegend, possibletemplates
    # Collect all templates (and categories) for the win/tie/loss sentence
    if type == 'general':
        possiblelegend = []
        possibletemplates = []
        for idx, val in enumerate(legend):
            if (re.search(r'^General\,\swin\/tie\/loss', val)) and not (re.search(r'^General\,\swin\/tie\/loss\s\(final\sscore\)', val)):
                possiblelegend.append(legend[idx])
                possibletemplates.append(templates[idx])
        return possiblelegend, possibletemplates
    # Collect all templates (and categories) for the final score sentence
    if type == 'final_score':
        possiblelegend = []
        possibletemplates = []
        for idx, val in enumerate(legend):
            if re.search(r'^General\,\swin\/tie\/loss\s\(final\sscore\)', val):
                possiblelegend.append(legend[idx])
                possibletemplates.append(templates[idx])
        return possiblelegend, possibletemplates

def GameCourseTemplates(gamecoursetopic, legend, templates, reporttarget):
    #Four types of events are reported on: regular goals, missed penalties, own goals, and penalty goals, furthermore all these topics can be
    # reported on from the perspective in favor of the focus team or against the focus team, so 4x2 variations total

    def TemplateFilter(query1, query2, query3):
        possiblelegend = []
        possibletemplates = []
        if reporttarget=='home':
        	query = query1
        elif reporttarget=='away':
        	query = query2
        else:
        	query = query3
        # Templates for event from the perspective of the current team
        for idx, val in enumerate(legend):
            if re.search(query, val):
                possiblelegend.append(legend[idx])
                possibletemplates.append(templates[idx])
        return possiblelegend, possibletemplates

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

def GameStatisticsTemplates(gamestatisticstopic, legend, templates):
    #Three types of events are reported on: yellow cards, twice yellow, direct red, no query difference between teams
    def TemplateFilter(query1):
        possiblelegend = []
        possibletemplates = []
        # Templates for event from the perspective of the current team
        for idx, val in enumerate(legend):
            if re.search(query1, val):
                possiblelegend.append(legend[idx])
                possibletemplates.append(templates[idx])
        return possiblelegend, possibletemplates

    if gamestatisticstopic['event'] == None:
        return TemplateFilter(r'Game\sstatistics\,\syellow\scards\s\(none\)')
    if gamestatisticstopic['event'] == 'yellow card':
        return TemplateFilter(r'^Game\sstatistics\,\syellow\scards')
    if gamestatisticstopic['event'] == 'twice yellow':
        return TemplateFilter(r'^Game\sstatistics\,\stwice\syellow')
    if gamestatisticstopic['event'] == 'red card':
        return TemplateFilter(r'^Game\sstatistics\,\sred\scards')