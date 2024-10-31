# Twitch-Automoderator
A twitch bot that auto moderate any chat in any language using machine learning
# How to run
1) Install required packages
```bash
pip install torch tensorflow tf-keras transformers
```
2) Setup your bot writing the tokens and the initial channel in the config.ini file
```bash
[DEFAULT]
token = oauth:xxxxxxxxxxxxx
client_id = yyyyyyyyyyyyyyy
nick = your_bot_name
prefix = !
initial_channel = your_channel_name
```
3) Run it
```bash
python twitch_moderator.py
```
- The bot will give 2 warnings before timeout the users.
  - The timeout counter will reset if you shutdown the bot (state is not persistent).
  - After the third time he will give the timeout to the user that continues to use a bad language.
- The bot will give a timeout of 1m after 3 warnings, then the timeout duration grows exponentially every 3 warning.
  - 2m after 6 warnings
  - 4m after 9 warnings
  - ...................
  - 64m after 21 warnings and so on...

**WARNING: make sure your bot is a mod**
