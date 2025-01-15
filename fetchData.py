import requests
import json
from datetime import datetime

# Replace with your NatStat API key and endpoint
API_KEY = '74ba-3a27cd'
BASE_URL = 'https://api.natstat.com/v1/'
ENDPOINT = {
    'nba': 'nba/games',
    'ncaam': 'ncaam/games',
}

def fetch_games_data(sport):
    url = f"{BASE_URL}{ENDPOINT[sport]}"
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code} - {response.text}")
        return None

def generate_rss(data, sport):
    rss_feed = f"""
    <rss version="2.0">
    <channel>
        <title>{sport.upper()} Games Feed</title>
        <link>https://your-github-username.github.io/your-repo/</link>
        <description>Latest games from {sport.upper()}.</description>
        <lastBuildDate>{datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>
    """
    for game in data.get('games', []):
        game_date = datetime.strptime(game['date'], '%Y-%m-%dT%H:%M:%SZ')
        rss_feed += f"""
        <item>
            <title>{game['home_team']} vs {game['away_team']}</title>
            <link>https://www.natstat.com/{sport}/{game['id']}</link>
            <description>{game['status']} - {game['home_team']} {game['home_score']} : {game['away_score']} {game['away_team']}</description>
            <pubDate>{game_date.strftime('%a, %d %b %Y %H:%M:%S GMT')}</pubDate>
        </item>
        """
    rss_feed += """
    </channel>
    </rss>
    """
    return rss_feed.strip()

def save_rss_to_file(feed, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(feed)

if __name__ == '__main__':
    sports = ['nba', 'ncaam']
    for sport in sports:
        data = fetch_games_data(sport)
        if data:
            rss_feed = generate_rss(data, sport)
            save_rss_to_file(rss_feed, f'{sport}_feed.xml')
