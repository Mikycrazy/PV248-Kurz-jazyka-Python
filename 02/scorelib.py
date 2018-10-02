# -*- coding: utf-8 -*-

import re


def load(filename):

    records_str = []
    with open(filename,'r', encoding='utf-8') as f:
        text = ""
        for line in f:
            if(len(line.strip()) == 0):
                if(len(text) > 0):
                    records_str.append(text)
                text = ""
            else:
                text += line
        records_str.append(text)

    prints = []
    for text in records_str:
        print_obj = Print(text)
        prints.append(print_obj)
    
    return prints


    

class Print(object):
    def __init__(self, text):
        matches = re.finditer(r"^([^:]*):(.*)$", text, re.MULTILINE)   
        dict_props = { match.group(1):match.group(2).strip() for match in matches }   
            
        print_id = int(dict_props['Print Number'])
        partiture = True if dict_props['Partiture'].lower().strip() == 'yes' else False
        name = ( dict_props['Edition'] if 'Edition' in dict_props else None ) 
        editors = []
        if 'Editor' in dict_props:
          editors = [ ParsePerson(editor) for editor in [ editor.strip() for editor in dict_props['Editor'].split(';') if editor.strip() != '']]      
        title = ( dict_props['Title'] if 'Title' in dict_props else None ) 
        incipit = ( dict_props['Incipit'] if 'Incipit' in dict_props else None ) 
        key = ( dict_props['Key'] if 'Key' in dict_props else None )
        genre = ( dict_props['Genre'] if 'Genre' in dict_props else None ) 
        year = None
        if 'Composition Year' in dict_props:
            r = re.compile(r"(\d{4})")
            m = r.match(dict_props['Composition Year'])
            if m is not None:
                year = int(m.group(1))
        voices = [ ParseVoice(v) for k,v in dict_props.items() if 'Voice' in k]
        composition_authors = []
        if 'Composer' in dict_props:
          composition_authors = [ ParsePerson(composer) for composer in [ composer.strip() for composer in dict_props['Composer'].split(';') if composer.strip() != '']]
          
        self.print_id = print_id
        self.partiture = partiture
        self.edition = Edition(name, editors, Composition(title, incipit, key, genre, year, voices, composition_authors))

    def format(self):
        print("Print Number: {}".format(self.print_id))
        print("Composer: {}".format(str.join("; ", [str(x) for x in self.edition.composition.authors])))
        print("Title: {}".format(xstr(self.edition.composition.name)))
        print("Genre: {}".format(xstr(self.edition.composition.genre)))
        print("Key: {}".format(xstr(self.edition.composition.key)))
        print("Composition Year: {}".format(xstr(self.edition.composition.year)))
        print("Edition: {}".format(xstr(self.edition.name)))
        print("Editor: {}".format(str.join(";", [str(x) for x in self.edition.authors])))
        for idx,voice in enumerate(self.edition.composition.voices):
            print("Voice {}: {}".format(idx + 1, voice))
        print("Partiture: {}".format("yes" if self.partiture else "no"))
        print("Incipit: {}".format(xstr(self.edition.composition.incipit)))

    def composition(self):
        return self.edition.composition


class Edition(object):
    def __init__(self, name, authors, composition):
        self.name = name
        self.authors = authors
        self.composition = composition
        


class Composition(object):
    def __init__(self, name = None, incipit = None, key = None, genre = None, year = None, voices = [], authors = []):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors


class Voice(object):
    def __init__(self, name = None, range_val = None):
        self.name = name
        self.range = range_val
    
    def __str__(self):      
        if not self.range and not self.name:
            return ''
        elif not self.range and self.name:
            return self.name
        elif self.range and not self.name:
            return self.range
        else:
            return "{}, {}".format(self.range, self.name)

class Person(object):
    def __init__(self, name, born = None, died = None):
        self.name = name
        self.born = born
        self.died = died

    def __str__(self):
        if not self.born and not self.died:
            return self.name
        else:
            return "{} ({}--{})".format(self.name, xstr(self.born), xstr(self.died))


def ParsePerson(text):
    born, died = ParseLifespan(text)
    name = re.sub( r"\(.*\)", '', text).strip()
    return Person(name, born, died)


def ParseLifespan(text):
    regex = r"\((?P<Born>\d{4})?[^-]*-{1,2}(?P<Died>\d{4})?.*\)"
    m = re.search(regex, text)
    born = None
    died = None
    if m:
        born = m.group("Born") if m.group("Born") else None
        died = m.group("Died") if m.group("Died") else None
        return born, died
    
    m = re.search(r"\(\+(?P<Died>\d{4})\)", text)
    if m:
        died = m.group("Died") if m.group("Died") else None

    m = re.search(r"\(\*(?P<Born>\d{4})\)", text)
    if m:
        born = m.group("Born") if m.group("Born") else None


    return born, died

def ParseVoice(text):
    m = re.search(r"^([\d\w]+--[\d\w]+)", text)
    voice_range = m.group(1) if m else None 
    if voice_range:
        parts = [ x.strip() for x in text.split(',') ]
        voice_name = str.join(", ",parts[1:])
    else:
        voice_name = text
    voice = Voice(voice_name, voice_range)
    return voice


def xstr(s):
    return '' if s is None else str(s)




    