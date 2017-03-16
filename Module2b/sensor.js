'use strict';
var net = require('net');

var PIPE_NAME = "mypipe";

// for Windows
//var PIPE_PATH = "\\\\.\\pipe\\" + PIPE_NAME;
// for linux
var PIPE_PATH = "/home/pi/AzureIoTHandsOnLabs/Module2b/" + PIPE_NAME;

module.exports = {
    broker: null,
    configuration: null,
    server: null,
    pipeName: null,
    pipePath:  null,

    create: function (broker, configuration) {
        this.broker = broker;
        this.configuration = configuration;

        if(this.configuration && this.configuration.pipeName && this.configuration.pipePath) {
            this.pipeName = this.configuration.pipeName.toString();
            this.pipePath = this.configuration.pipePath.toString();
            return true;
        }
        else {
            console.error('This module requires the pipe name and path to be passed in via configuration.');
            return false;
        }

        this.server = net.createServer(function(stream) {
                stream.on('data', function(c) {
                //	console.log('received: ', c.toString());

                this.broker.publish({
                    properties: { },
                    content: new Uint8Array(Buffer.from(c.toString()))
                });	
            });
        });

        return true;
    },

    start: function () {
        this.server.listen(this.pipePath + this.pipeName, function(){ })
    	console.log('sensor.start');
    },

    receive: function(message) {
    },

    destroy: function() {
        this.server.close();
        console.log('sensor.destroy');
    }
};
