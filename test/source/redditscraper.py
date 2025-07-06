# change cwd to base directory of repo
import os
import sys
from pathlib import Path
import praw

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------- #


class RedditScraperBot:
    def __init__(self):
        self.client = praw.Reddit(
            client_id=os.environ.get("REDDIT_CLIENT_ID"),
            client_secret=os.environ.get("REDDIT_SECRET_KEY"),
            user_agent=os.environ.get("REDDIT_USER_AGENT"),
        )

    # ---------------------------------------------------------------- #

    def get_new_subreddit_posts(self, subreddit_name, limit=10):
        """
        Fetches the most recent posts from a given subreddit.
        :param subreddit_name: Name of the subreddit to fetch posts from.
        :param limit: Number of posts to fetch.
        :return: List of posts.
        """
        subreddit = self.client.subreddit(subreddit_name)
        return list(subreddit.new(limit=limit))

    def get_top_subreddit_posts(self, subreddit_name, time_filter="all", limit=10):
        """
        Fetches the top posts from a given subreddit.
        :param subreddit_name: Name of the subreddit to fetch posts from.
        :param time_filter: Time filter for top posts (e.g., "day", "week", "month", "year", "all").
        :param limit: Number of posts to fetch.
        :return: List of top posts.
        """
        subreddit = self.client.subreddit(subreddit_name)
        return list(subreddit.top(time_filter=time_filter, limit=limit))

    def get_hot_subreddit_posts(self, subreddit_name, limit=10):
        """
        Fetches the hot posts from a given subreddit.
        :param subreddit_name: Name of the subreddit to fetch posts from.
        :param limit: Number of posts to fetch.
        :return: List of hot posts.
        """
        subreddit = self.client.subreddit(subreddit_name)
        return list(subreddit.hot(limit=limit))

    # ---------------------------------------------------------------- #

    def extract_post_details(self, post):
        """
        Extracts details from a Reddit post.
        :param post: A Reddit post object.
        :return: A dictionary containing the post's title, author, score, and URL.
        """
        return {
            "title": post.title,
            "author": str(post.author),
            "score": post.score,
            "url": post.url,
            "created_utc": post.created_utc,
            "num_comments": post.num_comments,
        }

    def extract_post_comments(self, post, limit: int = 10):
        """
        Extracts comments from a Reddit post.
        :param post: A Reddit post object.
        :param limit: Number of comments to fetch.
        :return: List of comments.
        """
        post.comments.replace_more(limit=0)
        comments = post.comments.list()
        return [comment.body for comment in comments[:limit]]

    def extract_post_media(self, post):
        """
        Extracts media from a Reddit post.
        :param post: A Reddit post object.
        :return: URL of the media if available, otherwise None.
        """
        if hasattr(post, "media") and post.media:
            return post.media.get("reddit_video", {}).get("fallback_url", None)
        return None


# ---------------------------------------------------------------- #


if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parent.parent
    os.chdir(root_dir)
    print("Working in directory:", os.getcwd())

    # Initialize the RedditScraper
    scraper = RedditScraperBot()

    # fetch the 10 most recent posts from AITAH subreddit and print them out
    _targets = scraper.get_new_subreddit_posts("AITAH", limit=10)
    for i, t in enumerate(_targets):
        print(t.title)
    _targets = scraper.get_top_subreddit_posts("AITAH", limit=10)
    for i, t in enumerate(_targets):
        print(t.title)
    _targets = scraper.get_hot_subreddit_posts("AITAH", limit=10)
    for i, t in enumerate(_targets):
        print(t.title)
    # print the number of posts fetched
    print(f"Fetched {len(_targets)} posts from AITAH subreddit.")
