import requests
import anthropic
import dotenv
dotenv.load_dotenv()
import os
import datetime
import argparse

def sorter(schedule_data: dict, date: datetime) -> bool:
    start_date = datetime.datetime.strptime(schedule_data["start_date"], "%Y-%m-%d")
    end_date = datetime.datetime.strptime(schedule_data["end_date"], "%Y-%m-%d")
    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)  # end of day
    return start_date <= date <= end_date

schedule = [
    {"week": "01", "start_date": "2025-08-18", "end_date": "2025-09-01"},
    {"week": "02", "start_date": "2025-09-02", "end_date": "2025-09-07"},
    {"week": "03", "start_date": "2025-09-08", "end_date": "2025-09-14"},
    {"week": "04", "start_date": "2025-09-15", "end_date": "2025-09-21"},
    {"week": "05", "start_date": "2025-09-22", "end_date": "2025-09-28"},
    {"week": "06", "start_date": "2025-09-29", "end_date": "2025-10-05"},
    {"week": "07", "start_date": "2025-10-06", "end_date": "2025-10-12"},
    {"week": "08", "start_date": "2025-10-13", "end_date": "2025-10-19"},
    {"week": "09", "start_date": "2025-10-20", "end_date": "2025-10-26"},
    {"week": "10", "start_date": "2025-10-27", "end_date": "2025-11-02"},
    {"week": "11", "start_date": "2025-11-03", "end_date": "2025-11-09"},
    {"week": "12", "start_date": "2025-11-10", "end_date": "2025-11-16"},
    {"week": "13", "start_date": "2025-11-17", "end_date": "2025-11-23"},
    {"week": "14", "start_date": "2025-11-24", "end_date": "2025-11-30"},
    {"week": "15", "start_date": "2025-12-01", "end_date": "2025-12-07"},
]
def select_week(date: datetime.datetime) -> str:
    return sorted(
        filter(
            lambda w: sorter(w, date),
            schedule
        ),
        key=lambda w: w["week"]
    )[0]
    

# week = select_week(datetime.datetime.now())
parser = argparse.ArgumentParser(description="Generate ACC Football Newsletter")
 
parser.add_argument("--week", default=None, help="Week of the season in two digit format (e.g., '01', '02')")
args = parser.parse_args()

now = datetime.datetime.now()
week = args.week if args.week is not None else select_week(now)["week"]
year = "2025"

print(f"Generating newsletter for week {week} of the {year} season.")
football_api_uri = f"http://localhost:3000/scoreboard/football/fbs/{year}/{week}/all_conf"

def fetch_scores():
    response = requests.get(football_api_uri)
    if response.status_code == 200:
        return response.json()['games']
    else:
        raise RuntimeError(f"Error fetching scores: {response.status_code}")
    
def filter_to_conference(game, conference):
    return any(
        team_conference['conferenceName'] == conference
        for team_conference in game['game']['home']['conferences']
    ) or any(
        team_conference['conferenceName'] == conference
        for team_conference in game['game']['away']['conferences']
    )

def get_games():
    return list(filter(lambda game: filter_to_conference(game, "ACC"), fetch_scores()))


if __name__ == "__main__":
    games = get_games()
    print(f"Found {len(games)} games in the ACC conference.")

    client = anthropic.Anthropic(
        # defaults to os.environ.get("ANTHROPIC_API_KEY")
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )

    # Replace placeholders like {{SEARCH_FUNCTIONS}} with real values,
    # because the SDK does not support variables.
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=20000,
        temperature=1,
        system="You are a sports research assistant tasked with creating a comprehensive newsletter about recent ACC (Atlantic Coast Conference) football games.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
                            Your goal is to identify ACC games that occurred in the past 7 days and create a detailed newsletter with game results, news, and commentary.
                            
                            **Important Notes:**
                            - The ACC (Atlantic Coast Conference) includes:
                              - Clemson
                              - Duke
                              - Universrity of North Carolina at Chapel Hill
                              - NC State
                              - Wake Forest
                              - Virginia
                              - Georgia Tech
                              - Florida State
                              - Miami
                              - Virginia Tech
                              - Boston College
                              - Pittsburgh
                              - Syracuse
                              - Notre Dame (partial member)
                              - Louisville
                              - Southern Methodist University (SMU)
                              - University of California, Berkeley (Cal)
                              - Stanford
                            - "Past week" means the last 7 days from today's date
                            - Focus on both basketball and football games as appropriate for the current season
                            - DO NOT use any functions other than those provided to you
                            
                            **Step-by-Step Process:**
                            
                            1. **Gather Game Information**: For each game provided, collect:
                              - Teams that played
                              - Final scores
                              - Date and location of game
                              - Key statistics or highlights
                              
                            **Newsletter Format Requirements:**
                            
                            Your newsletter should contain exactly three sections:
                            
                            **Acc Football Newsletter - Week {week} Recap**
                            **Game Results Table**
                            Create a table with the following columns:
                            - Date
                            - Teams (Winner vs Loser)
                            - Final Score
                            - Location/Venue
                            
                            **News Summary**
                            Provide a summary of significant news stories related to the games, including:
                            - Major storylines
                            - Player performances
                            - Coaching highlights
                            - Any controversies or notable events
                            
                            **Commentary Summary**
                            Summarize expert analysis and commentary about:
                            - Game implications for conference standings
                            - Team performance analysis
                            - Looking ahead to upcoming games
                            - Broader trends in ACC play
                            
                            **Output Format:**
                            - Use Markdown formatting for the entire newsletter
                            - Structure your final response with clear section headers and organize the information in an easy-to-read newsletter format. 
                            - If you cannot find any ACC games from the past week, clearly state this in your response.
                            
                            Your final newsletter should be comprehensive yet concise, providing readers with a complete picture of recent ACC action. 
                            Focus on factual reporting while incorporating the most insightful commentary and analysis you can find. 
                            
                            The specific games to include are {games}. This is for week {week} of the {year} season.
                        """
                    }
                ]
            }
        ]
    )

    initial_content = message.content[0].text
    
    # Second pass: fact-checking, proofreading, and editing
    print("Running fact-check, proofreading, and editing pass...")
    edit_message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=20000,
        temperature=0.3,
        system="You are an expert editor and fact-checker for sports journalism. Your task is to review, fact-check, proofread, and improve the provided ACC football newsletter.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
                            Please review the following ACC football newsletter and improve it by:
                            
                            **Fact-Checking:**
                            - Verify team names are spelled correctly and consistently
                            - Check that scores and game details are accurate based on the provided data
                            - Ensure conference affiliations are correct
                            - Validate dates and venues when possible
                            
                            **Proofreading:**
                            - Fix any grammatical errors
                            - Correct spelling mistakes
                            - Improve sentence structure and clarity
                            - Ensure consistent formatting
                            
                            **Editorial Improvements:**
                            - Enhance readability and flow
                            - Improve transitions between sections
                            - Make the writing more engaging while maintaining factual accuracy
                            - Ensure the tone is professional yet accessible
                            - Add any missing context that would help readers understand the significance of games
                            
                            **Original Game Data for Reference:**
                            {games}
                            
                            **Newsletter to Review and Edit:**
                            {initial_content}
                            
                            Please return the improved version of the newsletter with all corrections and enhancements applied. Maintain the same overall structure and format but improve the quality throughout.
                        """
                    }
                ]
            }
        ]
    )
    
    final_content = edit_message.content[0].text
    
    now = datetime.datetime.now()
    with open(f"./content/{now.strftime('%Y')}week{week}.md", "w") as f:
        f.write(f"""Title: ACC Football Newsletter - {now.strftime('%Y')} Week {week}
Date: {now.strftime("%Y-%m-%d")}
Category: Newsletter
Tags: [ACC, Football, Newsletter]
""")
        f.write(final_content)
    print(f"Newsletter written to {now.strftime('%Y')}week{week}.md (with fact-checking and editing)")
