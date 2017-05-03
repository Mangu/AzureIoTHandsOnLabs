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

        // read sample size from config.  Tells us how many readings to 'average over'
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

        // split the temp and Humidity into separate strings in an array.
        var splitString = Buffer.from(message.content).toString().split('\r')[0].split(",");

        // add the current values to a running total
        this.humtotal = this.humtotal + parseFloat(splitString[0]);
        this.temptotal = this.temptotal + parseFloat(splitString[1]);
        this.samplecount = this.samplecount + 1;

        // once we've reached the number of samples specified in the config
        if(this.samplecount >= this.samplesize)
        {
            // compute the average values
            var humavg = this.humtotal / this.samplesize;
            var tempavg = this.temptotal / this.samplesize;

            // re-write into the original CSV format, since the downstream formatter module reads that format
            var myMessage = humavg.toFixed(2) + "," + tempavg.toFixed(2) + "\r";
            console.log("edgeprocessor output: " + myMessage);

            // send the message to the broker to move it on downstream
            this.broker.publish({
                        properties: {},
                        content: new Uint8Array(Buffer.from(myMessage))
            });

            // reset our counters and running totals
            this.humtotal = 0;
            this.temptotal = 0;
            this.samplecount = 0;
        }

    },

    destroy: function() {
        console.log('edgeprocessor.destroy');
    }
};
