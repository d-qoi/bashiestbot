# Bashiest Bot
A bot to allow Telegram Users execute code in a docker container

### Technologies used

	* Docker
	* MongoDB
	* Python Telegram API (https://github.com/python-telegram-bot/python-telegram-bot)
	* Python 3.x
	* Telegram

### Specifications

Each user will be allowed 4 files that are of the max message length of a telegram message
The container that is running this code is based on the latest version of ubuntu.
	- This may be expanded later, once this is proven to work

If the file is not specified, it will be put into `start.sh` and that will be run when the container starts.

Containers will have a max runtime of 5 minutes.

### TODO
Update the readme

