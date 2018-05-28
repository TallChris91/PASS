from Governing_module import TopicWalk
import re
import os
import sys
import pickle
from Info_dict_module import InfoDict
import glob


def main(file, savestate='n'):
    templatetexthome, templatetextaway, templatetextneutral, templatedict = TopicWalk(file)
    infodict = InfoDict(file)
    # print(templatetexthome)
    # print(templatetextaway)
    # print(templatedict)
    # print(infodict)

    data = {'meta': infodict, 'content': templatedict}
    print(data)

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

    return data


def matches():
    matches = []
    xml_files = glob.glob('./NewInfoXMLs/*.xml')
    print(os.getcwd())
    print(xml_files)
    # i = 0
    for file in xml_files:
        # if i == 10:
        #     break
        data = {}
        data['file'] = os.path.basename(file)
        data['info'] = InfoDict(file)

        matches.append(data)
        # i = i + 1

    # TODO: sort matches by date
    return matches


# print(matches())

# main('./InfoXMLs/VVV_FCEM_22042016_goal.xml', 'y')

#if __name__ == '__main__':
    #main(sys.argv[1:])