//
// Command: event approve
//
module.exports = function (controller) {

     controller.hears(['event approve'], 'direct_message,direct_mention', function (bot, message) {

         bot.startConversation(message, function (err, convo) {

             convo.ask('What is the ID of the event to approve?', function (response, convo) {

                 const { spawn } = require('child_process')

                 const logOutput = (name) => (data) => console.log(`[${name}] ${data.toString()}`)

                 function run() {
                   // passing 3 arguments to the event_approve.py script:
                   // First arg is the user input (event ID)
                   // Second arg is the email address of the user who sent the message
                   // Third arg is the room/person ID
                   // Fourth arg is the message type ('direct_mention' or 'direct_message')
                   const process = spawn('python', ['./event_approve.py', response.text, message.user, message.channel, message.type]);

                   process.stdout.on(
                     'data',
                     logOutput('stdout')
                   );

                   process.stderr.on(
                     'data',
                     logOutput('stderr')
                   );
                 }

                 (() => {
                   try {
                     run()
                     // process.exit(0)
                   } catch (e) {
                     console.error(e.stack);
                     process.exit(1);
                   }
                 })();
                 convo.next();
             });
         });
         //console.log("MESSAGE from: " + message.original_message.personEmail);
     });
 };
