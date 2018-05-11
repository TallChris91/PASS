from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import os.path
import time
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import regex as re
from datetime import date
from lxml import etree
import sys


def query(query, currentpath):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-infobars")
    try:
        driver = webdriver.Chrome(currentpath + '/chromedriver')
    except OSError:
        driver = webdriver.Chrome(currentpath + '/chromedriver.exe')
    while True:
        try:
            driver.get(query)
            break
        except:
            ''
    driver.find_element_by_xpath('//form').click()
    page_source = driver.page_source
    driver.close()
    root = BeautifulSoup(page_source, "lxml")
    return root

def getteams(root):
    tablepart = root.find('div', {"class": "o-table__body c-stats-table__body"})
    teams = tablepart.find_all('a')
    websitelist = []
    for team in teams:
        website = team['href']
        website = 'https://www.vi.nl' + website
        website = re.sub('wedstrijden', 'selectie', website)
        websitelist.append(website)
    return websitelist

def getplayers(teamroot):
    tablepart = teamroot.find_all('div', {"class": "o-table__body c-stats-table__body"})
    websitelist = []
    for table in tablepart:
        players = table.find_all('a')
        for player in players:
            website = player['href']
            website = 'https://www.vi.nl' + website
            viplayername = player.find('div', {"class": "o-table__cell c-stats-table__cell c-stats-table__cell--hover"}).text.strip()
            websitelist.append((website, viplayername))
    return websitelist

def playerinfo(playerlink, currentpath, filename):
    playerroot = query(playerlink, currentpath)
    s2 = playerroot.prettify()
    with open(currentpath + '/NewInfoXMLs/PlayerInfo/' + filename + '_pagesource.xml', 'wb') as f:
        f.write(bytes(s2, 'UTF-8'))
    print(currentpath + '/NewInfoXMLs/PlayerInfo/' + filename + '_pagesource.xml has been written')

    playerinfopart = playerroot.find('div', {"class": "o-layout__item u-9/12@md u-9/12@lg"}).text.strip()
    playerinfopart = re.sub(r':\s+', ': ', playerinfopart)
    playerinfopart = re.sub(r'\s{2,}', '; ', playerinfopart)
    playerinfopart = re.sub(r'\n', '; ', playerinfopart)
    playerinfopart = playerinfopart.split('; ')
    for idx, pip in enumerate(playerinfopart):
        if not (':' in playerinfopart[idx]) and not (':' in playerinfopart[idx+1]):
            playerinfopart[idx] = playerinfopart[idx] + ': ' + playerinfopart[idx+1]
            playerinfopart[idx + 1] = ''
    playerinfopart = '; '.join(playerinfopart)
    playerinfopart = re.sub(r'\n', '; ', playerinfopart)
    try:
        firstname = re.search(r"Voornaam: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        firstname = ''
    try:
        lastname = re.search(r"Achternaam: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        lastname = ''

    fullname = firstname + " " + lastname
    try:
        birthdate = re.search(r"Geboortedatum: (.*?)(;|$)", playerinfopart).group(1)
        datedict = {'januari': 'January', 'februari': 'February', 'maart': 'March', 'april': 'April', 'mei': 'May', 'juni': 'June', 'juli': 'July',
                    'augustus': 'August', 'september': 'September', 'oktober': 'October', 'november': 'November', 'december': 'December'}
        birthdate = birthdate.split(' ')
        birthdate[1] = datedict[birthdate[1]]
        birthdate = birthdate[1] + ' ' + birthdate[0] + ', ' + birthdate[2]
    except AttributeError:
        birthdate = ''
    try:
        age = re.search(r"Leeftijd: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        age = ''
    try:
        birthplace = re.search(r"Geboorteplaats: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        birthplace = ''
    try:
        nationality = re.search(r"Nationaliteit: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        nationality = ''
    try:
        height = re.search(r"Lengte: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        height = ''
    try:
        weight = re.search(r"Gewicht: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        weight = ''
    try:
        preferredfoot = re.search(r"Voet: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        preferredfoot = ''
    try:
        currentclub = re.search(r"Huidige club: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        currentclub = ''
    try:
        yearswithclub = re.search(r"Actief bij club: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        yearswithclub = ''
    yearswithclub = re.sub(r" - nu", "-", yearswithclub)
    try:
        currentleague = re.search(r"Actief in: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        currentleague = ''
    try:
        position = re.search(r"Positie: (.*?)(;|$)", playerinfopart).group(1)
        if position == 'Keeper':
            position = 'Goalkeeper'
        if position == 'Verdediger':
            position = 'Defender'
        if position == 'Middenvelder':
            position = 'Midfielder'
        if position == 'Aanvaller':
            position = 'Attacker'
    except AttributeError:
        position = ''
    try:
        kitnumber = re.search(r"Shirtnummer: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        kitnumber = ''

    return fullname, firstname, lastname, birthdate, age, birthplace, nationality, height, weight, preferredfoot, currentclub, yearswithclub, currentleague, position, kitnumber

def PlayerXML(player, currentpath, filename):
    viname, vilink, fullname, firstname, lastname, birthdate, age, birthplace, nationality, height, weight, preferredfoot, currentclub, activeatclub, currentdivision, position, kitnumber = player
    playerelement = etree.Element("Player")
    #playerelement.set("PlayerId", id)
    firstnameelement = etree.SubElement(playerelement, "FirstName")
    firstnameelement.text = firstname
    lastnameelement = etree.SubElement(playerelement, "LastName")
    lastnameelement.text = lastname
    fullnameelement = etree.SubElement(playerelement, "Fullname")
    fullnameelement.text = fullname
    birthdateelement = etree.SubElement(playerelement, "BirthDate")
    birthdateelement.text = birthdate
    ageelement = etree.SubElement(playerelement, "Age")
    ageelement.text = age
    birthplaceelement = etree.SubElement(playerelement, "BirthPlace")
    birthplaceelement.set("BirthPlace", birthplace)
    birthplaceelement.set("Nationality", nationality)
    heightelement = etree.SubElement(playerelement, "Height")
    heightelement.text = height
    weightelement = etree.SubElement(playerelement, "Weight")
    weightelement.text = weight
    preferredfootelement = etree.SubElement(playerelement, "PreferredFoot")
    preferredfootelement.text = preferredfoot
    positionelement = etree.SubElement(playerelement, "WikiPosition")
    positionelement.text = position
    goalplayernumber = etree.SubElement(playerelement, "GoalComPlayerNumber")
    goalplayernumber.text = kitnumber
    goalshownname = etree.SubElement(playerelement, "GoalComShownName")
    goalshownname.text = viname
    goalwebsite = etree.SubElement(playerelement, "GoalComWebsite")
    goalwebsite.text = vilink
    currentteamelement = etree.SubElement(playerelement, "CurrentTeam")
    currentteamelement.text = currentclub
    yearsatcurrentteamelement = etree.SubElement(playerelement, "YearsAtCurrentTeam")
    yearsatcurrentteamelement.text = activeatclub
    currentdivisionelement = etree.SubElement(playerelement, "CurrentDivision")
    currentdivisionelement.text = currentdivision
    currentnumber = etree.SubElement(playerelement, "CurrentNumber")
    currentnumber.text = kitnumber

    playerelement = etree.tostring(playerelement, encoding="utf-8", xml_declaration=False, pretty_print=True)
    with open(currentpath + '/NewInfoXMLs/PlayerInfo/' + filename + '_element.xml', 'wb') as f:
        f.write(playerelement)
    print(currentpath + '/NewInfoXMLs/PlayerInfo/' + filename + '_element.xml has been written')

def mainscraper():
    currentpath = os.getcwd()
    root = query('https://www.vi.nl/competities/nederland/tweede-divisie/2017-2018/stand', currentpath)
    teamlist = getteams(root)
    for team in teamlist:
        teamroot = query(team, currentpath)
        playerlist = getplayers(teamroot)
        for player in playerlist:
            filename = re.search(r'spelers\/(.*?)\/profiel', player[0]).group(1)
            filename = re.sub(r'-', '_', filename)
            if not os.path.isfile(currentpath + '/NewInfoXMLs/PlayerInfo/' + filename + '_element.xml'):
                playerinfotuple = playerinfo(player[0], currentpath, filename)
                playerinfotuple = (player[1], player[0]) + playerinfotuple
                PlayerXML(playerinfotuple, currentpath, filename)



mainscraper()