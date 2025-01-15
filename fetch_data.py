import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# Predefine the list of game IDs you want to track
game_ids = ["1081688", "1081687", "1081686"]  # Add more game IDs as needed

def fetch_live_boxscore(sport, api_key, game_id):
    """Fetch live boxscore data for a specific game using the provided API key."""
    base_url = f"https://api.natstat.com/v2/boxscores/{sport}/"
    params = {
        "key": api_key,
        "format": "xml",
        "max": 1,
        "gameid": game_id  # Fetch data for the specific game ID
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.text
    else:
        print(f"Error fetching data: {response.status_code} - {response.text}")
        return None

def parse_game_data(xml_data, game_ids):
    """Parse the XML data to extract relevant game information."""
    root = ET.fromstring(xml_data)

    items = []

    # Add a first item for "NBA Live Scores"
    items.append({
        "title": "NBA Live Scores",
        "link": "https://api.natstat.com/v2/boxscores/NBA/",
        "description": "Live updates for NBA games.",
        "pubDate": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
    })

    for game_id in game_ids:
        # Look for each specific game data in the XML response
        boxscore = root.find(f".//boxscores/boxscore_{game_id}")
        if boxscore is not None:
            title = f"Game {game_id}: {boxscore.find('Visitor').text} {boxscore.find('ScoreVis').text} vs {boxscore.find('Home').text} {boxscore.find('ScoreHome').text} | Top Players: "
            link = boxscore.find('URL').text
            description = f"Game Summary: {boxscore.find('BoxscoreHeader').text}"

            items.append({
                "title": title,
                "link": link,
                "description": description,
                "pubDate": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
            })
        else:
            print(f"No data found for game ID {game_id}")

    return items

def generate_rss_feed(items):
    """Generate the RSS feed XML format."""
    rss_feed = """<?xml version="1.0" encoding="utf-8" ?>
<rss version="2.0">
    <channel>
        <title>NBA Live Scores</title>
        <link>https://api.natstat.com/v2/boxscores/NBA/</link>
        <description>Live updates for NBA games.</description>
        <lastBuildDate>{}</lastBuildDate>
""".format(datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000"))

    for item in items:
        rss_feed += f"""
        <item>
            <title>{item['title']}</title>
            <link>{item['link']}</link>
            <description>{item['description']}</description>
            <pubDate>{item['pubDate']}</pubDate>
        </item>
"""

    rss_feed += """
    </channel>
</rss>"""

    return rss_feed

def main():
    sport = "NBA"
    api_key = "c6b2-d9aa6f"  # Replace with your actual API key

    # Fetch data for each game ID
    all_items = []
    for game_id in game_ids:
        xml_data = fetch_live_boxscore(sport, api_key, game_id)
        if xml_data:
            items = parse_game_data(xml_data, game_ids)
            all_items.extend(items)

    # Generate the RSS feed with the items
    rss_feed = generate_rss_feed(all_items)

    # Write the RSS feed to a file
    with open("rss_feed.xml", "w") as file:
        file.write(rss_feed)

    print("RSS feed generated and saved to 'rss_feed.xml'.")

if __name__ == "__main__":
    main()
