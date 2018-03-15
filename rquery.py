from typing import List
import re
import sqlite3
import argparse
import praw

parser = argparse.ArgumentParser(description='Puts given users\'s posts/submissions into a sqlite db.')
parser.add_argument('--id', required=True, type=str, help='reddit client id')
parser.add_argument('--secret', required=True, type=str, help='reddit client secret')
parser.add_argument('--limit', type=int, help='limit for how many comments/submissions to fetch', default=100)
parser.add_argument('--db', type=str, help='db path', default='reddit.sqlite')
parser.add_argument('users', metavar='user', type=str, nargs='+', help='Users you wanna store in sqlite')
args = parser.parse_args()

LIMIT = args.limit
reddit = praw.Reddit(client_id=args.id,
                     client_secret=args.secret, user_agent='linux:rquery:v0.0.1')


class Store(object):
    def __init__(self, dbpath):
        conn = sqlite3.connect(dbpath)
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS comments (
            submission_id varchar(255),
            user varchar(255),
            url text,
            body text
        );
        CREATE TABLE IF NOT EXISTS submissions (
            id varchar(255),
            user varchar(255),
            is_self boolean,
            url text
        );
        ''')
        self.conn = conn

    def save_comment(self, sid: str, user: str, url: str, body: str) -> None:
        self.conn.execute('INSERT INTO comments VALUES (?,?,?,?);', (sid, user, url, body))
        self.conn.commit()

    def save_submission(self, id: str, user: str, is_self: bool, url: str) -> None:
        self.conn.execute('INSERT INTO submissions VALUES (?,?,?,?);', (id, user, is_self, url))
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()


class UserExtractor(object):
    """Extracts posts/submissions of users and stores them."""

    def __init__(self, store: Store, reddit: praw.Reddit, users: List[str]):
        self.users = users
        self.store = store
        self.reddit = reddit

    def extract_comments(self, redditor: praw.models.Redditor) -> None:
        print("Extracting comments of %s" % redditor.name)
        for comment in redditor.comments.new(limit=LIMIT):
            self.store.save_comment(
                comment.submission.id, redditor.name, "https://www.reddit.com"+comment.permalink, comment.body)

    def extract_submissions(self, redditor: praw.models.Redditor) -> None:
        print("Extracting submissions of %s" % redditor.name)
        for submission in redditor.submissions.new(limit=LIMIT):
            self.store.save_submission(
                submission.id, redditor.name, submission.is_self, submission.url)

    def extract(self):
        for user in self.users:
            redditor = self.reddit.redditor(user)
            self.extract_comments(redditor)
            self.extract_submissions(redditor)
            print("%s done." % user)


store = Store(args.db)
user_extractor = UserExtractor(store, reddit, args.users)
user_extractor.extract()
store.close()
print("Extraction complete. Stored to %s" % args.db)
