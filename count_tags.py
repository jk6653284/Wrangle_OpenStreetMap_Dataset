import xml.etree.ElementTree as ET
import pprint

osm_file = 'SAMPLE_OSM.osm'

# see the tags within the file and count tags
def count_tags(filename):
    tag_dict = {}
    for event, element in ET.iterparse(filename):
        if element.tag not in tag_dict:
            tag_dict[element.tag] = 1
        elif element.tag in tag_dict:
            tag_dict[element.tag] += 1
    return tag_dict

print(count_tags(osm_file))
