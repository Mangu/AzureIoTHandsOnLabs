'use strict';

module.exports = {
    broker: null,
    configuration: null,
    samplesize:  5,
    samplecount: 0,
    humtotal: 0.0,
    temptotal: 0.0,
    humavg: 0.0,
    tempavg:  0.0,

    create: function (broker, configuration) {
        this.broker = broker;
        this.configuration = configuration;

        if(this.configuration && this.configuration.samplesize) {
            this.samplesize = parseInt(this.configuration.samplesize.toString());
            return true;
        }
        else {
            console.error('This module requires the samplesize to be passed in via configuration.');
            return false;
        }

        return true;
    },

    start: function () {
	console.log('edgeprocessor.start with sample size' + this.samplesize.toString());
    },

    receive: function(message) {
	
        //  message format is aa.bb,cc.dd\n
        // where aa.bb is Humidity to two decimal places and cc.dd is Temperature to two decimal places

	console.log('edgeprocessor.receive: ', Buffer.from(message.content).toString());

        var splitString = Buffer.from(message.content).toString().split('\r')[0].split(",");

	this.humtotal = this.humtotal + parseFloat(splitString[0]);
	this.temptotal = this.temptotal + parseFloat(splitString[1]);
        this.samplecount = this.samplecount + 1;

	if(this.samplecount >= this.samplesize)
	{
		var humavg = this.humtotal / this.samplesize;
		var tempavg = this.temptotal / this.samplesize;

		var myMessage = humavg.toFixed(2) + "," + tempavg.toFixed(2) + "\r";
		console.log("edgeprocessor output: " + myMessage);

		// parse c and build JSON string
        	this.broker.publish({
                    properties: {},
                    content: new Uint8Array(Buffer.from(myMessage))
       });	
		this.humtotal = 0;
		this.temptotal = 0;
		this.samplecount = 0;
	}

    },

    destroy: function() {
        console.log('edgeprocessor.destroy');
    }
};
