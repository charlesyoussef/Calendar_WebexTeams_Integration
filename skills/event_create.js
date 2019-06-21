//
// Command: event create
//
module.exports = function (controller) {

     controller.hears(['event create'], 'direct_message,direct_mention', function (bot, message) {

       var text = "Please submit the event details on:   ";
       text += "\n" + "https://mea.cisco.com/web/submit-an-event";
       bot.reply(message, text);

     });
 };
