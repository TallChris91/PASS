from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.internet import reactor, endpoints
from twisted.web.server import NOT_DONE_YET
from Templatefillers import json_date_as_datetime
import html 
import os

import time
import cgi
import json

from Governing_module import TopicWalk


class Generation(Resource):
	isLeaf = True

	def render_GET(self, request):
		gamefile = './JSONGameData/' + request.args[b"game"][0].decode("utf-8")
		request.setHeader('Content-Type', "application/json")
		returndict = {}
		try:
			templatetexthome, templatetextaway, templatetextneutral, templatedict, gamedata = TopicWalk(gamefile)
			home_team = gamedata['MatchInfo'][0]['c_HomeTeam']
			away_team = gamedata['MatchInfo'][0]['c_AwayTeam']
			home_goals = str(gamedata['MatchInfo'][0]['n_HomeGoals'])
			away_goals = str(gamedata['MatchInfo'][0]['n_AwayGoals'])
			msjsontime = gamedata['MatchInfo'][0]['d_DateLocal']
			date = json_date_as_datetime(msjsontime)
			league = gamedata['MatchInfo'][0]['c_Competition']
			stadium = gamedata['MatchInfo'][0]['c_Stadium']
		
			returndict =	{
				 "league": league,
				 "date": date.strftime('%x'),
				 "time": date.strftime("%H:%M"),
				 "stadium": stadium,
				 "teamhome": home_team,
				 "teamaway": away_team,
				 "teamhomegoals": home_goals,
				 "teamawaygoals": away_goals,
				 "jsonfile": gamefile
			}
			for generated_report in templatedict:
				returndict[generated_report+"_report"] = templatedict[generated_report]
			returndict["status"] = "OK"
		except Exception as err:
			print("Error generating report for "+gamefile)
			print(type(err))
			print(err.args)
			print(err)
			returndict["status"] = "ERROR"
			request.write(json.dumps(returndict).encode('utf-8'))
		return json.dumps(returndict).encode('utf-8')


class ChooseMatch(Resource):
	def getChild(self, name, request):
		return self
		
	def render_GET(self, request):
		available_matches = []
		
		for filename in os.listdir('./JSONGameData'):
			if filename.endswith(".json"):
				available_matches.append(filename)
		
		with open('HTML/listmatches.html', 'r') as htmlfile:
				response_page=htmlfile.read()
		
		matches_table = ""
		for matchfile in available_matches:
			with open("./JSONGameData/"+matchfile, 'rb') as f:
				gamedata = json.load(f)
			home_team = gamedata['MatchInfo'][0]['c_HomeTeam']
			away_team = gamedata['MatchInfo'][0]['c_AwayTeam']
			score = str(gamedata['MatchInfo'][0]['n_HomeGoals']) + "-" + str(gamedata['MatchInfo'][0]['n_AwayGoals'])
			msjsontime = gamedata['MatchInfo'][0]['d_DateLocal']
			date = json_date_as_datetime(msjsontime)
			link = '/generate?game='+matchfile
			matches_table = matches_table + '<tr>\n' + \
							'\t<td><a href="'+link+'">' + home_team +'</a></td>\n' + \
							'\t<td><a href="'+link+'">' + away_team +'</td>\n' + \
							'\t<td><a href="'+link+'">' + score +'</td>\n' + \
							'\t<td><a href="'+link+'">' + date.strftime('%x') + '</td>\n' + \
							'</tr>\n'
		response_page = response_page.replace("#CONTENTPLACEHOLDER#",matches_table)
		
		return response_page.encode('utf-8')
		
		
root = ChooseMatch()

generation = Generation()
root.putChild(b"generate", generation)

xml = File('./JSONGameData')
root.putChild(b"gamedata", xml)


choosematch = ChooseMatch()
root.putChild(b"choosematch", choosematch)



factory = Site(root)
endpoint = endpoints.TCP4ServerEndpoint(reactor, 8888)
endpoint.listen(factory)
print("DUTCH server listening on port 8888")
reactor.run()
