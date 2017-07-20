'''
finding tag patterns in the dataset to look for problematic lines
'''

import xml.etree.ElementTree as ET
import re
import pprint

osm_file = 'SAMPLE_OSM.osm'

# list all tags in file
def tag_patterns(filename):
    k_patterns = {}
    for event, element in ET.iterparse(filename):
        if element.tag == 'tag':
            k = element.attrib['k']
            if k not in k_patterns:
                k_patterns[k] = 1
            elif k in k_patterns:
                k_patterns[k] += 1
    return k_patterns

# look for acceptable patterns, tags with a single colon, and tags with problematic characters

# list of patterns to search for
LOWER = re.compile(r'^([a-z]|_)*$', re.IGNORECASE)
LOWER_COLON = re.compile(r'^([a-z]|_)*:([a-z]|_)*$', re.IGNORECASE)
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]', re.IGNORECASE)

# keys to fill in
keys = {'lower': 0, 'lower_colon': 0, 'problemchars': 0,
       'other': 0}
key_types = {'lower': [],
            'lower_colon': [],
            'problemchars': [],
            'other': []}

# return counts for each pattern
def key_pattern_count(filename, keys):
    for event, element in ET.iterparse(filename):
        if element.tag == 'tag':
            k = element.attrib['k']
            if LOWER.search(k):
                keys['lower'] += 1
            elif LOWER_COLON.search(k):
                keys['lower_colon'] += 1
            elif PROBLEMCHARS.search(k):
                keys['problemchars'] += 1
            else:
                keys['other'] += 1
    return keys

# return cases satisfying each pattern
def key_patterns_print(filename, key_types):
    for event, element in ET.iterparse(filename):
        if element.tag == 'tag':
            k = element.attrib['k']
            if LOWER.search(k):
                if k not in key_types['lower']:
                    key_types['lower'].append(k)
            elif LOWER_COLON.search(k):
                if k not in key_types['lower_colon']:
                    key_types['lower_colon'].append(k)
            elif PROBLEMCHARS.search(k):
                if k not in key_types['problemchars']:
                    key_types['problemchars'].append(k)
            else:
                if k not in key_types['other']:
                    key_types['other'].append(k)
    return key_types

print('all tag patterns in ', str(osm_file))
print('\n',tag_patterns(osm_file))
print('\ncounts for each key pattern: ')
print('\n',key_pattern_count(osm_file, keys))
print('\nexamples of each type of key pattern:')
print('\n',key_patterns_print(osm_file, key_types))
