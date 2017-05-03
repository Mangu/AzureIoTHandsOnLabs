'use strict';
var net = require('net');

module.exports = {
    broker: null,
    configuration: null,
    server: null,
    pipeName: null,
    pipePath:  null,
    pipeStream: null,

    create: function (broker, configuration) {
        this.broker = broker;
        this.configuration = configuration;

	console.log('creating sensor');

        if(this.configuration && this.configuration.pipeName && this.configuration.pipePath) {
            this.pipeName = this.configuration.pipeName.toString();
            this.pipePath = this.configuration.pipePath.toString();
            return true;
        }
        else {
            console.error('This module requires the pipe name and path to be passed in via configuration.');
            return false;
        }

        return true;
    },

    start: function () {

    	console.log('sensor.start - listening on ', this.pipePath + this.pipeName);

        this.server = net.createServer(function(stream) {
                
		console.log('creating server');
		module.exports.pipeStream = stream;

		stream.on('data', function(c) {
                	console.log('sensor.received: ', c.toString());

	                module.exports.broker.publish({
        	            properties: { },
                	    content: new Uint8Array(Buffer.from(c.toString()))
                });	
            });
	});

        this.server.listen(this.pipePath + this.pipeName, function(){ })
    },

    receive: function(message) {

	var msgtxt = Buffer.from(message.content).toString()
	console.log('sensor received command: ' + msgtxt);
	this.pipeStream.write(msgtxt);

    },

    destroy: function() {
        this.server.close();
        console.log('sensor.destroy');
    }
};
