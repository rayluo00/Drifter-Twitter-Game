#Standard Python libs
import collections, configparser, datetime, os, pickle, re, sqlite3, statistics, sys

#Site-libs
import tweepy

class Twitter(object):
    def __init__(self, botName):
        self.api = self.initializeAPI()
        self.botName = botName
        self.rawTweets = []
        self.cleanTweets = []
        self.isValidCommand = None

        if os.path.exists('twitter.pickle'):
            self.loadState()
        else:
            self.lastTweetId = 0

    def initializeAPI(self):
        config = configparser.ConfigParser()
        config.read('twitter.conf')

        if 'twitter' in config:
            if config.has_option('twitter', 'consumer_key'):
                consumer_key = config['twitter']['consumer_key']
            else:
                return None
            if config.has_option('twitter', 'consumer_secret'):
                consumer_secret = config['twitter']['consumer_secret']
            else:
                return None
            if config.has_option('twitter', 'access_token'):
                access_token = config['twitter']['access_token']
            else:
                return None
            if config.has_option('twitter', 'access_token_secret'):
                access_token_secret = config['twitter']['access_token_secret']
            else:
                return None
        else:
            return None

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        return tweepy.API(auth)

    def loadState(self):
        with open('twitter.pickle', 'rb') as f:
            self.lastTweetId = pickle.load(f)

    def saveState(self):
        with open('twitter.pickle', 'wb') as f:
            pickle.dump(self.lastTweetId, f)

    def getTweets(self):
        tweets = {}
        newTweets = []

        if self.lastTweetId:
            self.rawTweets += self.api.mentions_timeline(count=200, since_id=self.lastTweetId)
        else:
            self.rawTweets += self.api.mentions_timeline(count=200)

        for t in self.rawTweets:
            if t.id > self.lastTweetId:
                self.lastTweetId = t.id

            if t.user.screen_name in tweets:
                #Add datetime comparison here
                if tweets[t.user.screen_name][1] < t.created_at:
                    print('Overwriting old tweet from %s' % t.user.screen_name)
                    tweets[t.user.screen_name] = [t.text, t.created_at, False]
                else:
                    continue

            tweets[t.user.screen_name] = [t.text, t.created_at, False]


        for t in tweets:
            msg = self.cleanTweet(tweets[t][0])
            if self.isValidCommand:
                msg = self.isValidCommand(msg)
                if msg:
                    newTweets.append([t, msg, tweets[t][1], tweets[t][2]])
                else:
                    print("INVALID TWEET -- {}: {}".format(t, msg))
            else:
                newTweets.append([t, msg, tweets[t][1], tweets[t][2]])

        #Don't lose the lastTweetId!
        self.saveState()

        print('%d total new tweets from %d user(s). [%d actual tweets]' % (len(self.rawTweets), len(tweets.keys()), len(newTweets)))

        self.cleanTweets = newTweets

        return newTweets

    def sendTweet(self, msg, picFileName=None):
        if picFileName:
            return self.api.update_with_media(picFileName, msg)
        else:
            return self.api.update_status(msg)

    def cleanTweet(self, msg):
        #Remove whitespace around msg
        msg.strip()

        #Remove the botname
        msg.replace(self.botName, '')

        #Remove hashtags
        newMsg = ''
        for i in msg.split():
            if i[:1] == '@':
                pass
            elif i[:1] == '#':
                pass
            elif i.find('://') > -1:
                pass
            else:
                newMsg = newMsg.strip() + ' ' + i

        return newMsg.strip()

    def findTop5Votes(self):
        rawVotes = {}
        top5Votes = []
        mergedTweets = []
        commandCounts = {}
        countedCommands = ['jettison', 'buy', 'sell', 'refine', 'gamble', 'craft']
        count = 0
        biggest = None
        biggestCount = 0

        for t in self.cleanTweets:
            tmp = t[1].split()
            if tmp[0] in countedCommands:
                if not tmp[0] in commandCounts:
                    commandCounts[tmp[0]] = {}
                #XXX: Hack for gamble since it doesn't take an item param
                if tmp[0] == 'gamble':
                    tmp.append('gamble')
                if not tmp[2] in commandCounts[tmp[0]]:
                    commandCounts[tmp[0]][tmp[2]] = []
                try:
                    commandCounts[tmp[0]][tmp[2]].append(int(tmp[1]))
                except e:
                    pass
            else:
                mergedTweets.append(t)
        #Merge the counted command tweets
        for c in commandCounts:
            count = 0
            biggestCount = 0
            biggest = ''
            for i in commandCounts[c]:
                avg = int(statistics.mean(commandCounts[c][i]))
                length = len(commandCounts[c][i])
                count += length
                if length > biggestCount:
                    biggestCount = length
                    biggest = i
                #Update the data we're keeping. Don't care about individual #s,
                #just keep the average and how many votes
                commandCounts[c][i] = [avg, length]
            for x in range(count):
                if c != 'gamble':
                    mergedTweets.append(['MERGED', '{} {} {}'.format(c, commandCounts[c][biggest][0], biggest)])
                else:
                    mergedTweets.append(['MERGED', '{} {}'.format(c, commandCounts[c][biggest][0])])


        for t in mergedTweets:
            if t[1] in rawVotes:
                rawVotes[t[1]] += 1
            else:
                rawVotes[t[1]] = 1

        return sorted(rawVotes.items(), key=lambda t: t[1], reverse=True)[:5]

    def top5ToString(self, top5):
        msg = 'Top 5 Votes:\n\n'

        for t in top5:
            msg += '"' + t[0] + '" - Votes: ' + str(t[1]) + '\n\n'

        if msg == 'Top 5 Votes:\n\n':
            msg = 'No votes submitted this round...\n\n'

        return msg

    def setSuccess(self, winningTweet):
        for t in self.cleanTweets:
            if t[1] == winningTweet:
                t[3] = True

    def resetTweets(self):
        self.rawTweets = []
        self.cleanTweets = []

    def logTweets(self):
        con = None

        try:
            con = sqlite3.connect('web/tweet.db')
            cur = con.cursor()
            for t in self.cleanTweets:
                cur.execute('''SELECT * FROM Player WHERE name=?;''', (t[0],))
                data = cur.fetchone()
                if data: #User exists in database, update their info
                    data = list(data)
                    #Update success
                    if t[3]:
                        data[2] += 1
                    #Update tweet count
                    data[3] += 1

                    #Check for a newer date
                    if t[2].date() > datetime.datetime.strptime(data[5], '%m/%d/%Y').date():
                        data[5] = t[2].strftime('%m/%d/%Y')
                        data[4] += 1

                    #Update the existing entry
                    cur.execute('''UPDATE Player SET Success=?, Total=?, TotalDay=?, LastDay=? WHERE id=?;''', (data[2], data[3], data[4], data[5], data[0]))

                else: #Add user to DB
                    success = 1 if t[3] else 0
                    cur.execute('''INSERT INTO Player (Name, Success, Total, TotalDay, LastDay) VALUES(?, ?, 1, 1, ?);''', (t[0], success, t[2].strftime('%m/%d/%Y')))

                con.commit()

        except sqlite3.Error as e:
            print("Error: {}".format(e))
        finally:
            if con:
                con.close()
