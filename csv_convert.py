import unicodecsv as csv
import codecs
from unittest import TestCase
import re
import xml.etree.ElementTree as ET

import cerberus
import schema

# import cleaning functions
from updated_values import no_directions, update_street, update_city, update_number

OSM_PATH = 'edinburgh_scotland.osm'

NODES_PATH = 'nodes.csv'
NODE_TAGS_PATH ='node_tags.csv'
WAYS_PATH = 'ways.csv'
WAY_TAGS_PATH = 'way_tags.csv'
WAY_NODES_PATH = 'way_nodes.csv'

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+', re.IGNORECASE)
PROBLEMCHARS = re.compile(r'^[=\+/&<>;\'"?%#$@\,\. \t\r\n]', re.IGNORECASE)

street_mapping = {
    'Ave': 'Avenue',
    'Ave.': 'Avenue',
    'Bildings': 'Buildings',
    'Rd' : 'Road',
    'court': 'Court',
    'place': 'Place',
    'Pl': 'Place'
}

city_mapping = {
    'Ed': 'Edinburgh',
    'Penicuick': 'Penicuik'
}

SCHEMA = schema.schema

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version',
              'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset',
             'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

def shape_element(element, node_attr_fields = NODE_FIELDS, way_attr_fields = WAY_FIELDS,
                  problem_chars = PROBLEMCHARS, default_tag_type = 'regular'):
    
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []
    
    
    if element.tag == 'node':
        # filling in for node
        
        for att in node_attr_fields:
            try:
                node_attribs[att] = element.attrib[att]
            except:
                if att == 'user':
                    node_attribs[att] = 'Unknown'
                elif att == 'uid':
                    node_attribs[att] = 0
                
        # filing in for node_tags
        # cleaning tag values
        for tag in element:
            if tag.attrib['k'] == 'addr:street':
                tag.attrib['v'] = update_street(tag.attrib['v'], street_mapping)
            elif tag.attrib['k'] == 'addr:city':
                tag.attrib['v'] = update_city(tag.attrib['v'], city_mapping)
            elif tag.attrib['k'] == 'phone' or tag.attrib['k'] == 'contact:phone':
                tag.attrib['v'] = update_number(tag.attrib['v'])
            
            node_tags = {}
            # ignore tags if it contains problemchars
            if problem_chars.match(tag.attrib['k']):
                continue
            # if k has a colon, separate key and type
            elif LOWER_COLON.match(tag.attrib['k']):
                node_tags['id'] = element.attrib['id']
                node_tags['key'] = tag.attrib['k'].split(':',1)[1]
                node_tags['value'] = tag.attrib['v']
                node_tags['type'] = tag.attrib['k'].split(':',1)[0]
                tags.append(node_tags)
            # for other k values
            else:
                node_tags['id'] = element.attrib['id']
                node_tags['key'] = tag.attrib['k']
                node_tags['value'] = tag.attrib['v']
                node_tags['type'] = 'regular'
                tags.append(node_tags)
        
        # return values
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        # filling in for way
        for att in way_attr_fields:
            try:
                way_attribs[att] = element.attrib[att]
            except:
                if att == 'user':
                    way_attribs[att] = 'Unknown'
                elif att == 'uid':
                    way_attrbs[att] = 0
        
        # filling in for way_nodes

        i = 0
        for tag in element:
            if tag.tag == 'nd':
                way_node = {}
                way_node['id'] = element.attrib['id']
                way_node['node_id'] = tag.attrib['ref']
                way_node['position'] = i
                i += 1
                way_nodes.append(way_node)
        
        # filling in for way_tags
            elif tag.tag == 'tag':
                if tag.attrib['k'] == 'addr:street':
                    tag.attrib['v'] = update_street(tag.attrib['v'], street_mapping)
                elif tag.attrib['k'] == 'addr:city':
                    tag.attrib['v'] = update_city(tag.attrib['v'], city_mapping)
                elif tag.attrib['k'] == 'phone' or tag.attrib['k'] == 'contact:phone':
                    tag.attrib['v'] = update_number(tag.attrib['v'])
                
                way_tag = {}
                if PROBLEMCHARS.match(tag.attrib['k']):
                    continue
                elif LOWER_COLON.match(tag.attrib['k']):
                    way_tag['id'] = element.attrib['id']
                    way_tag['key'] = tag.attrib['k'].split(':',1)[1]
                    way_tag['value'] = tag.attrib['v']
                    way_tag['type'] = tag.attrib['k'].split(':',1)[0]
                    tags.append(way_tag)
                else:
                    way_tag['id'] = element.attrib['id']
                    way_tag['key'] = tag.attrib['k']
                    way_tag['value'] = tag.attrib['v']
                    way_tag['type'] = 'regular'
                    tags.append(way_tag)
                
        
        return {'way': way_attribs, 'way_nodes': way_nodes,
               'way_tags': tags}
    
    
    
# ================================================== #
#               Helper Functions                     #
# ================================================== #

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        errors = validator.errors.items()
        message_string = "\nElement has the following errors:\n{}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(error_string))



class Writer(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, bytes) else v) for k, v in row.items()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""
    with codecs.open(NODES_PATH, 'wb') as nodes_file, \
        codecs.open(NODE_TAGS_PATH, 'wb') as nodes_tags_file, \
        codecs.open(WAYS_PATH, 'wb') as ways_file, \
        codecs.open(WAY_NODES_PATH, 'wb') as way_nodes_file, \
        codecs.open(WAY_TAGS_PATH, 'wb') as way_tags_file:

        nodes_writer = csv.DictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = csv.DictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = csv.DictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = csv.DictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = csv.DictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element,)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)
