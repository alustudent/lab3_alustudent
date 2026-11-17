#!/usr/bin/env bash
# Prints the Top 5 Most Active Users (most tweets) in a Twitter CSV.
# Usage: bash feed-analyzer.sh [twitter_dataset.csv]

FILE="${1:-twitter_dataset.csv}"

if [ ! -e "$FILE" ]; then
    echo "Error: '$FILE' was not found." >&2
    echo "Usage: bash feed-analyzer.sh [twitter_dataset.csv]" >&2
    exit 1
fi
if [ ! -f "$FILE" ]; then
    echo "Error: '$FILE' is not a regular file." >&2
    exit 1
fi
if [ ! -s "$FILE" ]; then
    echo "Error: '$FILE' is empty." >&2
    exit 1
fi

# Username must be the 2nd column, because cut -f2 below depends on it
HEADER_COLUMN=$(head -n 1 "$FILE" | tr -d '\r' | sed 's/^\xEF\xBB\xBF//' | cut -d',' -f2)
if [ "$HEADER_COLUMN" != "Username" ]; then
    echo "Error: expected 'Username' as the 2nd column of '$FILE', found '$HEADER_COLUMN'." >&2
    exit 1
fi

echo "Top 5 Most Active Users in $FILE"
echo "Tweets  Username"

# Tweet texts are quoted and can span several lines, so awk keeps only the first line
# of each record: a new record starts only when every quote opened so far is closed.
# Then: take the Username column, drop blanks, count each user, rank by count (ties A-Z).
tail -n +2 "$FILE" \
    | tr -d '\r' \
    | awk '{ if (!in_quotes) print; if (gsub(/"/, "&") % 2 == 1) in_quotes = !in_quotes }' \
    | cut -d',' -f2 \
    | grep -v '^[[:space:]]*$' \
    | sort \
    | uniq -c \
    | sort -k1,1nr -k2,2 \
    | head -n 5
