import config
import os

# Module to interact with reddit API
import praw

# For cooldown periods
import time

# To fetch JSON data from the Oxford Dictionary API
import requests
import json

app_id = "" # License id from Oxford Dictionary API website
app_key = "" # License key from Oxford Dictionary API website
language = 'en' # Dictionary language setting

# Function to log bot into reddit
def bot_login():
    r = praw.Reddit(username=config.username,
            password=config.password,
            client_id=config.client_id,
            client_secret=config.client_secret,
            user_agent="") # Log-in info from config file
    print("Log-in Successful!") # Message to confirm successful Log-in
    return r # Returns successful log-in instance

def save_list():

    # If a record of comments replied to doesn't exist, create an empty list
    if not os.path.isfile("comments_replied_to.txt"):
        comments_replied_to = []

    # Otherwise, open the record and append it
    else:
        with open("comments_replied_to.txt","r") as f:
            comments_replied_to = f.read()
            comments_replied_to = comments_replied_to.split("\n")

    # Return a master list of comments replied to
    return comments_replied_to


# Main function that runs the bot
def run_bot(r):

    # 'test' = name of subreddit, limit = maximum number of comments processed
    for comment in r.subreddit('test').comments(limit=25):

        # To prevent repeated and self replies
        if "!meaning" in comment.body and comment.id not in comment_list and not comment.author == r.user.me():

            # Confirmation of found comment
            print("Comment Found!")

            # Split the comment into individual words
            words = comment.body.split(' ')

            # Iterate through each individual word
            for word in words:

                # Process each word except the calling key
                if word != "!meaning":

                    # Fetch word information from the Oxford Dictionary API
                    url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word.lower()

                    # Convert JSON data & comment the extracted word definition
                    r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
                    data = json.dumps(r.json())
                    data1 = json.loads(data)
                    comment.reply(''.join(data1['results'][0]['id']) + ": "+ ''.join(data1['results'][0]['lexicalEntries'][1]['entries'][0]['senses'][0]['definitions'])
                                  )
                    # To by-pass the Reddit 5 second cooldown between comments for comments with multiple words
                    time.sleep(5)

            # Append comment id to master list
            comment_list.append(comment.id)
            with open ("comments_replied_to.txt", "a") as f:
                f.write(comment.id + "\n")

    # Sleep for 10 seconds to prevent spam
    print("Sleeping for 10 seconds!")
    time.sleep(10)

# Log-in instance
r = bot_login()

# List of comments
comment_list = save_list()

# Main loop
while True:
    run_bot(r)