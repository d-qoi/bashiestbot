#! /usr/bin/env python
# -*- coding: utf-8
#
# THis is a telegram bot that is designed to let users and chanels run code in a docker container 
# This will use MongoDB 

import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
#from pymongo import MongoClient
from os import listdir, mkdir, utime, remove
from os.path import isfile, join, exists
from configparser import ConfigParser


config = ConfigParser()
config.read('bashiestbot.conf')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.setLevel(int(config['general']['logging_level']))
mongoPort = int(config['mongodb']['mongoPort'])
mongoPath = config['mongodb']['mongoPath']
api_token = config['telegram']['api_token']
baseFilePath = config['telegram']['user_data']
helloWorld = config['general']['hello_world']



#dbClient = MongoClient(mongoPath, mongoPort)

def runContainer(bot, update):
    echoToConsol(bot, update)

def killContainer(bot, update):
    echoToConsol(bot, update)

def selectFile(bot, update, args, chat_data):
    logger.info('User "%s (%s)" sent /selectfile' % (update.message.chat.username, update.message.chat.id))
    userDirectory = join(baseFilePath, str(update.message.chat.id))
    fileList = listdir(userDirectory)
    logger.debug(str(args))
    logger.debug(str(chat_data))
    logger.debug(str(fileList))
    if args:
        if args[0] in fileList:
            chat_data['selected_file'] = args[0]
            reply = "Selected %s" % (args[0])
        else:
            reply = "Please selected something from you existing files, or create it."
    else:
        reply = "Please pass the name of the file you would like to select.\n Your options are:\n %s\n\n" % (str(fileList))
        reply = reply + 'You currently have "%s" selected' % (None if 'selected_file' not in chat_data else chat_data['selected_file'])
    update.message.reply_text(reply)
        

def listFiles(bot, update):
    logger.info('User "%s (%s)" sent /listFiles' % (update.message.chat.username, update.message.chat.id))
    fileList = listdir(join(baseFilePath, str(update.message.chat.id)))
    reply = str(fileList)
    logger.debug("File list for user: %s" % (reply))
    update.message.reply_text(fileList)

def createFile(bot, update, args, chat_data):
    logger.info('User "%s (%s)" sent /createfile' % (update.message.chat.username, update.message.chat.id))
    userDirectory = join(baseFilePath, str(update.message.chat.id))
    fileList = listdir(join(baseFilePath, str(update.message.chat.id)))
    if len(fileList) < 4:
        if args:
            if '/' in args[0] or '\\' in args[0]:
                reply = "file cannot contain directory information, YTK has been allerted"
                logger.warn("%s(%s) Tried to use directory information" % (update.message.chat.username, update.message.chat.id))
            else:
                with open(join(userDirectory, args[0]), 'a'):
                   utime(join(userDirectory, args[0]), None)
                reply = "Created and selected %s" % (args[0])
                chat_data['selected_file'] = args[0]
                logger.debug("Creating file %s" %(join(userDirectory, args[0])))
        else:
            reply = "Please specify the file you would like to create."
    else:
        reply = "You may have only 4 files initially, please delete an old one before making a new one."
    update.message.reply_text(reply)

def catFile(bot, update, args, chat_data):
    logger.info('User "%s (%s)" sent /catfile' % (update.message.chat.username, update.message.chat.id))
    userDirectory = join(baseFilePath, str(update.message.chat.id))
    fileList = listdir(userDirectory)
    if args:
        if args[0] in fileList and isfile(join(userDirectory, args[0])):
            with open(join(userDirectory, args[0]), 'r') as f:
                reply = "%s\n\n" % (args[0])
                reply = reply + f.read()
        else:
            reply = "Please choose an existing file, or select a file."
    else:
        if 'selected_file' in chat_data and isfile(join(userDirectory, chat_data['selected_file'])):
            with open(join(userDirectory, chat_data['selected_file']), 'r') as f:
                reply = "%s\n\n" % (chat_data['selected_file'])
                reply = reply + f.read()
        else:
            reply = "Please choose an existing file, or select a file."
    update.message.reply_text(reply)


def deleteFile(bot, update, args):
    logger.info('User "%s (%s)" sent /deletefile' % (update.message.chat.username, update.message.chat.id))
    userDirectory = join(baseFilePath, str(update.message.chat.id))
    if args:
        logger.debug("attempting to remove %s" % (args[0]))
        if isfile(join(userDirectory, args[0])):
            remove(join(userDirectory, args[0]))
            logger.debug("Should be removed")
        reply = "If it existed, it shouldn't any longer"
    else:
        reply = "Please send a file name"
    update.message.reply_text(reply)

def start(bot, update, chat_data):
    logger.info('User "%s (%s)" sent /start' % (update.message.chat.username, update.message.chat.id))
    userDirectory = join(baseFilePath, str(update.message.chat.id))
    reply = "Thanks for using @BashiestBot\n"
    if exists(userDirectory):
        reply = reply + "Welcome back!\n"
        fileList = listdir(userDirectory)
        if fileList:
            reply = reply + "You have existing files:\n"
            reply = reply + str(fileList) + '\n'
        else:
            reply = reply + 'Start.sh has automatically been created with a "hello world"'
            with open(join(userDirectory, 'start.sh'), 'w') as f:
                f.write(helloWorld)
    else:
        reply = reply + 'Welcome!\n start.sh has automatically been created with "hello world"'
        mkdir(userDirectory)
        with open(join(userDirectory, "start.sh"), 'w') as f:
            f.write(helloWorld)
    if 'selected_file' in chat_data:
        reply = reply + "You currently have %s as your selected file.\n" % (chat_data['selected_file']) 
    update.message.reply_text(reply)

def help(bot, update):
    logger.info('User "%s (%s)" sent /help' % (update.message.chat.username, update.message.chat.id))
    update.message.reply_text("Please use /man")

def realHelp(bot, update):
    logger.info('User "%s (%s)" sent /man' % (update.message.chat.username, update.message.chat.id))
    update.message.reply_text('''Thanks for using /man
runcontainer 
    Runs the code that you have given this bot, it will always start with ./start.sh
    The container will automatically stop after 5 minutes of run time
kilcontainer
    submits the kill command to the container, it will return stdout logs
listfiles
    basically "ls -la"
createfile <name>
    Create a new file with name <name>
    Selects the file after creation
catfile <name>
    basically "cat <name>"
deletefile <name>
    basically "rm <name>"
help
    redirects to man
man
    prints help docs, also unlisted because reasons
manpages
    Helpfull links about linux for the uninformed (one word only)''')

def helpme(bot, update, args):
    if args:
        update.message.reply_text("https://lmgtfy.com/?q=man7+%s" % (args[0]))
    else:
        update.message.reply_text("https://lmgtfy.com/?q=man+man")

def writeToFile(bot, update, chat_data):
    logger.info('User "%s (%s)" sent code' % (update.message.chat.username, update.message.chat.id))
    logger.debug("Code to be written:\n %s" % (update.message.text))
    userDirectory = join(baseFilePath, str(update.message.chat.id))
    if "selected_file" in chat_data and exists(join(userDirectory, chat_data['selected_file'])):
        with open(join(userDirectory, chat_data["selected_file"]), 'w') as f:
            f.write(update.message.text)
        reply = "Written to %s" % (chat_data['selected_file'])
    else:
        reply = "Please select an existing file"
    update.message.reply_text(reply)

def echoToConsol(bot, update):
    print(update.message)
    logger.info('Message received "%s"' % (update.message))
    update.message.reply_text("You message has been received, Feature not implemented yet")

def error(bot, update, error):
    logger.warn('Update "%s" cause error "%s"' %(update, error))

def debugHelp(bot, update, chat_data):
    userDirectory = join(baseFilePath, str(update.message.chat.id))
    fileList = listdir(userDirectory)
    logger.info("------------------DEBUG CALLED-------------------------")
    logger.debug("Username: %s (%s)" %(update.message.chat.username, update.message.chat.id))
    logger.debug("User Dir: %s" % (userDirectory))
    logger.debug("File list: %s" % (str(fileList)))
    logger.debug("chat_data: %s" % (str(chat_data)))
    logger.debug("update: %s" % (str(update)))

def main():
    updater = Updater(api_token)

    dp = updater.dispatcher

    # contianer commands
    dp.add_handler(CommandHandler('runcontainer', runContainer))
    dp.add_handler(CommandHandler('killcontainer', killContainer))

    #file commands
    dp.add_handler(CommandHandler('selectfile', selectFile, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler('listfiles', listFiles))
    dp.add_handler(CommandHandler('createfile', createFile, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler('catfile', catFile, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler('deletefile', deleteFile, pass_args=True))

    #Other commands
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('man', realHelp))
    dp.add_handler(CommandHandler('start', start, pass_chat_data=True))
    dp.add_handler(CommandHandler('debug', debugHelp, pass_chat_data=True))
    dp.add_handler(CommandHandler('manpages', helpme, pass_args=True))

    #other text commands
    dp.add_handler(MessageHandler(Filters.text, writeToFile, pass_chat_data=True, allow_edited=False))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
