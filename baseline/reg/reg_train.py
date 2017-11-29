__author__ = 'thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 08/08/2017
Description:
    Compute frequency of referring expressions for each reference condition
"""

import cPickle as p
import nltk
import sys
sys.path.append('../')

lemma = {
    'he':'he', 'his':'he', 'him': 'he',
    'she':'she', 'her':'she', 'hers':'she',
    'it':'it', 'its':'it',
    'we':'we', 'our':'we', 'ours':'we', 'us':'we',
    'they':'they', 'their':'they', 'theirs':'they', 'them':'they'
}
pronouns, names, descriptions, demonstratives = {}, {}, {}, {}

# References extracted on preprocessing
references = p.load(open('../../data/train/data.cPickle'))

# Retrieve all wiki entities and normalize their names
entities = set()
for reference in references:
    entities = entities.union([reference['entity']])

print 'Number of entities: ', len(list(entities))

for entity in entities:
    print 'Entity: ', entity
    pronouns[entity] = []
    bnames, bdescriptions, bdemonstratives = [], [], []

    for syntax in ['np-subj', 'np-obj', 'subj-det']:
        for text_status in ['new', 'given']:
            for sentence_status in ['new', 'given']:
                reference = filter(lambda x: x['entity'] == entity and x['syntax'] == syntax and x['text_status'] == text_status and x['sentence_status'] == sentence_status, references)

                if (syntax, text_status, sentence_status, entity) not in names:
                    names[(syntax, text_status, sentence_status, entity)] = []
                if (syntax, text_status, sentence_status, entity) not in descriptions:
                    descriptions[(syntax, text_status, sentence_status, entity)] = []
                if (syntax, text_status, sentence_status, entity) not in demonstratives:
                    demonstratives[(syntax, text_status, sentence_status, entity)] = []

                if len(reference) > 0:
                    for refex in reference:
                        reftype = refex['reftype']
                        reg = refex['refex'].strip().lower()

                        if reftype == 'pronoun' and reg in lemma:
                            pronouns[entity].append(lemma[reg])
                        elif reftype == 'name':
                            names[(syntax, text_status, sentence_status, entity)].append(reg)
                        elif reftype == 'description':
                            descriptions[(syntax, text_status, sentence_status, entity)].append(reg)
                        elif reftype == 'demonstrative':
                            demonstratives[(syntax, text_status, sentence_status, entity)].append(reg)

                if len(names[(syntax, text_status, sentence_status, entity)]) == 0:
                    bnames.append((syntax, text_status, sentence_status, entity))
                if len(descriptions[(syntax, text_status, sentence_status, entity)]) == 0:
                    bdescriptions.append((syntax, text_status, sentence_status, entity))
                if len(demonstratives[(syntax, text_status, sentence_status, entity)]) == 0:
                    bdemonstratives.append((syntax, text_status, sentence_status, entity))

            # First backoff
            reference = filter(lambda x: x['entity'] == entity and x['syntax'] == syntax and x['text_status'] == text_status, references)
            if len(reference) > 0:
                for refex in reference:
                    reftype = refex['reftype']
                    reg = refex['refex'].strip().lower()

                    if reftype == 'name':
                        for key in bnames:
                            names[key].append(reg)
                        bnames = []
                    elif reftype == 'description':
                        for key in bdescriptions:
                            descriptions[key].append(reg)
                        bdescriptions = []
                    elif reftype == 'demonstrative':
                        for key in bdemonstratives:
                            demonstratives[key].append(reg)
                        bdemonstratives = []

        # Second backoff
        reference = filter(lambda x: x['entity'] == entity and x['syntax'] == syntax, references)
        if len(reference) > 0:
            for refex in reference:
                reftype = refex['reftype']
                reg = refex['refex'].strip().lower()

                if reftype == 'name':
                    for key in bnames:
                        names[key].append(reg)
                    bnames = []
                elif reftype == 'description':
                    for key in bdescriptions:
                        descriptions[key].append(reg)
                    bdescriptions = []
                elif reftype == 'demonstrative':
                    for key in bdemonstratives:
                        demonstratives[key].append(reg)
                    bdemonstratives = []

    # Third backoff
    reference = filter(lambda x: x['entity'] == entity, references)
    if len(reference) > 0:
        for refex in reference:
            reftype = refex['reftype']
            reg = refex['refex'].strip().lower()

            if reftype == 'name':
                for key in bnames:
                    names[key].append(reg)
                bnames = []
            elif reftype == 'description':
                for key in bdescriptions:
                    descriptions[key].append(reg)
                bdescriptions = []
            elif reftype == 'demonstrative':
                for key in bdemonstratives:
                    demonstratives[key].append(reg)
                bdemonstratives = []

for entity in pronouns:
    pronouns[entity] = sorted(nltk.FreqDist(pronouns[entity]).items(), key=lambda x:x[1], reverse=True)[:2]

for key in names:
    names[key] = sorted(nltk.FreqDist(names[key]).items(), key=lambda x:x[1], reverse=True)[:2]

for key in descriptions:
    descriptions[key] = sorted(nltk.FreqDist(descriptions[key]).items(), key=lambda x:x[1], reverse=True)[:2]

for key in demonstratives:
    demonstratives[key] = sorted(nltk.FreqDist(demonstratives[key]).items(), key=lambda x:x[1], reverse=True)[:2]

references = {'pronouns':pronouns, 'names':names, 'descriptions':descriptions, 'demonstratives':demonstratives}
p.dump(references, open('reg.cPickle', 'w'))