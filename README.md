# rquery - reddit query

> rquery fetches given reddit users's posts/submissions and puts it in a local sqlite db.

## Usage

```
usage: rquery.py [-h] --id ID --secret SECRET [--limit LIMIT] [--db DB]
                 user [user ...]

Puts given users's posts/submissions into a sqlite db.

positional arguments:
  user             Users you wanna store in sqlite

optional arguments:
  -h, --help       show this help message and exit
  --id ID          reddit client id
  --secret SECRET  reddit client secret
  --limit LIMIT    limit for how many comments/submissions to fetch
  --db DB          db path
```

Sample query:

```sql
SELECT 
submissions.user as submitter, 
comments.user as commenter,
submissions.url as submission_url, 
comments.url as comment_url,
comments.body as comment_body
FROM submissions
INNER JOIN comments ON comments.submission_id = submissions.id
WHERE commenter != submitter;
```
Output:

![](https://i.imgur.com/7Cari5G.png)