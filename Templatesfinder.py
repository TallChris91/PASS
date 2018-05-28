import sys
from contextlib import closing
from lxml import etree
from bs4 import BeautifulSoup
import lxml.html as html # pip install 'lxml>=2.3.1'
from lxml.html.clean        import Cleaner
from selenium.webdriver     import Firefox         # pip install selenium
from werkzeug.contrib.cache import FileSystemCache # pip install werkzeug
import unicodedata
import regex as re
import os.path
import os
from itertools import chain
from nltk.tokenize import sent_tokenize
import unicodedata
from unidecode import unidecode

sentenceinfo = []
filenames = []
rootDir = ('C:/Users/Chris/Documents/Syncmap/Promotie/Newspaper Corpus/Corpus/Eredivisie15-16/', 'C:/Users/Chris/Documents/Syncmap/Promotie/Newspaper Corpus/Corpus/Eredivisie16-17/')

#Get all files in the list
for dirName, subdirList, fileList in chain.from_iterable(os.walk(dir) for dir in rootDir):
#for dirName, subdirList, fileList in os.walk(rootDir):
    for fname in fileList:
        filename = dirName + fname
        with open(filename, "rb") as f:
            text = f.read()
        text = text.decode('utf-8', errors='replace')
        try:
            textsents = sent_tokenize(text)
        except UnicodeDecodeError:
            text = unicode(text)
            text = unicodedata.normalize("NFKD", text).encode('ascii', 'ignore')
            textsents = sent_tokenize(text)
        sentenceinfo.append(textsents[:5]) #Title, opponent, win/draw/loss
        #p = re.compile(r'(\bgeel\b)|(\bgele\b)', re.IGNORECASE) #Yellow cards
        #p = re.compile(r'(\brood\b)|(\brode\b)', re.IGNORECASE) #Red cards
        #p = re.compile(r'(\bgoal\b)|(\btreffer\b)|(\braak\b)|(\bschoot\b)|(\bdoel\b)|(\bdoelpunt\b)|(\bnet(ten)?\b)|(\btouw(en)?\b)|(\bwinkelhaak\b)|(\b\d\-\d\b)', re.IGNORECASE) #Goals
        #p = re.compile(r'(\bpenalty\b)|(\bpingel\b)|(\bstrafschop\b)|(stip\b)|(\bbuitenkans)|(elf\s?meter)', re.IGNORECASE) #Penalties
        '''
        sentencelist = []
        for i in textsents:
            m = p.search(i)
            if m:
                sentencelist.append(i)
        sentenceinfo.append(sentencelist)
        '''
        filenames.append(fname)

savestring = ''
for idx, val in enumerate(sentenceinfo):
    savestring += filenames[idx]
    savestring += '\n'
    savestring += '\n'.join(sentenceinfo[idx])
    savestring += '\n'
    savestring += '\n'
with open('C:/Users/Chris/Documents/Syncmap/Promotie/PASS/Sportsdesk Scraper/GeneralTemplates.txt', 'wb') as f:
#with open('C:\Users\Chris\Documents\Syncmap\Promotie\First version data-to-text\Relevant sentences\OwnGoalWin.txt', 'wb') as f:
    f.write(bytes(savestring.encode('utf-8')))
