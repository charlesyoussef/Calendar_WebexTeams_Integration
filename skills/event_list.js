//
// Command: event list
//
module.exports = function (controller) {

    controller.hears(["event list"], "direct_message,direct_mention", function (bot, message) {

      const { spawn } = require('child_process')

      const logOutput = (name) => (data) => console.log(`[${name}] ${data.toString()}`)

      function run() {
        // passing 3 argument to the event_list.py script:
        // 1. email address of the user who sent the message
        // 2. channel ID (room ID or user ID)
        // 3. message type ('direct_mention' or 'direct_message')
        const process = spawn('python', ['./event_list.py', message.user, message.channel, message.type]);

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

    });
};
