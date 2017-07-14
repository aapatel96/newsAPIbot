import json
import os.path
import os
import sys

from telegram.ext import Updater, CommandHandler, MessageHandler,ConversationHandler, Filters, Job, JobQueue, CallbackQueryHandler
import telegram.replykeyboardmarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram.keyboardbutton
from telegram.chataction import ChatAction

import logging
import urllib
import time
from random import randint
import pymongo
import requests

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

APIAI_CLIENT_ACCESS_TOKEN = 'f60e16e080d7446285e92826bf51415e'

ai = apiai.ApiAI(APIAI_CLIENT_ACCESS_TOKEN)

newsapi = "https://newsapi.org/v1/articles?source="
news_keyboard= telegram.replykeyboardmarkup.ReplyKeyboardMarkup([[telegram.KeyboardButton("google news")],[telegram.KeyboardButton("the hindu")],
                                                              [telegram.KeyboardButton("recode")],[telegram.KeyboardButton("techcrunch")],
                                                              [telegram.KeyboardButton("the guardian")],[telegram.KeyboardButton("the verge")],
                                                              [telegram.KeyboardButton("new york times")],[telegram.KeyboardButton("wapo")],
                                                              [telegram.KeyboardButton("reuters")],[telegram.KeyboardButton("ap")],
                                                              [telegram.KeyboardButton("bloomberg")],
                                                              [telegram.KeyboardButton("business insider")],
                                                              [telegram.KeyboardButton("economist")]], resize_keyboard=True)
inline_news_keyboard= InlineKeyboardMarkup(
                                [
                                    [InlineKeyboardButton("google news"),InlineKeyboardButton("the hindu")],
                                    [InlineKeyboardButton("recode"),InlineKeyboardButton("techcrunch")],
                                    [InlineKeyboardButton("the guardian"),InlineKeyboardButton("the verge")],
                                    [InlineKeyboardButton("new york times"),InlineKeyboardButton("wapo")],
                                    [InlineKeyboardButton("reuters"),InlineKeyboardButton("ap")],
                                ]
                                )
inlineNextKeyboard1 = InlineKeyboardMarkup([[InlineKeyboardButton("next", callback_data='1')]])
inlineNextKeyboard2 = InlineKeyboardMarkup([[InlineKeyboardButton("previous", callback_data='2'),InlineKeyboardButton("next", callback_data='1')]])
inlineNextKeyboard3 = InlineKeyboardMarkup([[InlineKeyboardButton("previous", callback_data='2')]])


googlec = "google-news"
thehinduc="the-hindu"
recodec="recode"
vergec="the-verge"
techcrunchc="techcrunch"
guardianc="the-guardian-uk"
nytc="the-new-york-times"
wapoc="the-washington-post"
reutersc="reuters"
apc="associated-press"
economistc ="the-economist"
hnc ="hacker-news"
topnews = "&sortBy=top&apiKey=07ce18ffbbca413289f3d57290de93e9"


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

client = pymongo.MongoClient('mongodb://heroku_f2r337th:ne3c4ehdbnknfrd5k815kth4qa@ds143362.mlab.com:43362/heroku_f2r337th',connect=False)

db = client.get_default_database()



users = db['users']
newsLists = db['newslists']



# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


#classes

userformat = {"uid":None,"listIDs":[],"lists":[]}

newsListformat = {'uid':None,'listID':None,'code':None,'list':None,'index':None}

def find_newsList(listf, listID):
    for i in range(len(listf)):
        if listf[i]['listID'] == listID:
            return i
    return None


def start(bot, update, job_queue):
    userDB = users.find_one({"uid":update.message.from_user.id})
    
    if userDB != None:
        update.message.reply_text("you are already registered")
        return
        
    userJ = {"uid":update.message.from_user.id,"listIDs":[],"lists":[]}
    users.insert_one(userJ)
    bot.sendChatAction(update.message.chat.id, ChatAction.TYPING)
    update.message.reply_text("Welcome to News bot")
    bot.sendChatAction(update.message.chat.id, ChatAction.TYPING)
    time.sleep(2)
    update.message.reply_text("Credit to https://newsapi.org/ for the news sources")
    time.sleep(2)
    bot.sendChatAction(update.message.chat.id, ChatAction.TYPING)
    update.message.reply_text("Choose from below to see the news that you want:", reply_markup=news_keyboard)
    job_queue.run_once(herokualarm,1,context=job_queue)
        
        
def help(bot, update):
    update.message.reply_text(' newtask <taskname:priority:duedate> to create a task'+ '\n'
                              + ' mytasks to show tasks'+'\n'+ ' newhabit <habitname:priority>'+'\n'+ ' myhabits to show tasks'+'\n'+ ' deltask <taskid> to delete task by task id (you can find this out using /mytasks command)'
                              +'fintask ,<taskid> to delete task by task id (you can find this out using /mytasks command'+ '\n' +'delthabit <habitid> to delete habit by habit id (you can find this out using /myhabits command)' +"/help to get command list")

def herokualarm(bot,job):
    logger.info("ping")
    requests.post("https://delayedecho.herokuapp.com/", data={"ping":"ping"})
    job = job.context.run_once(herokualarm, 15*60,context=job.context)
    
def whatNews(bot,update):

    try:
        userDB = users.find_one({"uid":update.message.from_user.id})
    except:
        update.message.reply_text("You are not registered. Press /start and then resend command2")
        return ConversationHandler.END
    

    
    if update.message.text == "What do you think about the government?":
        update.message.reply_text("yeh government bik gayi hai")
        return ConversationHandler.END
    
    else:
        request = ai.text_request()
        request.session_id = update.message.chat_id
        request.query = update.message.text
        response = request.getresponse()
        JSON= json.loads(response.read().decode())
        if JSON['result']['metadata']['intentName'] != 'smaug.news':
            update.message.reply_text("hmmm...did not get that...choose from below please",reply_markup=news_keyboard)
            return
        else:
            code = JSON['result']['parameters']['Newsource']
            listID = str(randint(10000,99999))
            while listID in userDB["listIDs"]:
                listID = str(randint(10000,99999))
                
            newsList = newsListformat
            
            url = newsapi+code+topnews
            response = urllib.urlopen(url)
            data = json.loads(response.read())
            x = ''
            
            newsList['code']=code
            newsList['list']=data['articles']
            newsList['index']=0
            newsList['listID']=listID
            newsList['uid'] = update.message.from_user.id

            x = newsLists.insert({"code":code,"list":data['articles'],"index":0,"listID":listID,"uid":update.message.from_user.id})
            

            users.update({"uid":update.message.from_user.id}, {'$push':{'listIDs': listID}})
            users.update({"uid":update.message.from_user.id}, {'$push':{'listIDs': listID}})


            newsList2use = newsLists.find_one({"listID":listID})

            x = "QUERY"+str(listID) +'\n'+'\n'+newsList2use['list'][newsList2use['index']]['url']

            update.message.reply_text(x,reply_markup=inlineNextKeyboard1,parse_mode='HTML')
    return

def nextButton(bot,update):
    query = update.callback_query.id
    queryObj = update.callback_query
    queryData = update.callback_query.data
    text =  message=update.callback_query.message.text
    textComps = text.split('\n')
    listID = textComps[0][5:]
    mid = queryObj.message.message_id
    uid = queryObj.message.chat.id


    query = {"uid":queryObj.message.chat.id,"listID":listID}
    newsList = newsLists.find_one({"uid":queryObj.message.chat.id,"listID":listID})


    newsListIndex = newsList['index']
    

    if str(queryData) == "2":

        newsLists.update(query, {'$inc': {"index":-1}})
    if str(queryData) == "1":

        newsLists.update(query, {'$inc': {"index":1}})

    newsList = newsLists.find_one({"uid":queryObj.message.chat.id,"listID":listID})
    if newsList['index'] == 0:
        keyboard =inlineNextKeyboard1
    elif newsList['index'] == len(newsList['list'])-1:
        keyboard=inlineNextKeyboard3
    else:
        keyboard=inlineNextKeyboard2

        
    x = "QUERY"+str(listID)+'\n'+'\n'+newsList['list'][newsList['index']]['url']


    bot.edit_message_text(text=x,   
                      chat_id=queryObj.message.chat_id,
                      message_id=mid)
    bot.edit_message_reply_markup(chat_id =queryObj.message.chat_id,message_id=mid,reply_markup =keyboard,parse_mode='HTML')

    return

    
def main():
    PORT = int(os.environ.get('PORT', '5000'))
    TOKEN = "395034398:AAHfgv6aYDbhT2odEo5PvFWJH3EhhK6uC9s"
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)
    '''
    userslist = list(users.find())
    for user in userslist:
        updater.bot.send_message(user['uid'],"Business Insider and Economist added as sources",reply_markup=news_keyboard)
    '''
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start",start,pass_job_queue=True))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, whatNews))
    dp.add_handler(CallbackQueryHandler(nextButton))

    #news

    # log all errors
    dp.add_error_handler(error)
    updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
    updater.bot.set_webhook("https://telegramnewsbot.herokuapp.com/" + TOKEN)
    # Start the Bot
##    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
