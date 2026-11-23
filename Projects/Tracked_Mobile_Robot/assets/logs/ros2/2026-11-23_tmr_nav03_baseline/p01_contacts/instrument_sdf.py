"""Attach a Gazebo contact sensor to each collision of an already-converted robot SDF."""
import argparse
from pathlib import Path
from xml.etree import ElementTree as ET

def instrument(source, output):
    tree = ET.parse(source)
    model = tree.getroot().find('model')
    if model is None:
        raise ValueError('Expected a single robot model')
    topics = {}
    for link in model.findall('link'):
        for collision in link.findall('collision'):
            name = collision.attrib['name']
            sensor_name = 'observe_' + name
            sensor = ET.SubElement(link, 'sensor', name=sensor_name, type='contact')
            contact = ET.SubElement(sensor, 'contact')
            ET.SubElement(contact, 'collision').text = name
            topics[f"/world/empty/model/{model.attrib['name']}/link/{link.attrib['name']}/sensor/{sensor_name}/contact"] = name
    if not topics:
        raise ValueError('No collision shapes found')
    tree.write(output, encoding='utf-8', xml_declaration=True)
    return topics

if __name__ == '__main__':
    import json
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('source', type=Path)
    args.add_argument('output', type=Path)
    args.add_argument('topic_manifest', type=Path)
    a = args.parse_args()
    a.topic_manifest.write_text(json.dumps(instrument(a.source, a.output), indent=2)+'\n')
