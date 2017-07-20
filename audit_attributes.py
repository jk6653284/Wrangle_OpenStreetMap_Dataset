'''let's look for faulty names'''

import xml.etree.ElementTree as ET
import re
import pprint
from collections import defaultdict

osm_file = 'SAMPLE_OSM.osm'

'''STREET NAME AUDIT'''
# check if the street name is in expected, 
# if not, add it to street_types
expected = ['Place', 'Street', 'Crescent', 'Terrace', 'Road', 
            'Lane', 'Avenue', 'Way', 'Bank', 'Boulevard', 'Brae',
            'Bridge', 'Broadway', 'Causeway', 'Circus', 'Close',
            'Court', 'Drive', 'End', 'Entry','Glade', 'Greem',
            'Grove', 'Hill', 'Link', 'Links', 'Loan', 'Mains',
            'Medway', 'Mews', 'Parkway', 'Path', 'Rigg', 'Rise',
            'Row', 'Square', 'View', 'Walk', 'Wynd']

# function to look at the last word of the street name
# and see if the name is present in the dictionary
# if not, update the dictionary with the new word
def audit_street_type(street_types, street_name):
    # regex pattern to look at only the last word of the value
    street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
            
def audit_street_name(filename):
    # create a dictionary of set
    # this will contain all the 'unexpected' street names
    street_types = defaultdict(set)
    for event, element in ET.iterparse(filename):
        if element.tag == 'node' or element.tag == 'way':
            for tag in element.iter('tag'):
                if tag.attrib['k'] == 'addr:street':
                    audit_street_type(street_types, tag.attrib['v'])
    return street_types

print('faulty street names in the data: ')
print('\n',audit_street_name(osm_file))

'''POSTAL CODE AUDIT'''
# postal codes in Edinburgh should be of EH# #AA format

def audit_postal_code(filename):
    # regex pattern to search for the right postal code format
    find_postal = re.compile(r'(EH\d{1,2} \d{1}[A-Z][A-Z])')
    faulty_post = []
    for event, element in ET.iterparse(filename):
        if element.tag == 'way' or element.tag == 'node':
            for tag in element.iter('tag'):
                if tag.attrib['k'] == 'postal_code' or tag.attrib['k'] == 'addr:postcode':
                    if find_postal.match(tag.attrib['v']):
                        continue
                    else:
                        faulty_post.append(tag.attrib['v'])
    return faulty_post

print('faulty postcodes in the data: ')
print('\n',audit_postal_code(osm_file))


'''CITY AUDIT'''
# Find everything that is not 'Edinburgh'

def audit_city(filename):
    faulty_city = []
    for event, element in ET.iterparse(filename):
        if element.tag == 'way' or element.tag == 'node':
            for tag in element.iter('tag'):
                if tag.attrib['k'] == 'addr:city':
                    if tag.attrib['v'] != 'Edinburgh':
                        if tag.attrib['v'] not in faulty_city:
                            faulty_city.append(tag.attrib['v'])
    return faulty_city

print('faulty city names in the data: ')
print('\n',audit_city(osm_file))



'''PHONE AUDIT'''
# find every phone number that doesn't follow the standard
# Edinburgh phone format which is 0131 ### ####

def audit_number(filename):
    # regex pattern to search for the right phone number format
    phone_check = re.compile(r'(0131) \d\d\d \d\d\d\d')
    faulty_number = []
    for event, element in ET.iterparse(filename):
        if element.tag == 'node' or element.tag == 'way':
            for tag in element.iter('tag'):
                if tag.attrib['k'] == 'contact:phone' or tag.attrib['k'] == 'phone':
                    if phone_check.match(tag.attrib['v']):
                        continue
                    else:
                        faulty_number.append(tag.attrib['v'])
    return faulty_number

print('faulty phone numbers in the data: ')
print('\n',audit_number(osm_file))
