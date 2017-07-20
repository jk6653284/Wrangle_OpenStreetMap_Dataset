import xml.etree.ElementTree as ET
import re
import pprint

osm_file = 'SAMPLE_OSM.osm'

street_mapping = {
    'Ave': 'Avenue',
    'Ave.': 'Avenue',
    'Bildings': 'Buildings',
    'Rd' : 'Road',
    'court': 'Court',
    'place': 'Place',
    'Pl': 'Place'
}

# let's get rid of those directions
def no_directions(name):
    name = name.split(' ')
    name = ' '.join(name[:-1])
    return name


# let's create a function to update the names
def update_street(name, street_mapping):
    name_split = name.split(' ')
    
    # directions should be get rid of to replace it with the decsriptions before
    directions = ['East', 'North', 'South', 'West']
    
    # return address without directions at the end
    if name_split[-1] in directions:
        new_name = no_directions(name)
        return new_name
    
    # change names by mapping faulty names to right one
    else:
        for i in range(len(name_split)):
            if name_split[i] in street_mapping:
                name_split[i] = street_mapping[name_split[i]]
            else:
                continue
        new_name = ' '.join(name_split)
        
    return new_name

# change city names that are faulty

city_mapping = {
    'Ed': 'Edinburgh',
    'Penicuick': 'Penicuik'
}

def update_city(city, city_mapping):
    if city in city_mapping:
        return city_mapping[city]
    else:
        return city


# function to update phone number:
def update_number(number):
    # right format
    phone_check = re.compile(r'(0131) \d\d\d \d\d\d\d')
    
    # return original if number matches the right format
    if phone_check.match(number):
        return number
    
    # all other formats
    else:
        # numbers with country code
        if "+44" in number:
            # get rid of country code
            number = number[4:]
            
            # get rid of '-'
            if '-' in number:
                number = number.replace('-','')
                i_f = ''.join(['0', number[:3]])
                i_s = number[3:6]
                i_t = number[6:]
                number = ' '.join([i_f,i_s,i_t])
                
            # number code is 0131 but starts with 131
            elif re.compile(r'^131*').match(number):
                number = number.replace(' ','')
                if len(number) == 10:
                    i_f = ''.join(['0', number[:3]])
                    i_s = number[3:6]
                    i_t = number[6:]
                    number = ' '.join([i_f,i_s,i_t])
                else:
                    return number
            
            # number contains '()'
            elif "(" in number:
                number = number.split(")")[1].replace(' ','')
                if re.search(r'^800', number):
                    i_f = ''.join(['0',number[:3]])
                    i_s = number[3:]
                    number = ' '.join([i_f,i_s])
                else:
                    i_f = ''.join(['0',number[:3]])
                    i_s = number[3:6]
                    i_t = number[6:]
                    number = ' '.join([i_f,i_s,i_t])
                    
            # number code is 0800
            elif re.search(r'^800', number) or re.search(r'^0800', number):
                number = number.replace(' ','')
                i_f = ''.join(['0',number[:3]])
                i_s = number[3:]
                number = ' '.join([i_f,i_s])
                
            # all other numbers
            else:
                number = number.replace(' ','')
                if len(number) == 9:
                    if re.search(r'^3',number):
                        i_f = ''.join(['0',number[:3]])
                        i_s = number[3:6]
                        i_t = number[6:]
                        number = ' '.join([i_f, i_s,i_t])
                    else:
                        return number
                elif len(number) == 10:
                    if re.search(r'^7',number):
                        i_f = ''.join(['0',number[:4]])
                        i_s = number[4:]
                        number = ' '.join([i_f,i_s])
                    elif re.search(r'^8',number):
                        i_f = ''.join(['0',number[:3]])
                        i_s = number[3:6]
                        i_t = number[6:]
                        number = ' '.join([i_f,i_s,i_t])
                    else:
                        i_f = ''.join(['0',number[:4]])
                        i_s = number[4:]
                        number = ' '.join([i_f,i_s])
                else:
                    if re.search(r'^(0131)',number):
                        i_f = number[:4]
                        i_s = number[4:7]
                        i_t = number[7:]
                        number = ' '.join([i_f,i_s,i_t])
                    else:
                        return number
        
        # numbers without country code
        elif "+44" not in number:
            number = number.replace(' ', '')
            if number[0] == '0':
                if number[:4] == '0131':
                    i_f = number[:4]
                    i_s = number[4:7]
                    i_t = number[7:]
                    number = ' '.join([i_f,i_s,i_t])
                else:
                    i_f = number[:5]
                    i_s = number[5:]
                    number = ' '.join([i_f,i_s])
            else:
                return number
                
    return number

# function to mark all changes
def changed_names(filename, street_mapping, city_mapping):
    count = 0
    for event, element in ET.iterparse(filename):
        if element.tag == 'node' or element.tag == 'way':
            for tag in element.iter('tag'):
                
                # update street names
                if tag.attrib['k'] == 'addr:street':
                    new_name = update_street(tag.attrib['v'],street_mapping)
                    if new_name != tag.attrib['v']:
                        print('{} -> {}'.format(tag.attrib['v'], new_name))
                        count += 1
                elif tag.attrib['k'] == 'addr:city':
                    new_name = update_city(tag.attrib['v'], city_mapping)
                    if new_name != tag.attrib['v']:
                        print('{} -> {}'.format(tag.attrib['v'], new_name))
                        count += 1
                elif tag.attrib['k'] == 'phone' or tag.attrib['k'] == 'contact:phone':
                    new_name = update_number(tag.attrib['v'])
                    if new_name != tag.attrib['v']:
                        print('{} -> {}'.format(tag.attrib['v'], new_name))
                        count += 1
    print('\nTotal {} values updated.'.format(count))
                
# call function                  
# changed_names(osm_file, street_mapping, city_mapping)



