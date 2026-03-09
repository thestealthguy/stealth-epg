import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import re

def parse_schedule(raw_data):
    root = ET.Element("tv", {"generator-info-name": "StealthSportsAuto"})
    
    # Pre-define channels to avoid duplicates
    channels_added = set()

    for line in raw_data.strip().split('\n'):
        if not line or '|' not in line: continue
        
        # 1. Basic Extraction
        parts = line.split('|')
        channel_header = parts[0].strip() # e.g., US ESPN+ 001
        event_info = parts[1].strip()     # e.g., TEAM A VS TEAM B (2026-03-08 12:00:00)

        # 2. Extract Time using Regex
        time_match = re.search(r'\((\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\)', event_info)
        if not time_match: continue
        
        start_time_str = time_match.group(1)
        clean_title = event_info.replace(f"({start_time_str})", "").strip()
        
        # 3. Create Channel Tag if new
        chan_id = channel_header.replace(" ", ".")
        if chan_id not in channels_added:
            chan_node = ET.SubElement(root, "channel", id=chan_id)
            ET.SubElement(chan_node, "display-name").text = channel_header
            channels_added.add(chan_id)

        # 4. Handle Timezones & Durations
        start_dt = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
        # Standard 4 hour duration (14400 seconds)
        stop_dt = start_dt + timedelta(hours=4)
        
        # Format for XMLTV: YYYYMMDDHHMMSS +offset
        xml_start = start_dt.strftime("%Y%m%d%H%M%S") + " -0400"
        xml_stop = stop_dt.strftime("%Y%m%d%H%M%S") + " -0400"

        # 5. Build Programme
        prog = ET.SubElement(root, "programme", start=xml_start, stop=xml_stop, channel=chan_id)
        ET.SubElement(prog, "title", lang="en").text = clean_title.replace("_", " ").replace("@", "vs.")
        ET.SubElement(prog, "desc", lang="en").text = f"Live Sports: {channel_header}"

    # Save to file
    tree = ET.ElementTree(root)
    tree.write("sports.xml", encoding="utf-8", xml_declaration=True)
    print("Success! sports.xml has been created.")

# Add your raw data here or read from a file
if __name__ == "__main__":
    print("Paste your raw data below, then press Enter and Ctrl+D (or Ctrl+Z on Windows):")
    import sys
    data = sys.stdin.read()
    parse_schedule(data)