from flask import Flask,render_template, redirect, request
import numpy
import tweepy 
import pandas as pd
import re

from textblob import TextBlob
from wordcloud import WordCloud

app = Flask(__name__)

@app.route('/sentiment', methods = ['GET','POST'])
def sentiment():
    userid = request.form.get('userid')
    hashtag = request.form.get('hashtag')

    if userid == "" and hashtag == "":
        error = "Masukkan satu nilai"
        return render_template('index.html', error=error)
    
    if not userid == "" and not hashtag == "":
        error = "Keduanya tidak diizinkan, masukkan satu nilai saja"
        return render_template('index.html', error=error)

    #insert API dari Twitter
    api_key = "cyyUF98R33B2WKma6zkrxidUP"
    api_Secret = "kLoDeNKWPJlLv4Ay0zqluoXzPbCsNlnoeBcZ7r1X9G5veZ83KN"
    accessToken = "1300251636661583872-IYNoLn3D7ozZgaRbOZ6UYLZ9FRZeqy"
    accessTokenSecret = "uNZX4iARllpuga77C9j5FrM9PjiXan13BH0xAn9UP9I58"
    
    
    authenticate = tweepy.OAuthHandler(api_key, api_Secret)
    authenticate.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(authenticate, wait_on_rate_limit = True)

    def cleanTxt(text):
        text = re.sub('@[A-Za-z0–9]+', '', text) #Removing @mentions
        text = re.sub('#', '', text) # Removing '#' hash tag
        text = re.sub('RT[\s]+', '', text) # Removing RT
        text = re.sub('https?:\/\/\S+', '', text) # Removing hyperlink
        return text
    def getSubjectivity(text):
        return TextBlob(text).sentiment.subjectivity
    def getPolarity(text):
        return TextBlob(text).sentiment.polarity
    def getAnalysis(score):
            if score < 0:
                return 'Negative'
            elif score == 0:
                return 'Neutral'
            else:
                return 'Positive'

    if userid == "":
        # hash tag coding
        msgs = []
        msg =[]
        for tweet in tweepy.Cursor(api.search, q=hashtag).items(500):
            msg = [tweet.text] 
            msg = tuple(msg)                    
            msgs.append(msg)

        df = pd.DataFrame(msgs)
        df['Tweets'] = df[0].apply(cleanTxt)
        df.drop(0, axis=1, inplace=True)
        df['Subjectivity'] = df['Tweets'].apply(getSubjectivity)
        df['Polarity'] = df['Tweets'].apply(getPolarity)
        df['Analysis'] = df['Polarity'].apply(getAnalysis)
        positive = df.loc[df['Analysis'].str.contains('Positive')]
        negative = df.loc[df['Analysis'].str.contains('Negative')]
        neutral = df.loc[df['Analysis'].str.contains('Neutral')]

        positive_per = round((positive.shape[0]/df.shape[0])*100, 1)
        negative_per = round((negative.shape[0]/df.shape[0])*100, 1)
        neutral_per = round((neutral.shape[0]/df.shape[0])*100, 1)

        return render_template('anasen.html', name=hashtag,positive=positive_per,negative=negative_per,neutral=neutral_per)
    else:
        # user coding
        username = "@"+userid

        post = api.user_timeline(screen_name=userid, count = 500, lang ="en", tweet_mode="extended")
        twitter = pd.DataFrame([tweet.full_text for tweet in post], columns=['Tweets'])

        twitter['Tweets'] = twitter['Tweets'].apply(cleanTxt)
        twitter['Subjectivity'] = twitter['Tweets'].apply(getSubjectivity)
        twitter['Polarity'] = twitter['Tweets'].apply(getPolarity)

        twitter['Analysis'] = twitter['Polarity'].apply(getAnalysis)
        positive = twitter.loc[twitter['Analysis'].str.contains('Positive')]
        negative = twitter.loc[twitter['Analysis'].str.contains('Negative')]
        neutral = twitter.loc[twitter['Analysis'].str.contains('Neutral')]

        positive_per = round((positive.shape[0]/twitter.shape[0])*100, 1)
        negative_per = round((negative.shape[0]/twitter.shape[0])*100, 1)
        neutral_per = round((neutral.shape[0]/twitter.shape[0])*100, 1)

        return render_template('anasen.html', name=username,positive=positive_per,negative=negative_per,neutral=neutral_per)

@app.route('/')
def home():
    return render_template('index.html')

app.run(debug=True)
