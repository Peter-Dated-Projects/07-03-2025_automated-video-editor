from source.redditscraper import RedditScraperBot


import os
from dotenv import load_dotenv

load_dotenv("../.env")

reddit_scraper = RedditScraperBot(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_SECRET_KEY"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)


print(reddit_scraper.get_new_subreddit_posts("learnpython", limit=5))
