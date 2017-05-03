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

        // read the named pipe name and path from the gateway configuration file.
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

        // create the named pipe specified in configuration and wire up a 'stream'
        this.server = net.createServer(function(stream) {
                
		console.log('creating server');
        // save a reference to the stream for use in the receive function.  There is  probably a better
        // way to do this, given Node's crazy scoping rules, but I'm a Node novice and this works. :-)
		module.exports.pipeStream = stream;

        // when data is received on the pipe
		stream.on('data', function(c) {
                	console.log('sensor.received: ', c.toString());

                    // write the data out to the gateways message broker.  No properties specified and
                    // convert the data we received from the pipe to a byte array.
	                module.exports.broker.publish({
        	            properties: { },
                	    content: new Uint8Array(Buffer.from(c.toString()))
                });	
            });
	});

        // start listening to the named pipe
        this.server.listen(this.pipePath + this.pipeName, function(){ })
    },

    // this function is invoked by the gateway whenever a message is routed our way
    receive: function(message) {

        // convert the message to a string
	    var msgtxt = Buffer.from(message.content).toString()
	    console.log('sensor received command: ' + msgtxt);
        // write the message out to the named pipe
	    this.pipeStream.write(msgtxt);

    },

    // called when the gateway is shutting down
    destroy: function() {
        this.server.close();
        console.log('sensor.destroy');
    }
};
