'use strict';
require('timers');

module.exports = {
    broker: null,
    configuration: null,

    create: function (broker, configuration) {
        this.broker = broker;
        this.configuration = configuration;

	console.log('creating sensor');

        return true;
    },

    start: function () {

		console.log('creating server');
	

    },

    receive: function(message) {
    },

    destroy: function() {
//        this.server.close();
        console.log('sensor.destroy');
    }
};


	var c = "22.00,57.00";

	setInterval(function(){
                	console.log('received: ', c.toString());

	                module.exports.broker.publish({
        	            properties: { },
                	    content: new Uint8Array(Buffer.from(c.toString()))
			});
	}, 5000);

