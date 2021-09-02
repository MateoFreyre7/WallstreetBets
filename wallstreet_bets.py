"""
AUTHOR: Matt Freyre
"""

import pandas as pd
import numpy as np
import json
import praw
import re
import matplotlib.pyplot as plt

#### Constants ####
SUBREDDIT = 'wallstreetbets'
CLIENT = json.load(open('client_secrets.json', 'r'))
reddit = praw.Reddit(client_id=CLIENT['client_id'], \
                         client_secret=CLIENT['client_secret'], \
                         user_agent=CLIENT['user_agent'])

# extract stock symbols from text file and create a regex pattern
STOCK_REGEX = ''
with open('all_tickers.txt') as file:
    for line in file.readlines():
        STOCK_REGEX += line + '|'
STOCK_REGEX = STOCK_REGEX[:-1].replace('\n','')

#### Data Extraction ####
id, title, comment_list = '','',[]
subr = reddit.subreddit(SUBREDDIT)

# get today's daily discussion submission title and id
for post in subr.hot(limit=1):
    id = post.id
    title = post.title

# get today's daily discussion submission and associated top level comments only
submission = reddit.submission(id=id)
submission.comments.replace_more(limit=2)
for comment in submission.comments:
    print(comment.body)
    comment_list.append(comment.body)

# create data frame of reddit comments
df = pd.DataFrame(np.array(comment_list))

#### Clean Data ####
# remove emojis
df[0] = df[0].str.replace('[^\w\s#@/:%.,_-]', '', flags=re.UNICODE)

# remove special characters
df[0] = df[0].str.replace('\n|,|\?|\!|\$', ' ', regex=True)

# extract all occurrences of stock symbols
stocks = df[0].str.extractall(r'\b(?:({}))\b'.format(STOCK_REGEX)).value_counts() 

# convert stocks series to dataframe
top_stocks = stocks.to_frame(name='Counts')
top_stocks.reset_index(inplace=True)
top_stocks.rename(columns = {0:'Stocks'}, inplace=True)

# create a data frame with the dictionary results and filter out results that have a count of less than 5
top_stocks = top_stocks[top_stocks['Counts'] > 50]
top_stocks.sort_values(by=['Counts'], ascending=False, inplace=True, ignore_index=True) 

# create plot
title_fragments = title.split(',')
top_stocks.plot(x='Stocks', y='Counts', kind='bar', color='green', title='Most Talked About Stock on Wallstreetbets' + title_fragments[-2] + title_fragments[-1])
plt.show()