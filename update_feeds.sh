#!/bin/bash
chmod +x update_feeds.sh

# Run Python script to fetch and update feeds
python3 fetch_data.py

# Commit and push updates to GitHub Pages
git add *.xml
git commit -m "Update RSS feeds"
git push origin main
