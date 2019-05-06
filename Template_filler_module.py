import re
import Templatefillers
import sys

def ReplaceSemicolon(jsongamedata, homeaway, template, **kwargs):
    #Double semicolon is the category while the part before the double semicolon shows the template options
    filler, gap = re.split(r';; ', template)
    fillerlist = re.split(r'[|]', filler)
    fillerdict = {}
    for filler in fillerlist:
        val, key = re.split(r'; ', filler)
        fillerdict.update({key:val})
    gapfill = Templatefillers.templatefillers(jsongamedata, homeaway, gap, **kwargs)
    for key in fillerdict:
        if key == gapfill:
            return fillerdict[key]

def TemplateReplacement(jsongamedata, homeaway, template, **kwargs):
    p = re.compile(r'(<(.*?)>)')
    gapsfound = p.findall(template)
    gapsreplacement = [x[1] for x in gapsfound]
    gapscomplete = [x[0] for x in gapsfound]
    replacementgaps = []
    for gap in gapsreplacement:
        if ';;' in gap:
            replacementgaps.append(ReplaceSemicolon(jsongamedata, homeaway, gap, **kwargs))
        else:
            replacementgaps.append(Templatefillers.templatefillers(jsongamedata, homeaway, gap, **kwargs))

    for idx, val in enumerate(gapscomplete):
        try:
            if isinstance(replacementgaps[idx], tuple):
                template = re.sub(re.sub('[|]', '', gapscomplete[idx]), str(replacementgaps[idx][1]), re.sub('[|]', '', template))
            else:
                try:
                    template = re.sub(re.sub('[|]', '', gapscomplete[idx]), str(replacementgaps[idx]), re.sub('[|]', '', template))
                except Exception as ex:
                    message = "An exception of type {0} occurred. Arguments:\n{1!r}".format(type(ex).__name__, ex.args)
                    print(message)
                    print("The error was with the following template:")
                    print(template)
                    sys.exit(1)

            if template[0].islower():
                template = template[0].upper() + template[1:]
        except TypeError:
            ''

    return template, replacementgaps