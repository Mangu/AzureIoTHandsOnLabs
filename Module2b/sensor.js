'use strict';
var net = require('net');

var PIPE_NAME = "mypipe";
//var PIPE_PATH = "\\\\.\\pipe\\" + PIPE_NAME;
var PIPE_PATH = "/home/pi/AzureIoTHandsOnLabs/Module2b/" + PIPE_NAME;

var L = console.log;

var mybroker = null;

var server = net.createServer(function(stream) {
//    L('Server: on connection')

    stream.on('data', function(c) {
//        L('Server: on data:', c.toString());
//	console.log('received: ', c.toString());

	var splitString = c.toString().split('\r')[0].split(",");

 //   console.log("...", c.toString().split('\r')[0], "...");

	var myMessage = {
		DeviceID : "gwtestdevice",
		Temperature : splitString[1],
		Humidity : splitString[0]
	};

// parse c and build JSON string

	mybroker.publish({
                properties: {
                },
                content: new Uint8Array(Buffer.from(JSON.stringify(myMessage)))
            });	
    });

    stream.on('end', function() {
//        L('Server: on end')
        server.close();
    });

//    stream.write('Take it easy!');
});

server.listen(PIPE_PATH,function(){
    L('Server: on listening');
})

function getBytes(str) {
  var bytes = [], char;
  str = encodeURI(str);

  while (str.length) {
    char = str.slice(0, 1);
    str = str.slice(1);

    if ('%' !== char) {
      bytes.push(char.charCodeAt(0));
    } else {
      char = str.slice(0, 2);
      str = str.slice(2);

      bytes.push(parseInt(char, 16));
    }
  }

  return bytes;
};
module.exports = {
    broker: null,
    configuration: null,

    create: function (broker, configuration) {
        this.broker = broker;
	mybroker = broker;
        this.configuration = configuration;
	
        return true;
    },

    start: function () {
//        setInterval(() => {
//            this.broker.publish({
//                properties: {
//                    'source': 'sensor'
//                },
//                content: new Uint8Array([
//                    Math.random() * 50,
//                    Math.random() * 50
//                ])
//            });
//        }, 2000);

	console.log('sensor.start');
    },

    receive: function(message) {
    },

    destroy: function() {
        console.log('sensor.destroy');
    }



};
