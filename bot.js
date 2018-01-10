const cmd = require('node-cmd');
const telebot = require('telebot');


const bot = new telebot('459862233:AAHw003iZrx6pB04w7U0BwIElBJ87DqAGwI');

bot.on('text', (msg) => {
  cmd.get(
    msg.text,
    function(err, data, stderr){
    	if (err){return console.log(err)}
    	if (stderr){return console.log(stderr)}
    	console.log(data);
        bot.sendMessage(msg.from.id,data);
    }
  );
});

bot.start();
