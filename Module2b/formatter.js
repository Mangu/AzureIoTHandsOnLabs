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

        // read configuration..  device id and device key is passed into config for this module
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
        
        // import the file system module
        fs = require('fs')

        // read the deviceinfo.json file.  Easier to just hold the structure in an external file that just putting it in code
        fs.readFile('deviceinfo.json', 'utf8', function (err,data) {
            if (err) {
                console.log(err);
            }
            console.log(data);

        // the device info file has a placeholder for deviceID.  Put our real deviceID in
        var msgtxt = data.replace("%%DEVICEID%%", module.exports.deviceID);

    //	console.log('sending deviceinfo: ' + msgtxt);

        // publish the device info message to the broker so the iothub module can send it to azure
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

        // split the Temperature and Humidity into separate strings in an array
        var splitString = Buffer.from(message.content).toString().split('\r')[0].split(",");

        // create JSON message to send to iothub.
        var myMessage = {
            DeviceID : this.deviceID,
            Temperature : splitString[1],
            Humidity : splitString[0]
        };

        // publish message to send to iothub module.
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
