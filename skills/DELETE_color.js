module.exports = function (controller) {

     controller.hears(['color'], 'direct_message,direct_mention', function (bot, message) {

         bot.startConversation(message, function (err, convo) {
             convo.say('This is a Botkit conversation sample.');
             convo.ask('What is your favorite color?', function (response, convo) {
                 //convo.say('Cool, I like ' + response.text + ' too!');
                 convo.say('Cool, I like ' + message.user + ' too!');
                 convo.next();
             });
         });
         //console.log("MESSAGE from: " + message.original_message.personEmail);
     });
 };
