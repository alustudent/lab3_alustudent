import csv
import sys
import os

DEFAULT_FILE = "twitter_dataset.csv"
REQUIRED_COLUMNS = ["Username", "Text", "Retweets", "Likes"]
COUNT_COLUMNS = ["Likes", "Retweets"]
TOP_N = 10


def load_raw_data(filename):
    """
    Loads the CSV file into a list of dictionaries exactly as it is (messy).
    """
    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found.")
        print(f"Download {DEFAULT_FILE} from Kaggle and put it next to this script,")
        print("or pass its path: python3 data-detective.py path/to/twitter_dataset.csv")
        sys.exit(1)
    if not os.path.isfile(filename):
        print(f"Error: '{filename}' is a folder, not a CSV file.")
        sys.exit(1)

    raw_tweets = []
    try:
        # utf-8-sig also strips the invisible BOM that Excel adds to the first column name
        with open(filename, mode='r', encoding='utf-8-sig', newline='') as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                print(f"Error: '{filename}' is empty. It needs a header row like:")
                print("Tweet_ID,Username,Text,Retweets,Likes,Timestamp")
                sys.exit(1)

            reader.fieldnames = [name.strip() for name in reader.fieldnames]
            missing = [name for name in REQUIRED_COLUMNS if name not in reader.fieldnames]
            if len(missing) > 0:
                print(f"Error: '{filename}' is missing the column(s): {', '.join(missing)}")
                print(f"Columns found: {', '.join(reader.fieldnames)}")
                sys.exit(1)

            for row in reader:
                raw_tweets.append(row)
    except UnicodeDecodeError:
        print(f"Error: '{filename}' is not a UTF-8 text file. Re-download the CSV from Kaggle.")
        sys.exit(1)
    except csv.Error as error:
        print(f"Error: '{filename}' is not valid CSV near line {reader.line_num}: {error}")
        sys.exit(1)
    except OSError as error:
        print(f"Error: could not read '{filename}': {error.strerror}")
        sys.exit(1)

    return raw_tweets


def to_count(raw_value):
    """
    Converts a Likes/Retweets field to an int.
    Returns None when the field is blank or not a whole number of 0 or more.
    """
    text = (raw_value or "").strip()
    try:
        number = int(text)
    except ValueError:
        return None
    if number < 0:
        return None
    return number


def clean_data(tweets):
    """
    QUEST 1: Handle missing fields.
    Check for missing text, and replace empty likes/retweets with 0.
    Return a clean list of tweets.
    """
    clean_tweets = []
    removed = 0
    fixed = 0

    for tweet in tweets:
        # A short row gives None for the missing columns, so treat None as blank
        text = (tweet.get("Text") or "").strip()
        if text == "":
            removed += 1
            continue

        clean_tweet = {
            "Username": (tweet.get("Username") or "").strip(),
            "Text": text,
        }
        was_fixed = False
        if clean_tweet["Username"] == "":
            clean_tweet["Username"] = "unknown_user"
            was_fixed = True

        for column in COUNT_COLUMNS:
            number = to_count(tweet.get(column))
            if number is None:
                number = 0
                was_fixed = True
            clean_tweet[column] = number

        if was_fixed:
            fixed += 1
        clean_tweets.append(clean_tweet)

    print(f"Removed {removed} row(s) with no Text.")
    print(f"Fixed {fixed} row(s): blank or invalid Likes/Retweets set to 0, blank Username set to unknown_user.")
    print(f"{len(clean_tweets)} clean tweet(s) ready for analysis.")
    return clean_tweets


def find_viral_tweet(tweets):
    """
    QUEST 2: Loop through the list to find the tweet with the highest 'Likes'.
    Do not use the max() function.
    """
    if len(tweets) == 0:
        return None

    viral = tweets[0]
    for tweet in tweets:
        if tweet["Likes"] > viral["Likes"]:
            viral = tweet
    return viral


def custom_sort_by_likes(tweets):
    """
    QUEST 3: Implement Bubble Sort or Selection Sort to sort the list
    by 'Likes' in descending order. NO .sort() allowed!
    """
    # Selection sort on a copy, so the caller's list keeps its original order
    ranked = list(tweets)
    size = len(ranked)

    for position in range(size - 1):
        most_liked = position
        for candidate in range(position + 1, size):
            if ranked[candidate]["Likes"] > ranked[most_liked]["Likes"]:
                most_liked = candidate
        if most_liked != position:
            ranked[position], ranked[most_liked] = ranked[most_liked], ranked[position]

    return ranked


def search_tweets(tweets, keyword):
    """
    QUEST 4: Search for a keyword and extract matching tweets into a new list.
    """
    # Case-insensitive, so "python" also finds "Python" and "PYTHON"
    keyword = keyword.lower()
    matches = []
    for tweet in tweets:
        if keyword in tweet["Text"].lower():
            matches.append(tweet)
    return matches


def ask_for_keyword():
    """Asks until the user types a non-empty word. Returns None if input ends (Ctrl+D / Ctrl+C)."""
    while True:
        try:
            keyword = input("Enter a word to search for (e.g. Python or music): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nNo search word entered, so the search was skipped.")
            return None
        if keyword != "":
            return keyword
        print("Error: the search word can't be empty. Type a word such as: music")


def indent(text):
    # Many tweets span several lines, so indent every line, not just the first
    return "    " + text.replace("\n", "\n    ")


def print_tweet(tweet, label=""):
    print(f"{label}@{tweet['Username']} | Likes: {tweet['Likes']} | Retweets: {tweet['Retweets']}")
    print(indent(tweet['Text']))


def print_heading(title):
    print(f"\n=== {title} ===")


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE

    # Load the messy data
    dataset = load_raw_data(filename)
    print(f"Loaded {len(dataset)} raw tweets.\n")
    if len(dataset) == 0:
        print(f"Error: '{filename}' has a header but no tweets. Add some rows and try again.")
        sys.exit(1)

    print_heading("Quest 1: The Data Auditor")
    clean_dataset = clean_data(dataset)
    if len(clean_dataset) == 0:
        print("Error: no tweets are left after cleaning, because every row was missing its Text.")
        sys.exit(1)

    print_heading("Quest 2: The Viral Post")
    viral = find_viral_tweet(clean_dataset)
    print(f"Username: {viral['Username']}")
    print(f"Likes:    {viral['Likes']}")
    print("Text:")
    print(indent(viral['Text']))

    print_heading(f"Quest 3: Top {TOP_N} Most Liked Tweets")
    print(f"Sorting {len(clean_dataset)} tweets with selection sort (this can take a few seconds)...")
    ranked = custom_sort_by_likes(clean_dataset)
    top_tweets = ranked[:TOP_N]
    if len(top_tweets) < TOP_N:
        print(f"Only {len(top_tweets)} tweet(s) available, showing all of them.")
    for rank in range(len(top_tweets)):
        print_tweet(top_tweets[rank], f"{rank + 1}. ")

    print_heading("Quest 4: The Content Filter")
    keyword = ask_for_keyword()
    if keyword is not None:
        matches = search_tweets(clean_dataset, keyword)
        print(f"{len(matches)} tweet(s) contain \"{keyword}\".")
        for tweet in matches:
            print_tweet(tweet)
