import discord
import asyncio
from twython import Twython
import time
from tinydb import TinyDB, where
import json
import os
from sys import stderr

tokens = {}

if not os.path.exists('tokens.config'):
    print("No config file found.", file=stderr)
    exit(-1)
else:
    with open('tokens.config') as t_file:
        tokens = json.load(t_file)

token = tokens['token']
twitter_api_key = tokens['twitter_api_key']
twitter_api_secret = tokens['twitter_api_secret']

db = TinyDB('db.json')

twitter = Twython(twitter_api_key, twitter_api_secret)
auth = twitter.get_authentication_tokens()

OAUTH_TOKEN = auth['oauth_token']
OAUTH_TOKEN_SECRET = auth['oauth_token_secret']

client = discord.Client()


class WeekendGames(object):
    """
    Defines the WeekendGames class
    """

    def __init__(self):
        """
        WeekendGames constructor
        """

        self.people = []
        self.day = 'Sunday'

    def whos_in(self):
        """
        Prints who is currently in for the weekend games.

        :rtype str
        :return: str: Formatted string for the list of people currently signed
        up for weekend games
        """

        if len(self.people) == 0:
            return 'Well that sucks, nobody is in...'
        elif len(self.people) == 1:
            return 'Good news: {} is in for this weekend.'.format(
                self.people[0])
        elif len(self.people) == 2:
            return 'Good news: {} and {} are in for this weekend.'.format(
                self.people[0], self.people[1])
        elif len(self.people) > 2:
            person_list = ', '.join(self.people[:-1])
            person_list += ', and %s' % self.people[-1]
            return 'Good news: {} are in for this weekend.'.format(person_list)

    def add(self, person):
        """
        Adds a person to the weekend games list
        :param person: Person to add
        :return: None
        """

        if self.people.count(remove_formatting(person)) > 0:
            return
        else:
            self.people.append(remove_formatting(person))

    def remove(self, person):
        """
        Removes a person from the weekend games list

        :param person: Person to remove
        :rtype str
        :return: str: Formatted string indicating whether a person was removed.
        """

        if remove_formatting(person) in self.people:
            self.people.remove(remove_formatting(person))
            return '{} is out for this weekend. What a ***REMOVED***.'.format(
                remove_formatting(person))
        else:
            return '{} was never in anyway. Deceptive!'.format(
                remove_formatting(person))


whos_in = WeekendGames()


def remove_formatting(username):
    """
    Removes the hashtag id from a person's discord name, this is for
    readability.

    :param username: Full username to clean
    :rtype str
    :return: str: Clean user name (striped # from username)
    """

    if '#' in str(username):
        return str(username)[:str(username).index('#')]
    else:
        return str(username)


@client.event
async def on_ready():
    """
    Asynchronous event handler for logging in

    :return: None
    """
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    for channel in client.get_all_channels():
        print(channel)

    # await client.send_message('#general', 'Hi I\'m online :)')


@client.event
async def on_message(message):
    """
    Asynchronous event handler for incoming message

    :return: None
    """

    global whos_in
    if message.content.startswith('!test'):
        counter = 0
        tmp = await client.send_message(message.channel,
                                        'Calculating messages...')
        async for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1

        await client.edit_message(tmp, 'You have {} messages.'.format(counter))
    elif message.content.startswith('!sleep'):
        await asyncio.sleep(5)
        await client.send_message(message.channel, 'Done sleeping')

    elif message.content.startswith('!ham'):
        await client.send_message(message.channel,
                                  '@here Let\'s get retarded, {}'.format(
                                      message.author))

    elif message.content.startswith('!in'):
        arguments = message.content.split(' ')
        if len(arguments) > 1:
            arguments.remove('!in')
            for arg in arguments:
                whos_in.add(arg)
        else:
            whos_in.add(message.author)
            await client.send_message(message.channel,
                                      '{} is in for this weekend.'.format(
                                          remove_formatting(message.author)))
        await client.send_message(message.channel, whos_in.whos_in())

    elif message.content.startswith('!out'):
        person_is_out = whos_in.remove(message.author)
        await client.send_message(message.channel,person_is_out)
        await client.send_message(message.channel, whos_in.whos_in())

    elif message.content.startswith('!whosin'):
        await client.send_message(message.channel,whos_in.whos_in())

    elif message.content.startswith('@brochat-bot'):
        print(message)

    elif message.content.startswith('!text-brandon'):
        await client.send_message(message.channel, '#TODO: Twilio integration')

    elif message.content.startswith('!trump'):
        trumps_last_tweet = twitter.get_user_timeline(
            screen_name='realdonaldtrump', count=1, include_retweets=False)
        print(trumps_last_tweet[0])
        await client.send_message(
            message.channel,
            'Trump has been saying things, as usual...\n\n'
            'https://twitter.com/{}/status/{}'.format(
                trumps_last_tweet[0]['user']['screen_name'],
                str(trumps_last_tweet[0]['id'])))

    elif message.content.startswith('!help'):
        help_string = 'Here are some things I can help you with:\n\n' \
                      '**!ham:** I\'ll tell you what we\'re gonna get\n' \
                      '**!in:** Tell me you\'re in for the weekend\n' \
                      '**!whosin:** See who\'s in for the weekend\n' \
                      '**!out:** Tell me you\'re out for the weekend\n' \
                      '**!trump:** I\'ll show you Trump\'s latest Yuge ' \
                      'success!\n' \
                      '**!text-brandon:** Tempt fate\n'

        await client.send_message(message.channel, help_string)

client.run(token)


#TODO weekend gaming session management
#TODO !shots
#TODO !in