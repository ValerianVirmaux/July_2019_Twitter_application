#!/usr/bin/env python
# coding: utf-8

# In[4]:


import tweepy
from tweepy import OAuthHandler
import json
import datetime as dt
import time
import os
import sys
import nltk
from nltk.tokenize import TweetTokenizer


# In[5]:


import pymongo as pymongo
from pymongo import MongoClient

MONGO_HOST= 'mongodb://localhost/twitterdb'
client = MongoClient(MONGO_HOST)
db = client.twitterdb


# In[6]:


choice = []
question = 'COMSUMER_KEY : '
sys.stdout.write(question)
choice = input(), choice
global CONSUMER_KEY
CONSUMER_KEY = choice[0]

question = 'CONSUMER_SECRET : '
sys.stdout.write(question)
choice = input(), choice
global CONSUMER_SECRET
CONSUMER_SECRET = choice[0]


# In[7]:


from langdetect import detect
import datetime


def download_last_tweets():
    
    auth = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    if (not api):
        print ("Can't Authenticate")
        sys.exit(-1)
        
    MONGO_HOST= 'mongodb://localhost/twitterdb'
    client = MongoClient(MONGO_HOST)
    db = client.twitterdb


    db.upr_hastag.drop()
    now = datetime.datetime.now()

    maxTweets = 10000000 
    tweetsPerQry = 100 
    sinceId = None
    max_id = -1
    tweetCount = 0
    
    while tweetCount < maxTweets:
        try:
            if (max_id <= 0):
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry)
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                                since_id=sinceId)
            else:
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry, 
                                            max_id=str(max_id - 1))
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry, 
                                            max_id=str(max_id - 1), since_id=sinceId)
            if not new_tweets:
                break
            for tweet in new_tweets:
                date_tweet = tweet.created_at
                diff = now - date_tweet
                hours = diff.total_seconds() / 3600
                if hours <= int(period) * 24:
                    x = tweet.text
                    try:
                        lang = detect(x)
                        if lang == filter_lang:
                            datajson = tweet._json
                            db.upr_hastag.insert_one(datajson)
                    except:
                        pass
                    
            tweetCount += len(new_tweets)
            max_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            print("some error : " + str(e))
            break
            
    print(db.upr_hastag.estimated_document_count(), 'tweet in upr_hastag')


# In[8]:


import nltk
from nltk.stem import WordNetLemmatizer
import stop_words
from stop_words import get_stop_words
import re
import string

#sw = get_stop_words('french')
#sw = get_stop_words(filter_lang)

lemma = WordNetLemmatizer()
All = []
def clean_text_and_tokenize(line):
    sw = get_stop_words(filter_lang)
    line   = re.sub(r'\$\w*', '', line)  # Remove tickers
    line   = re.sub(r'http?:.*$', '', line)
    line   = re.sub(r'https?:.*$', '', line)
    line   = re.sub(r'pic?.*\/\w*', '', line)
    line = re.sub(r'[' + string.punctuation + ']+', ' ', line)

    tokens = TweetTokenizer(strip_handles=True, reduce_len=True).tokenize(line)
    tokens = [w.lower() for w in tokens if w not in sw and len(w) > 2 and w.isalpha()]
    tokens = [lemma.lemmatize(word) for word in tokens]
    
    return tokens


# In[9]:


def getCleanedWords(lines):
    words = []
    for line in lines:
        words += clean_text_and_tokenize(line)
    return words


# In[10]:


def lexical_diversity(tokens):
    return 1.0 * len(set(tokens)) / len(tokens)


# In[11]:


def average_words(lines):
    total_words = sum([len(s.split()) for s in lines])
    print('Tweet contain an average of', int(1.0 * total_words / len(lines)), 'words')


# In[12]:


from prettytable import PrettyTable
from collections import Counter

def top_words(words, top=10):
    pt = PrettyTable(field_names=['Words', 'Count'])
    c = Counter(words)
    [pt.add_row(kv) for kv in c.most_common()[:top]]
    pt.align['Words'], pt.align['Count'] = 'l', 'r'  # Set column alignment
    print(pt)


# In[13]:


def clean_tweet(tweet):
    return " ".join(clean_text_and_tokenize(tweet))


# In[14]:


from textblob import TextBlob
from textblob_fr import PatternTagger, PatternAnalyzer

def sentiment_analysis_basic(tweets):
    positive_tweets = 0
    neutral_tweets  = 0
    negative_tweets = 0

  
    for tweet in tweets:
        
        if filter_lang == 'fr':
            
            analysis  = TextBlob(tweet, pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())

            if analysis.sentiment[0] > 0:
                positive_tweets += 1
            elif analysis.sentiment[0] == 0:
                neutral_tweets += 1
            else:
                negative_tweets += 1

        if filter_lang == 'en':
            
            analysis  = TextBlob(tweet)

            if analysis.sentiment.polarity > 0:
                positive_tweets += 1
            if analysis.sentiment.polarity == 0:
                neutral_tweets += 1
            else:
                 negative_tweets += 1

        
    total_tweets_analysed      = positive_tweets + neutral_tweets + negative_tweets
    positive_tweets_percentage = round(positive_tweets / total_tweets_analysed * 100, 1)
    neutral_tweets_percentage  = round(neutral_tweets  / total_tweets_analysed * 100, 1)

    print("\nNo. of positive tweets = {} Percentage = {}".format(
        positive_tweets, positive_tweets_percentage))
    print("No. of neutral tweets  = {} Percentage = {}".format(
        neutral_tweets, neutral_tweets_percentage))
    print("No. of negative tweets = {} Percentage = {}".format(
        negative_tweets, 100 - (positive_tweets_percentage + neutral_tweets_percentage)))
    
    First()
    


# In[15]:


def remove_non_ascii(text):
    return ''.join(i for i in text if ord(i) < 128)


# In[16]:


from langdetect import detect

def fetchTweetsFromFile():
    fields = []
    rows   = []
    n = 0

    for row in db.upr_hastag.find():
        x = row.get("text")
        lang = detect(x)
        if lang == filter_lang:
            n += 1
            rows.append(x)
    print("Total no. of tweets: ", n)
    return rows


# In[17]:


def main_H():
   
    choose_query()
    
    download_last_tweets() # Get the Tweets
    #twitter_handle = sys.argv[1]
    tweet_rows     = fetchTweetsFromFile() # Keep french tweets

    tweets = [row for row in tweet_rows] # Decompose Tweets
    
    average_words(tweets)

    words = getCleanedWords(tweets) # Clean Tweets
    print("Lexical diversity =", lexical_diversity(words))
    
    top_words(words) # Get Top Worlds

    cleaned_tweets = []
    for tweet in tweets:
        cleaned_tweets.append(clean_tweet(tweet))    
    sentiment_analysis_basic(cleaned_tweets)


# In[18]:


def choose_query():
    choice = []
    
    if filter_lang == 'fr':
        question = 'Quel(s) mot(s) clef(s) souhaitez vous suivre ? Help (SOS) - Back (B)\n'
    if filter_lang == 'en':
        question = 'Which keyword(s) would you like to follow ? Help (SOS) - Back (B)\n'
    
    print('___')
    sys.stdout.write(question)
    print('')
    choice = input(), choice
    global searchQuery
    searchQuery = choice[0]
    
    if searchQuery == 'SOS':
        help_historic()
        choose_query()
    if searchQuery == 'B':
        First()
    if searchQuery == 'exit':
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
        
        
    else:
       

        if filter_lang == 'fr':
            question = 'Combien de jours souhaitez vous chercher ? \n           ***De 1 a 7***\n'
        if filter_lang == 'en':
            question = 'How many days back would you like to check ? \n           ***From 1 to 7***\n'

        print('___')
        sys.stdout.write(question)
        print('')
        choice = input(), choice
        global period
        period = choice[0]
        
        if period == 'exit':
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        


# In[20]:


def help_historic():
    print(tabulate([['watching now', 'containing both “watching” and “now”. This is the default operator.'], 
                    ['“happy hour”', 'containing the exact phrase “happy hour”.'], 
                    ['love OR hate', 'containing either “love” or “hate” (or both).'], 
                    ['beer -root', 'containing “beer” but not “root”.'], 
                    ['#haiku', 'containing the hashtag “haiku”.'],
                    ['from:interior', 'sent from Twitter account “interior”.'],
                    ['list:NASA/astronauts-in-space-now', 'sent from a Twitter account in the NASA list astronauts-in-space-now'],
                    ['to:NASA', 'a Tweet authored in reply to Twitter account “NASA”.'],
                    ['@NASA', 'mentioning Twitter account “NASA”.'],
                    ['traffic ?', 'containing “traffic” and asking a question.']], 
                   headers=['Operator', 'Finds Tweets...']))
    print('')


# In[19]:


from textblob import TextBlob
from textblob_fr import PatternTagger, PatternAnalyzer
import pprint

positif = 0
neutre = 0
negatif = 0

class StreamListener(tweepy.StreamListener):    
     
    def on_connect(self):
        print('\n')
        print('###########################################')
        print("You are now connected to the streaming API.")
        print('###########################################\n')
 
    def on_error(self, status_code):
        print('An Error has occured: ' + repr(status_code))
        return False
 
    def on_data(self, data):
        try:
            client = MongoClient(MONGO_HOST)
            
            db = client.twitterdb
            global datajson
    
            datajson = json.loads(data)
                    
            created_at = datajson['created_at']
            print("\n")
            print('*** *** *** *** *** ***')
            print("Tweet collected at : " + str(created_at))
            print('Tweet written by : ' + datajson['user']['name'])
            print('')

            
            get_tweet_text()
            print('')

            if filter_lang == 'fr':
                Sentiment_analysis_french()
                
            if filter_lang == 'en':
                Sentiment_analysis_english()

        except Exception as e:
            print(e)


# In[21]:


def get_tweet_text():
    if 'extended_tweet' in datajson:
        print(datajson['extended_tweet']['full_text'])
    else:
        if datajson['text'].startswith('RT @'):
            if datajson['text'].endswith('…'):
                print(datajson['retweeted_status']['extended_tweet']['full_text'])
            else:
                print(datajson['text'])
        else:
            print(datajson['text'])


# In[22]:


def Sentiment_analysis_french():
    analysis = TextBlob(datajson['text'], pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())
    if analysis.sentiment[0] < 0:
        global negatif
        negatif += 1
    if analysis.sentiment[0] == 0:
        global neutre
        neutre += 1
    if analysis.sentiment[0] > 0:
        global positif
        positif += 1
        
    print('Negatif :', negatif)
    print('Neutre :', neutre)
    print('Positif :', positif)
            
    db.upr_live.insert_one(datajson)
    


# In[23]:


def Sentiment_analysis_english():
    analysis = TextBlob(datajson['text'])
    if analysis.sentiment.polarity < 0:
        global negatif
        negatif += 1
    if analysis.sentiment.polarity == 0:
        global neutre
        neutre += 1
    if analysis.sentiment.polarity > 0:
        global positif
        positif += 1
        
    print('Negatif :', negatif)
    print('Neutre :', neutre)
    print('Positif :', positif)
            
    db.upr_live.insert_one(datajson)
    


# In[24]:


def word_seach():
    global positif
    positif = 0
    global neutre
    neutre = 0
    global negatif
    negatif = 0
    
    
    choice = []
    if filter_lang == 'fr':
        question = 'Quel(s) mot(s) clef(s) souhaitez vous suivre ? Help (SOS) - Back (B)\n'
    if filter_lang == 'en':
        question = 'Which keyword(s) would you like to follow ? Help (SOS) - Back (B)\n'

    print('___')
    sys.stdout.write(question)
    print('')
    
    choice = input(), choice
    words = choice[0]
    
    if words == 'B':
        First()
    if words == 'exit':
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    else:
        return words


# In[25]:


def welcome():

    question = 'For english version press 1\nPour la version francaise tappez 2\n'
    print('___')
    sys.stdout.write(question)
    print('')
    lang = input()
    global filter_lang

    if lang == '1':
        filter_lang = 'en'
    elif lang == '2':
        filter_lang = 'fr'
    elif lang == 'exit':
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    else:
        print('You have to choose a valide option\n')
        print('')
        welcome()
        
    return filter_lang


# In[26]:


def main_Streaming():
    CMR_KEY = CONSUMER_KEY
    CMR_SECRET = CONSUMER_SECRET
    ACCESS_TOKEN = ''
    ACCESS_TOKEN_SECRET = ''
    
    auth = tweepy.OAuthHandler(CMR_KEY, CMR_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    
    WORDS = word_seach()
    
    if WORDS == 'SOS':
        help_streaming()
        
    else:
    
        listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True)) 
        streamer = tweepy.Stream(auth=auth, listener=listener, tweet_mode='extended')
    
        try:
            streamer.filter(track=[WORDS], languages=[filter_lang])
        
        except KeyboardInterrupt:
            print('')
            print('')
            print('* KEYBOARD INTERRUPTION *')
            print('')
            print('')
            First()


# In[27]:


from tabulate import tabulate

def help_streaming():
    print(tabulate([['Twitter', 'TWITTERtwitter “Twitter” twitter. #twitter', 'TwitterTracker#newtwitter'], 
                    ['Twitter’s', 'I like Twitter’s new design', 'Someday I’d like to visit @Twitter’s'], 
                    ['twitter api,twitter streaming', 'Twitter API The twitter streaming Twitter has streaming API', 'I’m new to Twitter'], 
                    ['example.com', 'Someday I will visit example.com', 'There is no example.com/foobarbaz'], 
                    ['example com', 'example.comwww.example.com foo.example.com foo.example.com/bar', '...']], 
                   headers=['Parameter value', 'Will match...', 'Will not match...']))
    print('')
    main_Streaming()


# In[28]:


def get_original_tweet():
    import pprint
    
        
    auth = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    
    choice = []
    print('')
    question = 'Tweet ID ? (Choose B for Back): '
    print('___')
    sys.stdout.write(question)
    choice = input(), choice
    tweet_id = choice[0]
    if tweet_id == 'B':
        First()
    else:
        try:
            tweet = api.get_status(tweet_id)
            if tweet.retweeted == True:
                print('This tweet is a retweet. The original ID is the following :', tweet.retweeted_status.user.id_str)
            if tweet.retweeted == False:
                print(tweet)
                print('')
                get_original_tweet()
                print('')
                print('')
        except:
            print('')
            print('Wrong ID ? Try again !')
            get_original_tweet()
                


# In[35]:


def First():
    choice = []
    
    if filter_lang == 'fr':
        question = 'Souhaitez vous faire du Stream (1), Search (2), ou trouver un original (3) ?\n'
    if filter_lang == 'en':
        question = 'Would you like to make some Stream (1), Search (2) or Original (3) ?\n'
    
    print('___')
    sys.stdout.write(question)
    print('\n')
    
    choice = input(), choice
    if choice[0] == '1':
        main_Streaming()
    if choice[0] == '2':
        main_H()
    if choice[0] == '3':
        get_original_tweet()
    if choice[0] == 'B':
        main()
    if choice[0] == 'exit':
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    else:
        if filter_lang == 'fr':
            print('Vous devez choisir une des options proposes.')
            First()
        if filter_lang == 'en':
            print('You have to choose one of the available solutions.')
            First()


# In[36]:


def main():
    try:
        filter_lang = welcome()
        First()
    except:
        filter_lang = welcome()
        First()
    


# In[37]:


if __name__ == '__main__':
    print('')
    print('')
    print('#############################')
    print('###     MADE TO ENJOY     ###')
    print('#############################')
    print('')
    print('       * Version 1.0 *')
    print('')
    print('')
    print('')
    main()


# In[ ]:





# In[ ]:




