# newsAPIbot

This bot is part of my ongoing project to replace all the apps on my phone with chatbots. You can read more about it over here: https://medium.com/p/c8cbe91f5b38/edit

The bot can be accessed on telegram using the following link: https://t.me/@personalnewsbot and was created using [NewsAPI](newsapi.org).

# How the bot works?

Once you hit start in the bot, you should be greeted by a keyboard that looks like this:

![keyboard](https://i.imgur.com/3zA8H6w.png)

Clicking on any of the quick replies will show you a news article from that source with a next/prev button to flip betwen articles:

![navigation](https://i.imgur.com/IFTEzMq.gif)
 
You can also type out requests in the chat input box to have the bot send you news. This input method is hooked up to a [Dialogflow](dialogflow.com) NLP project, so you can say things like "The Times" to ask for New York Times, "The post" to ask for the Washington Post etc.

![nlp](https://i.imgur.com/vDHuPfJ.gif)

Also, you will notice that each seperate request comes with a unique id:

![uniqid](https://i.imgur.com/gJFMdxW.png)

This means that if you scroll back through your chat and hit next/prev on any of the queries you have made, you will be able to see the articles from that source on that particular date. Kind of like a time machine.
