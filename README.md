# Twitch-Automoderator
A twitch bot that auto moderate any chat in any language using machine learning
# How to run
1) Install required packages
```bash
pip install torch tensorflow tf-keras transformers
```
2) Run it
```bash
python automoderator.py
```
The bot will give 2 warnings before timeout the users. After the third time he will give the timeout to the user that continues to use a bad language. The bot will give a timeout of 1m after 3 warnings, then the timeout duration grows exponentially every 3 warning so 2m (6 warnings) 4m (9 warnings) 8m (12 warnings) and so on. The timeout counter will reset if you shutdown the bot (the number of warnings are not saved persistently).

**WARNING: make sure your bot is a mod**
