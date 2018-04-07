from Governing_module import TopicWalk, GeneralEvents
import re
import os
import sys
import glob


def main(argv):
    if len(argv) == 1:
        file = argv[0]
    if len(argv) == 2:
        file, savestate = argv
    templatetexthome, templatetextaway = TopicWalk(file)
    print(templatetexthome)
    print(templatetextaway)

    data = {}
    data['home'] = templatetexthome
    data['away'] = templatetextaway

    if savestate == 'y':
        newfile = os.path.splitext(os.path.basename(file))[0]
        newfile = re.sub(r'goal', '', newfile)

        with open('./SavedReports/' + newfile + 'home.txt', 'wb') as f:
            print(newfile + 'home.txt saved')
            f.write(bytes(templatetexthome, 'UTF-8'))

        with open('./SavedReports/' + newfile + 'away.txt', 'wb') as f:
            print(newfile + 'away.txt saved')
            f.write(bytes(templatetextaway, 'UTF-8'))

    return data


def matches():
    matches = []
    xml_files = glob.glob('InfoXMLs/*.xml')
    for file in xml_files:
        data = {}
        data['file'] = os.path.basename(file)
        data['team1'] = 'team 1 name'
        data['team2'] = 'team 2 name'
        data['score'] = 'score'

        matches.append(data)

    return matches



# main('C:/Users/Chris/Documents/Syncmap/Promotie/PASS/InfoXMLs/AC_DB_04122015_goal.xml', 'y')
#main(['/Users/stasiuz/PASS/InfoXMLs/AC_DB_04122015_goal.xml'])


# matches()


if __name__ == '__main__':
    main(sys.argv[1:])