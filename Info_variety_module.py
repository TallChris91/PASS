import pickle
from os import path

def InfoVariety(homeaway, templates, previoustemplates=None):
    if previoustemplates == None:
        previoustemplates = []
    previousreporttemplates = []
    if homeaway == 'home' and path.exists("templateshome.p"):
        with open('templateshome.p', 'rb') as f:
            previousreporttemplates = pickle.load(f)
    elif homeaway == 'away' and path.exists("templatesaway.p"):
        with open('templatesaway.p', 'rb') as f:
            previousreporttemplates = pickle.load(f)

    previoustemplates = previoustemplates + previousreporttemplates

    for cat_idx, cat_val in enumerate(templates):
        for previoustemplate in previoustemplates:
            if len(cat_val) > 1:
                try:
                    del templates[cat_idx][templates[cat_idx].index(previoustemplate)]
                except ValueError:
                    ''
    return templates