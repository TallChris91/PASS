import re
import Templatefillers
import sys

def ReplaceSemicolon(soup, homeaway, template, **kwargs):
    #Double semicolon is the category while the part before the double semicolon shows the template options
    filler, gap = re.split(r';; ', template)
    fillerlist = re.split(r'[|]', filler)
    fillerdict = {}
    for filler in fillerlist:
        val, key = re.split(r'; ', filler)
        fillerdict.update({key:val})
    gapfill = Templatefillers.templatefillers(soup, homeaway, gap, **kwargs)
    for key in fillerdict:
        if key == gapfill:
            return fillerdict[key]

def TemplateReplacement(soup, homeaway, template, **kwargs):
    p = re.compile(r'(<(.*?)>)')
    gapsfound = p.findall(template)
    gapsreplacement = [x[1] for x in gapsfound]
    gapscomplete = [x[0] for x in gapsfound]
    replacementgaps = []
    for gap in gapsreplacement:
        if ';;' in gap:
            replacementgaps.append(ReplaceSemicolon(soup, homeaway, gap, **kwargs))
        else:
            replacementgaps.append(Templatefillers.templatefillers(soup, homeaway, gap, **kwargs))

    for idx, val in enumerate(gapscomplete):
        try:
            if isinstance(replacementgaps[idx], tuple):
                template = re.sub(re.sub('[|]', '', gapscomplete[idx]), replacementgaps[idx][1], re.sub('[|]', '', template))
            else:
                try:
                    template = re.sub(re.sub('[|]', '', gapscomplete[idx]), replacementgaps[idx], re.sub('[|]', '', template))
                except:
                    print(template)
                    sys.exit(1)

            if template[0].islower():
                template = template[0].upper() + template[1:]
        except TypeError:
            ''

    return template, replacementgaps