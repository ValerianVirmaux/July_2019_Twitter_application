This project is coming from an association, asking me to help them using social media in a better way.

It has various axis, one of them is visualisation of their network. I succesfully used gml file and Gephi software to help them understand their network.

An other part was an analysis of their twitter profil. Graphs and statistics were made in that way.

Ths script I'm puting public is a little application I made in order to allow them using Tweepy tool.

Natural Language Processing as well as Sentiment Analysis are used in order to understand better the inside of the tweets.

The application first ask if we want to use it in French, or English. Tweets and instruction would be given in that languages.

Then three options are available. First one is streaming, basically tweepy.Stream functionality from which I added sentiment analysis. Second option is tweepy.seach one, allowing the users to search keywords through the free tweepy application and the 7/9 days available. A series of statistics (most used words, diversity of the vocabulary, sentiment analysis) is then given. Last functionality is given the inside of the tweet from tweepy point of view, thanks to tweet ID. I made it in order for the association to understand what could be given as information, and so they could come back to me with specific needs, allowing me to change this application accordingly.

Everything was made in a very short period of time and has to be seen as a draft.

This app is available in my docker : docker pull docker.io/valvirdocker/upr:version2

