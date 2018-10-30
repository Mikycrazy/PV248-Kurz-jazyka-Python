# -*- coding: utf-8 -*-
import json

class Print(object):
    def __init__(self, print_id, partiture, edition_name, editors, title, incipit, key, genre, year, voices, composers):
        self.print_id = print_id
        self.partiture = partiture
        self.edition = Edition(edition_name, editors, Composition(title, incipit, key, genre, year, voices, composers))

    def composition(self):
        return self.edition.composition

    def format_json(self):
        return { 'Print Number': self.print_id, 'Partiture': self.partiture, 'Edition': self.edition.format_json() }

class Edition(object):
    def __init__(self, name, authors, composition):
        self.name = name
        self.authors = authors
        self.composition = composition
    
    def format_json(self):
        return { 'Edition': self.name, 'Editor': [x.format_json() for x in self.authors], 'Composition': self.composition.format_json() }

class Composition(object):
    def __init__(self, name = None, incipit = None, key = None, genre = None, year = None, voices = {}, authors = []):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors

    def format_json(self):
        voices_json = {}
        if len(self.voices.keys()) > 0:
            keys = sorted(self.voices.keys())
            voices_json = { k:(self.voices[k].format_json()) if k in keys else Voice() for k in range(1, keys[-1] + 1) }

        return { 'Title': self.name,
         'Incipit': self.incipit, 
         'Key': self.key,
         'Genre': self.genre,
         'Year': self.year, 
        #  'Voices': {k:v.format_json() for k,v in sorted(self.voices.keys())},
         'Voices': voices_json,
         'Composer': [x.format_json() for x in self.authors] }
         


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

    def format_json(self):
        return {k:v for k,v in self.__dict__.items() if v is not None}

class Person(object):
    def __init__(self, name, born = None, died = None):
        self.name = name
        self.born = born
        self.died = died

    def format_json(self):
        return {k:v for k,v in self.__dict__.items() if v is not None}