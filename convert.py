import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import re

def parse_stealth_data(raw_data):
    root = ET.Element("tv", {"generator-info-name": "StealthSportsMaster"})
    channels_added = set()

    for line in raw_data.strip().split('\n'):
        if not line or '|' not in line and ':' not in line: continue
        
        try:
            # 1. Standardize Separators
            line = line.replace(' @ ', ' vs. ').replace(' X ', ' vs. ').replace(' AT ', ' vs. ')
            
            # 2. Extract Channel & Event Info
            parts = line.split('|') if '|' in line else line.split(': ', 1)
            channel_header = parts[0].strip()
            remainder = parts[1].strip()

            # 3. Time Extraction Logic
            # Matches (YYYY-MM-DD HH:MM:SS) OR START:YYYY-MM-DD HH:MM:SS
            start_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', remainder)
            stop_match = re.search(r'STOP:(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', remainder)
            
            if not start_match: continue
            start_str = start_match.group(1)
            start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
            
            # 4. Cleaning the Title
            # Remove time strings and brackets from title
            clean_title = re.sub(r'\(.*?\)', '', remainder)
            clean_title = re.sub(r'START:.*', '', clean_title).strip()
            clean_title = clean_title.replace('_', ' ')

            # 5. Create Channel ID
            chan_id = re.sub(r'[^a-zA-Z0-9]', '.', channel_header)
            if chan_id not in channels_added:
                chan_node = ET.SubElement(root, "channel", id=chan_id)
                ET.SubElement(chan_node, "display-name").text = channel_header
                channels_added.add(chan_id)

            # 6. Determine Duration
            if stop_match:
                stop_dt = datetime.strptime(stop_match.group(1), "%Y-%m-%d %H:%M:%S")
            else:
                stop_dt = start_dt + timedelta(hours=4) # Default for games

            # 7. Build Programme
            xml_start = start_dt.strftime("%Y%m%d%H%M%S") + " -0400"
            xml_stop = stop_dt.strftime("%Y%m%d%H%M%S") + " -0400"

            prog = ET.SubElement(root, "programme", start=xml_start, stop=xml_stop, channel=chan_id)
            ET.SubElement(prog, "title", lang="en").text = clean_title
            ET.SubElement(prog, "desc", lang="en").text = f"Live Coverage on {channel_header}"
            
        except Exception as e:
            continue

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write("sports.xml", encoding="utf-8", xml_declaration=True)

# This reads from a local file named 'input.txt' which you will create in your repo
if __name__ == "__main__":
    try:
        with open('input.txt', 'r') as f:
            data = f.read()
            parse_stealth_data(data)
    except FileNotFoundError:
        # Create empty file if missing to prevent crash
        open('sports.xml', 'w').close()
