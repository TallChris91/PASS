from Governing_module import TopicWalk
import re
import os
import sys
import pickle
from Info_dict_module import InfoDict

def main(file, savestate='n'):
    templatetexthome, templatetextaway, templatedict = TopicWalk(file)
    infodict = InfoDict(file)
    print(templatetexthome)
    print(templatetextaway)
    print(templatedict)
    print(infodict)
    if savestate == 'y':
        newfile = os.path.splitext(os.path.basename(file))[0]
        newfile = re.sub(r'goal', '', newfile)

        with open('./SavedReports/' + newfile + 'home.txt', 'wb') as f:
            print(newfile + 'home.txt saved')
            f.write(bytes(templatetexthome, 'UTF-8'))

        with open('./SavedReports/' + newfile + 'away.txt', 'wb') as f:
            print(newfile + 'away.txt saved')
            f.write(bytes(templatetextaway, 'UTF-8'))

        with open('./SavedReports/' + newfile + 'matchdict.p', 'wb') as f:
            print(newfile + 'matchdict.p saved')
            pickle.dump(templatedict, f)

        with open('./SavedReports/' + newfile + 'infodict.p', 'wb') as f:
            print(newfile + 'infodict.p saved')
            pickle.dump(infodict, f)

main('./InfoXMLs/VVV_FCEM_22042016_goal.xml', 'y')

#if __name__ == '__main__':
    #main(sys.argv[1:])