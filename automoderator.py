import warnings

warnings.filterwarnings("ignore")

from twitchio.ext import commands
from twitchio.abcs import Messageable
from twitchio.dataclasses import Message, User

from googletrans import Translator
from profanity_check import predict, predict_prob
from logging import Logger

log = Logger("Moderator")

trans = Translator()
"""
with open("./credentials.txt", "r") as file:
    channel = file.readline().decode("utf-8").replace("channel =").replace(" ","")
    token = file.readline().decode("utf-8").replace("token =").replace(" ","")
    clientId = file.readline().decode("utf-8").replace("clientID =").replace(" ","")
    secret = file.readline().decode("utf-8").replace("secret =").replace(" ","")
"""

log.info("Reading credentials...")

channel = "-"
token = "-"
clientId = "-"
secret = "-"

badWords = set()
warns = {}

log.info("Reading bad words...")
"""
with open("./badwords.txt") as file:
    for word in file.readlines():
        badWords.add(word)
"""


class Bot(commands.Bot):
    async def event_pubsub(self, data):
        pass

    def __init__(self):
        super().__init__(irc_token=token, client_id=clientId, client_secret=secret,
                         nick=channel, prefix='!', initial_channels=[channel.lower()])
        #enable commands
        Messageable.__invalid__ = ()
        #cache followers to avoid to check every time if the user is follower or not
        self.cacheFollowers = set()
        self.owner = None

    async def event_ready(self):
        #save the bot owner when ready and notify printing on screen
        self.owner = (await self.get_users(channel))[0]
        print(f"Connection to {channel} established successfully!")

    async def event_error(self, error: Exception, data=None):
        log.info(f"Error occurred {error}")

    def isCached(self, user):
        return self.cacheFollowers.__contains__(user.id)

    @staticmethod
    def isFollower(follow):
        return None != follow

    async def event_message(self, message: Message):
        #check if is fake donation
        try:
            if message.content.index("donat") < 30  and (message.content.__contains__("£") or message.content.__contains__("€") or message.content.__contains__("$")) \
                    and len(message.content) < 50:
                await message.channel.send(f"/delete {message.tags['id']}")
                return
        except ValueError:
            pass

        if message.author.is_subscriber or message.author.is_mod or self.isCached(message.author):
            return
        try:
            if Bot.isFollower(await self.get_follow(message.author.id, self.owner.id)):
                self.cacheFollowers.add(message.author.id)
                return
        except Exception as e:
            log.error(e)

        # translate text to english
        translated = trans.translate(message.content)

        # split message into words and check if contains bad words added manually
        words = message.content.split(" ")
        for word in words:
            if badWords.__contains__(word):
                await message.channel.send(f"/delete {message.tags['id']}")
                await self.moderate(message)
                return

        # analise the message and check if there are some "standard and masked" bad words
        for res in predict([translated.text]):
            if res:
                await message.channel.send(f"/delete {message.tags['id']}")
                await Bot.moderate(message)
                return

    @staticmethod
    async def moderate(message):
        # warn or timeout user depending on how many infractions
        if warns.get(message.author.id) is None:
            warns[message.author.id] = 1
            await message.channel.send(
                f"/me @{message.author.name} [{warns.get(message.author.id)}/3] WARN: if you keep writing profanities you will be timed out!")
        elif warns.get(message.author.id) == 3:
            await message.channel.send(f"Timed out @{message.author.name} for 1h reason: Profanities")
            await message.channel.send(f"/timeout {message.author.name} 1h")
            warns[message.author.id] = None
        else:
            warns[message.author.id] = warns[message.author.id] + 1
            await message.channel.send(
                f"/me @{message.author.name} [{warns.get(message.author.id)}/3] WARN: if you keep writing profanities you will be timed out!")


log.info("Connecting...")
Bot().run()
