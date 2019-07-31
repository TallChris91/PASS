from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.internet import reactor, endpoints
from twisted.web.server import NOT_DONE_YET

	
from xml.etree.ElementTree import ElementTree
import os
import fnmatch
import time
import cgi

import pdb

from Governing_module import TopicWalk


team_to_abbrev = {'ADO_Den_Haag' : 'ADO',
'AZ' : 'AZ',
'Achilles_29' : 'ACH',
'Ajax' : 'AX',
'Ajax_II' : 'JAX',
'Almere_City' : 'AC',
'Cambuur' : 'SCC',
'De_Graafschap' : 'DG',
'Den_Bosch' : 'DB',
'Dordrecht' : 'FCD',
'Eindhoven' : 'FCE',
'Emmen' : 'FCEM',
'Excelsior' : 'EX',
'Feyenoord' : 'FN',
'Fortuna_Sittard' : 'FS',
'Go_Ahead_Eagles' : 'GAE',
'Groningen' : 'FCG',
'Heerenveen' : 'SCH',
'Helmond_Sport' : 'HS',
'Heracles' : 'HA',
'MVV' : 'MVV',
'NAC_Breda' : 'NAC',
'NEC' : 'NEC',
'Oss' : 'FCO',
'PEC_Zwolle' : 'PEC',
'PSV' : 'PSV',
'PSV_II' : 'JPSV',
'RKC_Waalwijk' : 'RKC',
'Roda_JC' : 'RJC',
'Sparta_Rotterdam' : 'SR',
'Telstar' : 'T',
'Twente' : 'FCT',
'Utrecht' : 'FCU',
'VVV' : 'VVV',
'Vitesse' : 'V',
'Volendam' : 'FCV',
'Willem_II' : 'WII'}



class Generation(Resource):
	isLeaf = True
	def getFileName(self,POSTarg1,POSTarg2):
		date = "";
		self.teamhome = POSTarg1
		self.teamaway = POSTarg2
		if ("(" in POSTarg2):
			fields = POSTarg2.split("_")
			self.teamaway = fields[0]
			date = fields[1]
			date = date[1:len(date)-1].replace("/", "")
			return(team_to_abbrev[self.teamhome]+"_"+team_to_abbrev[self.teamaway]+"_"+date+"_goal.xml")
		else:
			file_pattern = team_to_abbrev[self.teamhome]+"_"+team_to_abbrev[self.teamaway]+"_*_goal.xml"
			for file in os.listdir('./InfoXMLs'):
				if fnmatch.fnmatch(file, file_pattern):
					return(file)
	
	def generate_Reports(self, request):
		#generate reports with PASS
		try:
			templatetexthome, templatetextaway, templatedict = TopicWalk(self.matchFilename)
		except Exception as err:
			print("Error generating report for "+self.matchFilename)
			print(type(err))
			print(err.args)
			print(err)
			with open('HTML/results-error.html', 'r') as htmlfile:
				responsePage=htmlfile.read()
			request.write(responsePage.encode('utf-8'))
			request.finish()
			return
			
		with open('HTML/results-end.html', 'r') as htmlfile:
			responsePage=htmlfile.read()
		homereport = templatetexthome.strip().splitlines( )
		homereport.pop(0) #remove "Report for the supporters of $team"
		hometitle =  homereport.pop(0)
		awayreport = templatetextaway.strip().splitlines( )
		awayreport.pop(0) #remove "Report for the supporters of $team"
		awaytitle = awayreport.pop(0)
		responsePage = responsePage.replace('#TITLEHOME#',hometitle,1).replace('#TITLEAWAY#',awaytitle,1)
		homereporthtml = ""
		for line in homereport:
			homereporthtml = homereporthtml + "<p>"+line+"</p>"+"\n"
		awayreporthtml = ""
		for line in awayreport:
			awayreporthtml = awayreporthtml + "<p>"+line+"</p>"+"\n"		
		responsePage = responsePage.replace('#HOMEREPORT#',homereporthtml,1).replace('#AWAYREPORT#',awayreporthtml,1)
		responsePage = responsePage.replace('#XMLREPORTFILE#',self.matchFilename.replace('./InfoXMLs/',""))
		request.write(responsePage.encode('utf-8'))
		request.finish()
				
	def render_POST(self, request):
		arg1 = request.args[b"selectHome"][0].decode("utf-8")
		arg2 = request.args[b"selectAway"][0].decode("utf-8")
		resubmitted = b"resubmitted" in request.args
		#ToDo: request.setHeader('Content-Type', "application/json")
		#tell the browser to start loading the page even if it's not done yet
		request.setHeader('Transfer-Encoding:', 'chunked')
		escapedArg1 = cgi.escape(arg1)
		escapedArg2 = cgi.escape(arg2)
		matchFilename = self.getFileName(escapedArg1,escapedArg2)
		self.matchFilename = './InfoXMLs/'+matchFilename

		#load resultsfile
		xmlmatch = ElementTree(file='./InfoXMLs/'+matchFilename)
		league = xmlmatch.find('./MatchData/Highlights/League').text
		date = xmlmatch.find('./MatchData/Highlights/StartDate').text
		time = xmlmatch.find('./MatchData/Highlights/StartTime').text
		stadium = xmlmatch.find('./MatchData/Highlights/Stadium').text
		teamhomefull = xmlmatch.find('./MatchData/Highlights/Home/Team').text
		teamawayfull = xmlmatch.find('./MatchData/Highlights/Away/Team').text
		teamhomegoals = xmlmatch.find('./MatchData/Highlights/Home/FinalGoals').text
		teamawaygoals = xmlmatch.find('./MatchData/Highlights/Away/FinalGoals').text

		with open('HTML/results-start.html', 'r') as htmlfile:
			responsePage=htmlfile.read()
		
		responsePage = responsePage.replace('#FORMVALUE1#',arg1).replace('#FORMVALUE2#',arg2)	
			
		responsePage = responsePage.replace('#LEAGUE#',league,1).replace('#DATETIME#',date+", "+time,1).replace('#STADIUM#',stadium,1)
		responsePage = responsePage.replace('#TEAMHOMEENCODED#',self.teamhome,1).replace('#TEAMAWAYENCODED#',self.teamaway,1)
		responsePage = responsePage.replace('#TEAMHOME#',teamhomefull).replace('#TEAMAWAY#',teamawayfull)
		responsePage = responsePage.replace('#RESULTHOME#',teamhomegoals).replace('#RESULTAWAY#',teamawaygoals)
		request.write(responsePage.encode('utf-8'))
		if not resubmitted:
			reactor.callLater(0.1, self.generate_Reports, request)
		else:
			reactor.callLater(0, self.generate_Reports, request)
		return NOT_DONE_YET
		
		
root = File('./HTML')
generation = Generation()
root.putChild(b"generate", generation)



xml = File('./InfoXMLs')
root.putChild(b"XML", xml)


factory = Site(root)
endpoint = endpoints.TCP4ServerEndpoint(reactor, 8888)
endpoint.listen(factory)
print("listening on port 8888")
reactor.run()
