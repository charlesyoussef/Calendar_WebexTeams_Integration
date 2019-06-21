module.exports = function (controller) {

    controller.hears(["event list"], "direct_message,direct_mention", function (bot, message) {
        //var text = "Here are my skills:";
        //bot.reply(message, text);
        var request = require("request");

        var METABASE_HOST = 'ixc-dashboard.cisco.com';
        var METABASE_AUTH_URL = `http://${METABASE_HOST}/api/session`;
        var METABASE_USERNAME = 'cyoussef@cisco.com';
        var METABASE_PASSWORD = 'Passw0rd1';

        var form_data = {
          "username": METABASE_USERNAME,
          "password": METABASE_PASSWORD
        };

        var headers = {
            'Content-Type': 'application/json',
        };

        var options = {
          'url': METABASE_AUTH_URL,
          'method': 'POST',
          'headers': headers,
          'body': JSON.stringify(form_data)
        };

        var token = '';
        global.upcoming_events = [];
        request(options, function(err, res, body) {
              var json_output = JSON.parse(body);
              //console.log(json_output)
              var token = json_output.id;
              //console.log(json_output);
              //console.log('console is ', token);

              // meta-event DB query:

              var query1_url = 'http://ixc-dashboard.cisco.com/api/card/135/query/json';
              //console.log(query1_url)
              var query1_headers = {
                'Content-Type': 'application/json',
                'X-Metabase-Session': token
              };
              var query1_options = {
                'url': query1_url,
                'method': 'POST',
                'headers': query1_headers
              };
              var request1 = require("request");
              request1(query1_options, function(err, res, body) {
                //const currentTime = new Date().getTime();
                let date = require('date-and-time');
                let now = new Date();
                var json_output = JSON.parse(body);
                global.upcoming_events = [];
                for (var i = 0; i < json_output.length; i++) {
                  var event_id = json_output[i].post_id;
                  var event_start_date = date.parse(json_output[i].meta_value, 'YYYY-MM-DD HH:mm:ss');
                  if (event_start_date > now && upcoming_events.length < 6) {
                    upcoming_events.push({'event_start_time': json_output[i]['meta_value'], 'event_id': json_output[i]['post_id'], 'event_name': ''});
                    //console.log(event_id)
                  }
                  //break
                  //var event_start_date_in_time =
                  //console.log(json_output[i].post_id);
                }
                //console.log(upcoming_event)
                //console.log(json_output)
                //upcoming_events.reverse();
                /*for (var j = 0; j < 5; j++) {
                  //var temp = upcoming_events.pop();
                  //console.log(upcoming_events.pop()['meta_value'])
                  bot.reply(message, upcoming_events.pop()['meta_value']);
                  //console.log("test")
                  //console.log('abc')
                }*/
              });
              // event DB query:

              var query2_url = 'http://ixc-dashboard.cisco.com/api/card/132/query/json';
              var query2_headers = {
                'Content-Type': 'application/json',
                'X-Metabase-Session': token
              };
              var query2_options = {
                'url': query2_url,
                'method': 'POST',
                'headers': query2_headers
              };
              var request2 = require("request");
              request2(query2_options, function(err, res, body) {

                var json_output = JSON.parse(body);
                global.upcoming_events_names = [];


                //let date = require('date-and-time');
                //let now = new Date();
                //var upcoming_events = [];
                for (var i = 0; i < json_output.length; i++) {
                  //console.log(i)
                  if (json_output[i].post_status == "publish") { //}&& json_output[i].ID in upcoming_events) {
                    //bot.reply(message, json_output[i].post_title);
                    //console.log(json_output[i].post_title);
                    for (var j = 0; j < upcoming_events.length; j++) {
                      //console.log(j)
                      if (json_output[i].ID == upcoming_events[j].event_id) {
                        upcoming_events[j].event_name = json_output[i].post_title;
                      }
                    }
                  }
                }
                upcoming_events.sort((a,b) => (a.event_start_time > b.event_start_time) ? 1 : ((b.event_start_time > a.event_start_time) ? -1 : 0));
                //var reply = "";
                //var reply_list = [];
                var events_msg = "Upcoming events are: \n";
                for (var i = 0; i < upcoming_events.length; i++) {
                   events_msg += "\n- " + upcoming_events[i].event_start_time + ": " + upcoming_events[i].event_name + "\n";
                }
                bot.reply(message, events_msg);
                   //console.log(i);
                   //console.log(upcoming_events[i].event_start_time + ": " + upcoming_events[i].event_name);
              });
        });

                  /*var event_id = json_output[i].post_id;
                  var event_start_date = date.parse(json_output[i].meta_value, 'YYYY-MM-DD HH:mm:ss');
                  if (event_start_date > now && upcoming_events.length < 6) {
                    upcoming_events.push(json_output[i]);
                    //console.log(event_id)
                  }
                  //break
                  //var event_start_date_in_time =
                  //console.log(json_output[i].post_id);
                }

              //console.log(currentTime)
        });*/

        /*
        bot.startConversation(message, function (err, convo) {

            convo.ask("What is your favorite color?", [
                {
                    pattern: "^blue|green|pink|red|yellow$",
                    callback: function (response, convo) {
                        convo.gotoThread("confirm_choice");
                    },
                },
                {
                    default: true,
                    callback: function (response, convo) {
                        convo.gotoThread("bad_response");
                    }
                }
            ], { key: "answer" });

            // Bad response
            convo.addMessage({
                text: "Sorry, I don't know this color!<br/>_Tip: try 'blue', 'green', 'pink', 'red' or 'yellow._'",
                action: 'default', // goes back to the thread's current state, where the question is not answered
            }, 'bad_response');

            // Confirmation thread
            convo.addMessage(
                "You picked '{{responses.answer}}'",
                "confirm_choice");

            convo.addQuestion("Please, confirm your choice ? (**yes**|no)", [
                {
                    pattern: "^yes|hey|oui|si|da$",
                    callback: function (response, convo) {
                        var pickedColor = convo.extractResponse('answer');
                        convo.setVar("color", pickedColor);
                        convo.gotoThread("success");
                    },
                },
                {
                    default: true,
                    callback: function (response, convo) {
                        convo.transitionTo("default", "Got it, let's try again...");
                    }
                }
            ], {}, "confirm_choice");

            // Success thread
            convo.addMessage(
                "Cool, I love '{{vars.color}}' too",
                "success");
        });*/
    });
};
