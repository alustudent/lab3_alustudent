# Lab 3: The Social Media Data Detective

Cleans and analyses a messy Twitter dataset in Python without `.sort()`, `sorted()` or `max()`, then finds the most active users in a single Bash pipeline.

## Files

| File | What it does |
|---|---|
| `data-detective.py` | Python app for the four quests |
| `feed-analyzer.sh` | Bash script that prints the Top 5 Most Active Users |
| `twitter_dataset.csv` | Dataset from Kaggle (`Tweet_ID, Username, Text, Retweets, Likes, Timestamp`) |
| `Readme.md` | This file |

## How to run

Requires Python 3 and Bash. Only the standard library is used (`csv`, `sys`, `os`), so nothing needs installing.

```bash
python3 data-detective.py                    # reads twitter_dataset.csv
python3 data-detective.py path/to/other.csv  # or any CSV with the same columns

bash feed-analyzer.sh                        # reads twitter_dataset.csv
bash feed-analyzer.sh path/to/other.csv
```

During Quest 4 the program asks for a search word. The Kaggle tweets are generated filler text, so `Python` finds 0 tweets. Words like `music`, `party` or `history` find around 330–350 each.

## The quests (`data-detective.py`)

1. **The Data Auditor:** `clean_data()` loops over every row and builds a new, clean list.
   - A row with no `Text` is removed.
   - A blank `Likes` or `Retweets` is replaced with `0`. So is anything that isn't a whole number of 0 or more (e.g. `abc`, `-4`).
   - A blank `Username` becomes `unknown_user`.
   - `Likes` and `Retweets` are cast with `int()`, so every later comparison is numeric, not text.
   - Prints how many rows were removed and how many were fixed.
2. **The Viral Post:** `find_viral_tweet()` starts with the first tweet and keeps the one with more `Likes` as it loops. No `max()`. Prints the Username, Likes and Text. In this dataset about 100 tweets share the top score of 100 Likes. Because the loop only switches on strictly more Likes, the first of them in the file wins (`ojordan`).
3. **The Algorithm Builder:** `custom_sort_by_likes()` is a **selection sort**, highest `Likes` first. For each position it finds the most-liked remaining tweet and swaps it into place. It sorts a copy, so the original list is unchanged. The result is sliced to the top 10. Ties are picked in file order, the same way as Quest 2, so the No. 1 tweet is the viral post. Sorting all 10,000 tweets takes about 2–3 seconds.
4. **The Content Filter:** `search_tweets()` builds a brand new list with `append()` of every tweet whose Text contains the word. The match ignores case, so `python` also finds `Python`. Prints `len()` of that list, then the tweets.

## The shell script (`feed-analyzer.sh`)

```bash
tail -n +2 "$FILE" | tr -d '\r' \
  | awk '{ if (!in_quotes) print; if (gsub(/"/, "&") % 2 == 1) in_quotes = !in_quotes }' \
  | cut -d',' -f2 | grep -v '^[[:space:]]*$' | sort | uniq -c | sort -k1,1nr -k2,2 | head -n 5
```

- `tail` skips the header.
- **`awk` keeps only the first line of each tweet.** Most tweets (9,753 of 10,000) have text spread over several lines inside quotes. Without this step, `cut -f2` would read a sentence fragment such as `76` or `44` as a username. The `awk` counts quote characters: a new record can only start once every opened quote is closed.
- `cut -f2` takes the Username column and `grep` drops blank usernames.
- `sort | uniq -c` counts the tweets per user.
- `sort -k1,1nr -k2,2` ranks by count, highest first, with ties in A–Z order so the output is the same every run.
- `head` keeps the top 5.

Output on the Kaggle dataset (matches a count of all 10,000 records with Python's `csv` module):

```
      6 pjohnson
      5 awilliams
      5 nbrown
      4 amiller
      4 fsmith
```

Several other users also have 4 tweets. With ties in A–Z order, `amiller` and `fsmith` take the last two places.

## Error handling

Every failure prints a message saying what went wrong and how to fix it, and the program exits with code `1` instead of crashing.

| Situation | Python | Bash |
|---|---|---|
| File doesn't exist / is a folder | ✅ | ✅ |
| Empty file | ✅ | ✅ |
| Header but no rows | ✅ | – (prints nothing) |
| Required column missing / Username not 2nd | ✅ | ✅ |
| Not UTF-8 or malformed CSV | ✅ | – |
| Missing Text, blank or invalid Likes/Retweets, short rows | ✅ cleaned and counted | – |
| Every row missing Text | ✅ | – |
| Empty search word | ✅ asks again | – |
| Ctrl+D / Ctrl+C at the search prompt | ✅ skips the search | – |
