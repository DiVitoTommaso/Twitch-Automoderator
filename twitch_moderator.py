import re
import configparser

from twitchio.ext import commands
from transformers import pipeline

profanity_classifier = pipeline("text-classification", model="SiddharthaM/hasoc19-bert-base-multilingual-cased-profane-new")
print("Profanity classifier ready")

def convert_seconds(seconds):
    days = seconds // (24 * 3600)    # Calculate days
    seconds %= (24 * 3600)           # Remaining seconds after days
    hours = seconds // 3600          # Calculate hours
    seconds %= 3600                  # Remaining seconds after hours
    minutes = seconds // 60          # Calculate minutes
    seconds %= 60                    # Remaining seconds after minutes

    return f"{days}d {hours}h {minutes}m {seconds}s"

class Bot(commands.Bot):
    def __init__(self):
        # Load configuration
        config = configparser.ConfigParser()
        config.read('config.ini')

        super().__init__(
            token=config['DEFAULT']['token'],
            client_id=config['DEFAULT']['client_id'],
            nick=config['DEFAULT']['nick'],
            prefix=config['DEFAULT']['prefix'],
            initial_channels=[config['DEFAULT']['initial_channel']]
        )
        self.channels = [config['DEFAULT']['initial_channel']]
        self.user_warnings = {}

    async def warn_user(self, ctx, msg):
        user = msg.author.id
        # Initialize the user in the warning map if not already present
        if user not in self.user_warnings:
            self.user_warnings[user] = {'count': 0, 'timeout': 0}

        user_data = self.user_warnings[user]
        user_data['count'] += 1

        # Check if the user has reached the max warning limit
        if user_data['count'] % 3 == 0:
            # Calculate timeout duration
            timeout_duration = 30 * (2 ** (user_data['count'] // 3))  # Exponential increase
            await ctx.send(f"{msg.author.mention} Has been timeout for {convert_seconds(timeout_duration)}")
            await ctx.send(f"/timeout {user} {timeout_duration}")
            return f"User {msg.author.name} Timeout! Duration: {convert_seconds(timeout_duration)}"
        else:
            await ctx.send(f"{msg.author.mention} moderate your language! Warn: {user_data['count'] % 3}")
            return f"User {msg.author.name} Warned! Warns: {user_data['count'] % 3}/3"


    async def event_ready(self):
        print(f'Logged in as: {self.nick}')

        for channel_name in self.channels:
            channel = self.get_channel(channel_name)
            await channel.send("Ready!")

    async def event_message(self, message):
        # Ignores the bot's own messages to avoid an echo
        if message.echo:
            return

        #if message.author.is_subscriber or message.author.is_mod or message.author.is_vip:
        #    return

        # Remove mentions (e.g., @username) from the message
        message_content = re.sub(r'@\w+', '', message.content).strip()

        result = profanity_classifier(message_content)
        print(result)
        if result[0]['label'] == '1' and result[0]['score'] >= 0.7:
            ctx = await self.get_context(message)
            result = await self.warn_user(ctx, message)
            print(result)


Bot().run()





