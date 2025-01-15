import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

API_KEY = "c6b2-d9aa6f"  # Replace with your actual API key
GITHUB_PAGES_DIR = "rss_output"  # Directory for GitHub Pages

def fetch_live_boxscore(sport, api_key, max_games=1, date="2025-01-15"):
    """Fetch live boxscore data for the given sport with a limit on the number of games."""
    base_url = f"https://api.natstat.com/v2/boxscores/{sport}/"
    params = {
        'key': api_key,
        'format': 'xml',
        'max': max_games,
        'date': date  # Add date parameter
    }
    response = requests.get(base_url, params=params)
    print(f"Request URL: {response.url}")
    print(f"Response Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Raw XML Data:\n{response.text}")  # Debugging: Print raw XML
        return response.text  # Raw XML response
    else:
        print(f"Error fetching data: {response.status_code} - {response.text}")
        return None

def save_rss_feed(sport, items, output_dir, filename):
    """Generate and save an RSS feed."""
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    # Channel metadata
    ET.SubElement(channel, "title").text = f"Live {sport} Boxscores"
    ET.SubElement(channel, "link").text = f"https://api.natstat.com/v2/boxscores/{sport}/"
    ET.SubElement(channel, "description").text = f"Live updates for {sport} games."
    ET.SubElement(channel, "lastBuildDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

    # Add items to the feed
    for item_data in items:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = item_data.get("title")
        ET.SubElement(item, "link").text = item_data.get("link")
        ET.SubElement(item, "description").text = item_data.get("description")
        ET.SubElement(item, "pubDate").text = item_data.get("pubDate")

    # Write the RSS feed to a file
    os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists
    filepath = os.path.join(output_dir, filename)
    tree = ET.ElementTree(rss)
    with open(filepath, "wb") as file:
        tree.write(file, encoding="utf-8", xml_declaration=True)
    print(f"Saved RSS feed to {filepath}")

if __name__ == '__main__':
    sports = ['NBA']  # Add other sports as needed
    max_games = 1  # Set to 1 for testing; increase as needed
    date = "2025-01-15"  # Set the desired date for the query

    for sport in sports:
        # Fetch live boxscore data
        xml_data = fetch_live_boxscore(sport, API_KEY, max_games, date)
        if xml_data:
            # Parse the XML data and prepare RSS items
            root = ET.fromstring(xml_data)
            items = []
            for game in root.findall(".//game"):  # Adjust XPath based on API response structure
                team1 = game.find('team1').text if game.find('team1') is not None else "Unknown"
                team2 = game.find('team2').text if game.find('team2') is not None else "Unknown"
                score1 = game.find('score1').text if game.find('score1') is not None else "N/A"
                score2 = game.find('score2').text if game.find('score2') is not None else "N/A"
                game_id = game.find('game_id').text if game.find('game_id') is not None else "0"

                items.append({
                    "title": f"{team1} vs {team2}",
                    "link": f"https://natstat.com/boxscore/{game_id}",
                    "description": f"Live score: {score1} - {score2}",
                    "pubDate": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
                })

            # Save the RSS feed
            rss_filename = f"{sport.lower()}_live_feed.xml"
            save_rss_feed(sport, items, GITHUB_PAGES_DIR, rss_filename)
