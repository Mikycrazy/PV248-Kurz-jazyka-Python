import sys
import re
from collections import Counter

if len(sys.argv) <= 2:
    exit("Too less arguments calling script")

fileName = sys.argv[1]
mode = sys.argv[2]
value = sys.argv[3] if len(sys.argv) == 4 else None

# Load data from file into collection
records_str = []
with open(fileName,'r', encoding='utf-8') as f:
    text = ""
    for line in f:
        if(len(line.strip()) == 0):
            records_str.append(text)
            text = ""
        else:
            text += line

# Process data into convenient format
records = []
for text in records_str:
    matches = re.finditer(r"^([^:]*):(.*)$", text, re.MULTILINE)   
    record_str = { match.group(1):match.group(2).strip() for match in matches }
    title = ( record_str['Title'] if 'Title' in record_str else None ) 
    composers = ( [ re.sub( r"\(.*\)", '', composer_str).strip() for composer_str in record_str['Composer'].split(';') if composer_str.strip() != ''] if 'Composer' in record_str else [])
    composition_year = None
    if 'Composition Year' in record_str:
        m = re.search(r"(\d{4})", record_str['Composition Year'])
        if m:
            composition_year = int(m.group(1))
        else:
            m = re.search(r"(\d{2})th century", record_str['Composition Year'])
            if m:
                composition_year = int(m.group(1)) * 100 - 1

    keys = [key.strip() for key in record_str['Key'].split(';') if key.strip() != ''] if 'Key' in record_str else []
    record = { 'Title': title, 'Composers':composers, 'Composition Year': composition_year, 'Keys': keys}
    records.append(record)

# Compute statistics
composers_ctr = Counter()
centuries_ctr = Counter()
keys_ctr = Counter()
for record in records:
    for composer in record['Composers']:
        composers_ctr[composer] += 1
    
    for key in record['Keys']:
        if 'minor' in key:
            key = key.split(' ')[0].lower()
        keys_ctr[key] += 1

    year = record['Composition Year']
    if year != None:
        century = (record['Composition Year'] - 1) // 100 + 1
        centuries_ctr[century] += 1

if mode == 'composer':
    for composer, count in sorted(composers_ctr.items()):
        print("{}: {}".format(composer, count))
elif mode == 'century':
    for century, count in sorted(centuries_ctr.items()):
        print("{}th century: {}".format(century, count))
elif mode == 'key':
    count = keys_ctr[value] if value in keys_ctr else None
    print("Key: {} Count: {}".format(value, count))
