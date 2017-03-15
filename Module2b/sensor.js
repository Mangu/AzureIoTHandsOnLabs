'use strict';
var net = require('net');

var PIPE_NAME = "mypipe";

// for Windows
//var PIPE_PATH = "\\\\.\\pipe\\" + PIPE_NAME;

// for linux
var PIPE_PATH = "/home/pi/AzureIoTHandsOnLabs/Module2b/" + PIPE_NAME;

var mybroker = null;

var server = net.createServer(function(stream) {
    stream.on('data', function(c) {
//	console.log('received: ', c.toString());

	var splitString = c.toString().split('\r')[0].split(",");

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
        server.close();
    });
});

server.listen(PIPE_PATH,function(){
})

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
	console.log('sensor.start');
    },

    receive: function(message) {
    },

    destroy: function() {
        console.log('sensor.destroy');
    }
};
