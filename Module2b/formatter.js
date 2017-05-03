'use strict';

module.exports = {
    broker: null,
    configuration: null,
    deviceID:  null,
    deviceKey:  null,

    create: function (broker, configuration) {
        this.broker = broker;
        this.configuration = configuration;

	console.log('formatter.create');

        if(this.configuration && this.configuration.deviceID && this.configuration.deviceKey) {
            this.deviceID = this.configuration.deviceID.toString();
            this.deviceKey = this.configuration.deviceKey.toString();
            return true;
        }
        else {
            console.error('This module requires the device id to be passed in via configuration.');
            return false;
        }

        return true;
    },

    start: function () {
	console.log('formatter.start');
	
	fs = require('fs')

	fs.readFile('deviceinfo.json', 'utf8', function (err,data) {
		if (err) {
		    console.log(err);
  		}
	  	console.log(data);

	var msgtxt = data.replace("%%DEVICEID%%", module.exports.deviceID);

	console.log('sending deviceinfo: ' + msgtxt);

        module.exports.broker.publish({
                    properties: {
			source: "mapping",    // needed for the iothub writer module
			deviceName: module.exports.deviceID,
			deviceKey: module.exports.deviceKey
                    },
                    content: new Uint8Array(Buffer.from(msgtxt))
       		});	
	});
    },

    receive: function(message) {
	
        //  message format is aa.bb,cc.dd\n
        // where aa.bb is Humidity to two decimal places and cc.dd is Temperature to two decimal places

	console.log('formatter.receive: ', Buffer.from(message.content).toString());

        var splitString = Buffer.from(message.content).toString().split('\r')[0].split(",");

        var myMessage = {
            DeviceID : this.deviceID,
            Temperature : splitString[1],
            Humidity : splitString[0]
        };

    // parse c and build JSON string
        this.broker.publish({
                    properties: {
			source: "mapping",    // needed for the iothub writer module
			deviceName: this.deviceID,
			deviceKey: this.deviceKey
                    },
                    content: new Uint8Array(Buffer.from(JSON.stringify(myMessage)))
       });	
    },

    destroy: function() {
        console.log('formatter.destroy');
    }
};
