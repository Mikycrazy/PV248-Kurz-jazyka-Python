import sys
import re
from collections import Counter

regex = r"(.*): (.*)$"

if len(sys.argv) <= 2:
    exit("Too less arguments calling script")

fileName = sys.argv[1]
mode = sys.argv[2]

records_str = []
with open(fileName,'r', encoding='utf-8') as f:
    text = ""
    for line in f:
        if(len(line.strip()) == 0):
            records_str.append(text)
            text = ""
        else:
            text += line
    
records = []
for text in records_str:
    matches = re.finditer(regex, text, re.MULTILINE)   
    record_str = { match.group(1):match.group(2) for match in matches }
    composers = ( [composer_str.strip() for composer_str in record_str['Composer'].split(';')] if 'Composer' in record_str else [])
    composition_year = (int(record_str['Composition Year']) if 'Composition Year' in record_str and record_str['Composition Year'].isdigit() else None)
    record = { 'Composers':composers, 'Composition Year': composition_year}
    records.append(record)
    print(record)

composers_ctr = Counter()
for record in records:
    for composer in record['Composers']:
        composers_ctr[composer] += 1

print(composers_ctr)

