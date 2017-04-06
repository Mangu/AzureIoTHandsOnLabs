'use strict';

module.exports = {
    broker: null,
    configuration: null,
    deviceID:  null,

    create: function (broker, configuration) {
        this.broker = broker;
        this.configuration = configuration;

	console.log('formatter.create');

        if(this.configuration && this.configuration.deviceID) {
            this.deviceID = this.configuration.deviceID.toString();
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
    },

    receive: function(message) {
	
        //  message format is aa.bb,cc.dd\n
        // where aa.bb is Humidity to two decimal places and cc.dd is Temperature to two decimal places

//	console.log('formatter.receive: ', Buffer.from(message.content).toString());

        var splitString = Buffer.from(message.content).toString().split('\r')[0].split(",");

        var myMessage = {
            DeviceID : this.deviceID,
            Temperature : splitString[1],
            Humidity : splitString[0]
        };

    // parse c and build JSON string
        this.broker.publish({
                    properties: {
//			source: "formatter",
			source: "mapping",
			deviceId: "gwtestdevice",
			deviceName: "gwtestdevice",
			deviceKey: "Y7tOX9yDWKl/uW2s6YYfu+Slz1E0T9e/PFIT76jzIac="
                    },
                    content: new Uint8Array(Buffer.from(JSON.stringify(myMessage)))
       });	
    },

    destroy: function() {
        console.log('formatter.destroy');
    }
};
