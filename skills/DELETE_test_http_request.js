
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
        for (var i = 0; i < upcoming_events.length; i++) {
           //bot.reply(message, upcoming_events[i].event_start_time + ": " + upcoming_events[i].event_name);
           console.log(i);
           console.log(upcoming_events[i].event_start_time + ": " + upcoming_events[i].event_name);
        }
      });
});

/*
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
request(options, function(err, res, body) {
      var json_output = JSON.parse(body);
      console.log(json_output)
      var token = json_output.id;
      //console.log(json_output);
      console.log('console is ', token);

      // DB query:

      var query1_url = 'http://ixc-dashboard.cisco.com/api/card/135/query/json';
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
        var upcoming_events = [];
        for (var i = 0; i < json_output.length; i++) {
          var event_id = json_output[i].post_id;
          var event_start_date = date.parse(json_output[i].meta_value, 'YYYY-MM-DD HH:mm:ss');
          if (event_start_date > now) {
            upcoming_events.push(json_output[i]);
            //console.log(event_id)
          }
          //break
          //var event_start_date_in_time =
          //console.log(json_output[i].post_id);
        }
        //console.log(upcoming_event)
        //console.log(json_output)
        //upcoming_events.reverse();
        for (var j = 0; j < 5; j++) {
          //var temp = upcoming_events.pop();
          console.log(upcoming_events.pop()['meta_value'])
          //console.log("test")
          //console.log('abc')
        }
      });


      //console.log(currentTime)
});
*/

/*
var Request = require("request");

Request.post({
    "headers": { "content-type": "application/json" },
    "url": "http://httpbin.org/post",
    "body": JSON.stringify({
        "firstname": "Nic",
        "lastname": "Raboy"
    })
}, (error, response, body) => {
    if(error) {
        return console.dir(error);
    }
    var output_log = JSON.parse(body);
    var msg = ""
    for (var i = 0; i < output_log.length; i++) {
      var current = output_log[i];
      msg += current.firstname
    }
    cb(null, events, msg);
});

/*
const https = require("https");
const url = "https://jsonplaceholder.typicode.com/posts/1";
https.get(url, res => {
  res.setEncoding("utf8");
  let body = "";
  res.on("data", data => {
    body += data;
  });
  res.on("end", () => {
    body = JSON.parse(body);
    console.log(body);
  });
});

/*
var debug = require("debug")("samples");
var fine = require("debug")("samples:fine");

var request = require("request");

var options = {
    method: 'GET',
    url: "https://devnet-events-api.herokuapp.com/api/v1/events/next?limit=5"
};

request(options, function (error, response, body) {
    if (error) {
        debug("could not retreive list of events, error: " + error);
        cb(new Error("Could not retreive upcoming events, sorry [Events API not responding]"), null, null);
        return;
    }

    if ((response < 200) || (response > 299)) {
        console.log("could not retreive list of events, response: " + response);
        cb(new Error("Could not retreive upcoming events, sorry [bad anwser from Events API]"), null, null);
        return;
    }

    var events = JSON.parse(body);
    debug("fetched " + events.length + " events");
    fine(JSON.stringify(events));

    if (events.length == 0) {
        cb(null, events, "**Guess what? No upcoming event!**");
        return;
    }

    var nb = events.length;
    var msg = "**" + nb + " upcoming events:**\n";
    if (nb == 1) {
        msg = "**only one upcoming event:**\n";
    }
    for (var i = 0; i < nb; i++) {
        var current = events[i];
        //msg += "\n:small_blue_diamond: "
        msg += "\n" + (i+1) + ". ";
        msg += current.beginDay + " - " + current.endDay + ": [" + current.name + "](" + current.url + "), " + current.city + " (" + current.country + ")";
    }

    cb(null, events, msg);
});



/* const superagent = require('superagent');


//const Http = new XMLHttpRequest();
const url='https://jsonplaceholder.typicode.com/posts';
const a = superagent.get(url);
console.log(a);
//Http.open("GET", url);
//Http.send();

/*Http.onreadystatechange = (e) => {
  console.log(Http.responseText)
}

const superagent = require('superagent');

superagent.get('https://api.nasa.gov/planetary/apod')
.query({ api_key: 'DEMO_KEY', date: '2017-08-02' })
.end((err, res) => {
  if (err) { return console.log(err); }
  console.log(res.body.url);
  console.log(res.body.explanation);
});

*/
