## Importing all required libraries
from bs4 import BeautifulSoup
import pandas as pd
import requests 
import time

all_teams = []  # List to store all team DataFrames

# Step 1: Get Premier League page HTML
html = requests.get('https://fbref.com/en/comps/9/Premier-League-Stats').text
soup = BeautifulSoup(html, 'lxml')

# Step 2: Locate the first table with team links
table = soup.find_all('table', class_='stats_table')[0]

# Step 3: Get all <a> links from the table
links = table.find_all('a')
links = [l.get("href") for l in links]
links = [l for l in links if '/squads/' in l]  # Filter only squad links

# Step 4: Build full URLs for team pages
team_urls = [f"https://fbref.com{l}" for l in links]

# Step 5: Loop through each team page and extract stats
for team_url in team_urls: 
    team_name = team_url.split("/")[-1].replace("-Stats", "")  # Clean team name
    data = requests.get(team_url).text
    soup = BeautifulSoup(data, 'lxml')
    
    stats = soup.find_all('table', class_='stats_table')[0]  # Get first stats table
    
    # Convert HTML table to pandas DataFrame
    team_data = pd.read_html(str(stats))[0]
    
    # Drop multi-index column level if it exists
    if isinstance(team_data.columns, pd.MultiIndex):
        team_data.columns = team_data.columns.droplevel()
    
    # Add team name to the DataFrame
    team_data["Team"] = team_name
    
    # Append to list of all teams
    all_teams.append(team_data)
    
    # Delay to avoid being blocked
    time.sleep(5)

# Step 6: Combine all teams into a single DataFrame
stat_df = pd.concat(all_teams)

# Step 7: Save to CSV
stat_df.to_csv("stats.csv", index=False)
