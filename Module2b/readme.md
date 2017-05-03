## Introduction
The purpose of this lab is to get a "dumb" IoT device connected to and talking to Azure IoTHub and the RM-PCS.  While this is demo device in a demo situation, it is very representative of the process of connecting any device to Azure via our Azure IoT Gateway SDK.  We will leverage an Arduino device and a DHT22 temperature and humidity sensor to represent our "dumb" device and a the Raspberry PI 3 as the IoT gateway. The gateway modules for this lab will be written in Node.js, however that is certainly not the only options.  Azure IoT gateway SDK modules can also be written in the following languages:

* C
* Java
* C#
* Node.js

In this series of labs, you will:

1. Create and navigate the Azure IoT Remote Monitoring Pre-Configured Solution (RM-PCS)
2. Create a device to read a temperature and humidity sensor and send that data to the RM-PCS for display
3. Create a Stream Analytics job that looks for ‘high temperature’ alerts and outputs that alert to a queue for further processing
4. Create an Azure Function that takes that alert, and sends a command to the device to turn on or off an LED depending on the alert condition.
    
At the end of this lab you will have a physical IoT device connected to an Azure IoT Gateway (connected via Wifi), sending telemetry data to Azure IoT.

At a high level, the steps of this lab involve

* Wire up and program the arduino device to represent a "dumb" device, and hook it up to the Raspberry Pi
* Create a 'custom' device in the RM-PCS solution
* Deploy the Azure gateway SDK to Raspberry Pi
* Write gateway modules to read from the Arduino (protocol translation), and convert the data to JSON (formatter), as examples of writing gateway modules
* Configure the gateway to authenticate to Azure IoT and run the solution
* Add some "edge processing" to the solution
* View the solution in the RM-PCS and send a test command to the device

### Step 1 - Arduino device setup and development

In this section, we will connect, setup, and program our Arduino device.  That will involve several tasks, including
*	Install the Arduino IDE
*   Familiarize yourself with the IDE and install the required libraries for our sensor
*   Physically connect the DHT22 temperature/humidity sensor to the Arduino
*   Develop and deploy the device code to read the DHT22 and send the data over the serial port to the gateway

##### Install the Arduino IDE

This lab module uses the Arduino IDE for development.  If this is not already installed on your workstation please follow these steps for installation:
1.	Using a web browser navigate to www.arduino.cc
2.	Click on the “Downloads” tab on the home page.
3.	Click on “Windows” for the current windows installer.

![ArduinoInstall](/images/m2bArduino1.png)

4. Using explorer launch the installer and follow the default prompts for installation.

![ArduinoInstall2](/images/m2bArduino2.png)![ArduinoInstall2](/images/m2bArduino3.png)

(Note:  Install USB driver is important as we’ll use this driver to communicate with the device and deploy code to it.) 

##### Familiarize ourselves with the Arduino IDE and install DHT libraries

1.)	Launch the Arduino Desktop App.  Upon launching you will be presented an empty project called a “sketch”.

![ArduinoIDE](/images/m2bArduino4.png)

2.)	Connect the Arduino device to the workstation with the USB cable.  (Note: the Arduino device can get power via either USB or an external power supply.  For the purposes of this workshop we’ll be getting power via USB)

3.)	In the Arduino IDE you must select your device as your deployment target.  Do this from the Tools -> Port menu:

![ArduinoIDE](/images/m2bArduino5.png)

4.)	Now that the device is setup in the IDE, you can open and deploy a sample sketch.  From the File -> Examples -> Basic menu open the “Blink” sketch.

![ArduinoIDE](/images/m2bArduino6.png)

5.)	Click the deploy button to load the sketch to the device.  After the sketch has deployed look at your Arduino to validate you have a blinking LED (once per second).

##### Assemble device

In this section, we will assemble the IoT device out of the arduino and DHT22 temp/humidity sensor

1.)	**Disconnect the Arduino from your workstation!!**.  Note this step is very important to ensure there is no electric charge running through the device while we’re assembling.

2.)	With the provided jumper wires and breadboard assemble the Arduino using the following schematic.  ** please note the diagram is logical and not to scale.  The first and second pins cannot really be separated like shown **

![schematic](/images/m2bArduino7.png)

This diagram may seem complicated, so let’s deconstruct it a bit.

3. )	The black wire is the ground wire; it runs to the right most pin on the DHT sensor.
4. )	The red wire provides power; it runs to the left most pin on the DHT sensor.
5. )	The green wire is the signal wire it runs to the pin adjacent to the power lead.
6. )	The resistor between pins 1 and 2 of the DHT sensor is called a "pull up" resistor.  It essentially just ensures that, during times we are not actively reading the sensor, the pin is "pulled up" to 5V and not electrically "bouncing around" freely.  This helps cut down on communication errors between the device and sensor.  **Note that resistors are not directional, so it doesn't matter which direction you plug the resistor into the breadboard**

##### Develop sketch to read sensor and send to gateway

In this section, we will write the arduino "code" to talk to the DHT sensor and send the temperature and humidity data across the serial port.  This is to represent a "dumb" device that can't talk to the cloud directly, but rather speaks a non-routable protocol (serial) and just blindly sends data down a console port

1.)	Plug your device back in to your workstation via USB.

2.)	In order to use the sensor we first need to download a library for simplifying communication with the device.  In the Arduino IDE select “Manage Libraries” from the Sketch -> Include Library menu.

![library install](/images/m2bArduino8.png)

3.)	From the library manager window search for “DHT”,  select the second option “DHT sensor library by Adafruit” library, and click “Install”.

![library install](/images/m2bArduino9.png)

4.)	When the install is complete close the Library Manager window.

5.)	Now it’s time to write some code.  First we must include a reference and some initialization code for the DHT sensor.  This includes referencing the installed module, defining which data pin we communicate on, and defining the sensor type (DHT22).  Put this code at the top of an empty new sketch

    #include <DHT.h>
    #define DHTTYPE DHT22

    //Set’s the pin we’re reading data from and initializes the sensor.
    int DHTPIN = 2;
    DHT dht(DHTPIN,DHTTYPE);
    String inputString = "";         // a string to hold incoming data
    boolean stringComplete = false;  // whether the string is complete
    #define pinLED 13     // pin 13 is the onboard LED

6.)	Next we need to open the connection to the sensor, open the port for communication of sensor readings (we’ll be using a serial connection over USB), and finally begin DHT sensor readings.  **In the provided setup() procedure** include the following:

    //Tell the arduino we’ll be reading data on the defined DHT pin
    pinMode(DHTPIN, INPUT);

    //Open the serial port for communication
    Serial.begin(9600);

    //start the connection for reading.
    dht.begin();
    // we will be 'writing' to the pin ( vs. reading)
    pinMode(pinLED, OUTPUT); 
    // start with the LED off
    digitalWrite(pinLED, LOW);

7.)	Finally, we need to capture the readings from the sensor and output them to the serial port.  The DHT22 sensor is only rated to read data once every 2 seconds so we’ll need to include some code to prevent reading too frequently.  We also add code to listen on the serial port for ‘commands’ from the gateway and turns the onboard LED on or off depending on the command.   **All the main application logic runs in the loop() procedure** which gets called after setup and runs as a never ending loop.

    //declare variables for storing temperature and humidity and capture
    float h = dht.readHumidity();
    float t = dht.readTemperature(true);

    //output data as humidity,temperature
    Serial.print(h);
    Serial.print(“,”);
    Serial.println(t);  //println includes linefeed
    serialEvent(); //call the function to read any command in the serial buffer
    // print the string when a newline arrives
    if (stringComplete) {

    // turn LED on or off depending on command
    if(inputString == "OFF")
        digitalWrite(pinLED, LOW); 
    if(inputString == "ON")
        digitalWrite(pinLED, HIGH);    
    // clear the string: 
    inputString = "";
    stringComplete = false;
    }
    
    //sleep for three seconds before reading again
    delay(3000);

8.)	We need to add the serialEvent function to loop through the read data from the serial buffer until it hits a newline and returns the string read from the port.  **add this code to the bottom of the file**

    void serialEvent() {
      // while there is data to read in the buffer, read it
      while (Serial.available()) {
        // get the new byte: 
        char inChar = (char)Serial.read();
        // add it to the inputString.  if it's a newline, bail as that completes the message
        if (inChar == '\n') {
          stringComplete = true; 
        }
        else
          inputString += inChar; 
      }
    }

9.)	Now that the code is complete you can deploy it to the device using the deploy button (after saving the sketch locally). A successful deployment will display the following:

![sketch deploy](/images/m2bArduino10.png)

10.)	To see that your sketch is running correctly use the serial monitor from the Tools menu.  This will display the data that the Arduino is sending over the COM port.

![sketch check](/images/m2bArduino11.png)

11.)	In the serial monitor, on the bottom right, make sure “newline only” is chosen.  Then type “ON” into the input box on the top, hit “SEND” and ensure the onboard LED lights up.  Type “OFF” and hit SEND and make sure the LED turns back off

12.)	Congratulations, you’ve built and programmed your sensor.  For more information on the DHT22 sensor see the adafruit website:  https://learn.adafruit.com/dht/overview 

#### Step 2 - Gathering IDs, Keys, and Connection Strings

Before we can connect the device to the Azure RM-PCS, we need to let the solution know about the device (so we can authenticate).  

1.	Navigate to your RM-PCS solution   (https://\[solutionname\].azurewebsites.net)
2.	On the bottom left corner, click the “Add a device” button
 
3.	Click Add New under “Custom Device”
4.	On the next screen, change the radio buttons to “let me define my own Device ID”, and pick a deviceID for your device
 ![Custom Device](/images/m2AddDevice.png) 
5.	Click Create
6.	Your device is now added to the RM-PCS.  Copy the three parameters displayed on this page, Device ID, IoTHub Hostname, and Device Key.  Paste them into notepad, as we will need them later on
7.	Click Done.  On the Devices screen, see that your device has been added to the list of devices in the solution.


### Step 3 - Prepare Raspberry Pi as a gateway

In this section, we will set up our Raspberry Pi for use as a gateway by downloading, building, and configuring the gateway SDK.  We assume your Raspberry Pi (RPI) is already installed and connected to the network (either wired or wireless) and that you can access it via SSH either over the network or serial console cable.  We further assume you are logged in under the 'pi' user name, if not, you'll need to adjust the path in a few commands and the gateway config.

**Note:  If you are doing this lab as part of an instructor-led delivery, this step MAY have already been done for you.  Ask your instructor!!**

1.) the first step is to clone the gateway SDK repository to your machine.  From the bash prompt, type:

    sudo apt-get update 
    sudo apt-get install curl build-essential libcurl4-openssl-dev git cmake libssl-dev uuid-dev valgrind libglib2.0-dev libtool autoconf
    git clone --recursive http://github.com/azure/azure-iot-gateway-sdk

2.) the RPI ships with an older version of Node.  We need to install the latest version with these steps:

    curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
    
and then
 
    sudo apt-get install nodejs

When finished, run
   
    node --version

and ensure the version number is 6.10.xx  (where XX may differ)

3.) The next step it to build the nodejs 'bindings' and the SDK itself.  This gets us the SDK and the ability to build gateway modules in node.js

From the RPI command line:
    
    cd <azure_iot_gateway_sdk_root>/tools/
    ./build_nodejs.sh 

(Note:  The Node and SDK builds will take quite a while, so grab some coffee (and maybe go out to a long lunch!))

4.) Copy and paste (execute) the export message that shows up on screen to set the NODE_INCLUDE and NODE_LIB environment variables

    ./build.sh --enable-nodejs-binding

Now we have all the necessary infrastructure to create a run a gateway.

### Step 4 - Review code and configure gateway

In this section we will download and review the gateway code for the lab, and configure the gateway.

**Note**:  As of this writing, there is a limitation in the gateway that just happens to expose itself in our specific scenario (reading from the serial port).  The issue occurs because the most popular (by far) Node library for reading from the serialport ('serialport') does a static link back into the Node executable itself (to leverage some function exported by the Node engine itself).  This is a rare occurence, but is unsupported by the gateway SDK.  This will not be an issue when the gateway SDK supports "out of process" Node modules, which is on our roadmap (it's supported in 'c' today).  So, to temporarily work around that, we actually have the gateway read from a named pipe.  We have a separate 'client' app that reads from the serial port and posts that data down the named pipe the gateway module is listening on.  The lab will be updated when out-of-process modules are supported in Node

1.) to get started, change back to the root of our user home directory

	cd ~

2.) clone the lab repository

	git clone --recursive http://github.com/mangu/AzureIoTHandsOnLabs

3.) change to the Module2b folder

	cd AzureIoTHandsOnLabs/Module2b

#### Anatomy of a gateway configuration

The configuration of the Azure IoT Gateway is controlled by a JSON configuration file.  The file contains three major types of entries:
* loaders - the MSFT provided libraries for 'loading' modules written in various languages
* modules - names, types (language), code/library location, and optional configuration information specific each module in the gateway pipeline
* links - the links between modules (i.e. which module receives messages published by which other modules).  Links are really what configures the 'pipeline' aspect of the gateway.

as an example of this, print out to the screen the contents of the file gateway_sample_lin.json.noedgeproc

	cat gateway_sample_lin.json.noedgeproc

Note the "links" section of the dumped JSON file (shown here)

    "links": [
        {
            "source": "*",
            "sink": "Logger"
        },
        {
            "source": "node_sensor",
            "sink": "node_formatter"
        },
        {
            "source": "node_formatter",
            "sink": "iothub"
        },
        {
            "source": "node_formatter",
            "sink": "node_printer"
        },
        {
            "source": "iothub",
            "sink": "node_printer"_
        },
        {
            "source": "iothub",
            "sink": "sensor"
        }
    ]

From a pipeline perspective, the data flows like this...

* data from every module (*) is sent to the logger component (for debug dumping to a file)
* the first module in the pipeline (nothing 'sources' it) is the node_sensor module.  This is the module doing "protocol translation" from our device.  Note, this data is the raw CSV-formatted temperature/humidity data from the 'dumb' Arduino device
* the data read from the sensor is sent to the node_formatter module.  This module will take the raw CSV data and re-format it to JSON, which is what we want to send to the IotHub.  The formatter module (just to have somewhere to put it), also sends the "device info" structure at startup to the RM-PCS, which uses it to drive the UI around what commands the device supports that can be sent to it.  This structure is specific to the RM-PCS and not generally a part of the gateway
* once the data leaves the node_formatter module, it is split.  One path sends the data to the Microsoft-provided 'iothub' module for tranmission up to IoTHub.  The other path sends the data to the node_printer module, whose simple job is dump the data to the screen for debugging
* the last two links deal with cloud-to-device commands coming to the device via ioTHub
  * the IoTHub module listens for commands from all devices that connect through it.  When a command is sent, a callback gets raised in that module and it drops the message back on the broker
  * We have two 'listeners' for that message, one is the printer to simply print out the received command, and
  * the other is the 'sensor' module, which from above, is the module that knows how to interact with the device.  The sensor module receives the command from IoTHub and, since we are just doing a simple test, passes the command along to the device.  The 'commands' in this case either contain the string 'ON' or 'OFF", which turns the on-board LED on the Arduino device on or off accordingly

#### Anatomy of a Node gateway module:

Let's take a look at the sensor module as an example of a typical Node module.  Open the sensor.js file in your favorite linux editor, for example:

	nano sensor.js

gateway modules are loaded and executed by the gateway module by exporting a set of well known methods.  These methods are implemented by the module and called by the engine over the lifetime of the gateway execution:

* create - called when the module is first loaded by the gateway engine.  A good place to read config, etc.  The gateway engine passes in a reference to the gateway's message broker, as well as the modules configuration from the configuration file.
* start - called when all modules are loaded and gateway execution is starting.  A good place for initialization
* receive - called whenever a message has been routed to the module by an upstream 'source'.  The message is sent in as a byte array and can be converted to a string by the code:  Buffer.from(message.content).toString()
* destroy - called when the gateway is shutting down.  Cleanup work goes here

One final thing to note, modules send data to the gateway pipeline (and thus other modules) by calling the broker.publish() method.  The module can set properties on the message, as well as send content (as a byte array, which can be created from a string by calling: new Uint8Array(Buffer.from(myMessageString)).  This can be seen in the formatter.js module.

ctrl-X lets you close the nano editor.  go ahead and open each of the node modules below and comb through the code to understand it.  A few notes:

* sensor.js - this module opens the named pipe mentioned above and reads the serial data from the device client and publishes it on the broker.  Note the empty receive() function because this module does not 'sink' any data from the broker, only 'sources'
* formatter.js - this module takes the CSV data from the sensor and JSON'ifys it.  Note the example of reading data from the broker, manipulating it, and publishing it back
* printer.js - dumps the received data to the console.  Would likely be left out of any production solution (as we have the logger module too)


#### gateway configuration and execution

1. ) The initial configuration (we'll play ith it later) of the gateway is in the file gateway_sample_lin.json.noedgeproc.  Open that file in your favorite linux editor

	nano gateway_sample_lin.json.noedgeproc

2. ) on line 40, replace \<yourdeviceid\> and \<yourdevicekey\> with the deviceID and deviceKey from the RM-PCS in Step 2

3. ) on line 51, replace \<youriothubname\> with the IoThub behind your RM-PCS (the IoTHub URI *without* the .azure-devices.net part)

4. ) review the rest of the configuration file and familiarize yourself with the rest of the config

5.) Hit

	CTRL-O
	<enter>
	CTRL-X

to exit the editor

6.) to execute the gateway, you run the ./gw executable, specifying the configuration file as a command line parameter:

	./gw gateway_sample_lin.json.noedgeproc

You will see some debug output indicating that the gateway is starting and each module is being loaded

7.) because of our temporary work around with the serial port, we need to run a separate client javascript program to actually read the data from the serial port and write it to the named pipe that the sensor.js module is listening too.  We will run this script in a separate putty window.  Open a new putty window and connect again to the raspberry pi.  Change to the ~/AzureIoTHandsOnLabs/Module2b folder again in this second window

8.) Before running the client, we need to install the serial port library by typing:

	npm install serialport

9.) now we are ready to run the client.js script.  At the bash prompt, enter

	node client.js

you will see the data being read from the arduino device over the serial port and written to the screen (and the named pipe).

Observe the gateway output, you should see output similar to the below:

	creating sensor
	formatter.create
	Gateway is running. Press return to quit.
	sensor.start - listening on  /home/pi/AzureIoTHandsOnLabs/Module2b/mypipe
	formatter.start
	creating server
	sensor.received:  55.40,73.58
	formatter.receive:  55.40,73.58
	Info: Retry policy set (5, timeout = 0)
	Info: Transport state changed from AMQP_TRANSPORT_STATE_NOT_CONNECTED to AMQP_TR                                                                                                                     ANSPORT_STATE_CONNECTING
	Info: Transport state changed from AMQP_TRANSPORT_STATE_CONNECTING to AMQP_TRANS                                                                                                                     PORT_STATE_CONNECTED
	printer.receive.properties: { source: 'mapping',
	  deviceName: 'gwtestdevice',
	  deviceKey: 'Y7tOX9yDWKl/uW2s6YYfu+Slz1E0T9e/PFIT76jzIac=' }
	printer.receive - {"DeviceID":"gwtestdevice","Temperature":"73.58","Humidity":"5                                                                                                                     5.40"}
	sensor.received:  55.40,73.58
	formatter.receive:  55.40,73.58
	printer.receive.properties: { source: 'mapping',
	  deviceName: 'gwtestdevice',
	  deviceKey: 'Y7tOX9yDWKl/uW2s6YYfu+Slz1E0T9e/PFIT76jzIac=' }
	printer.receive - {"DeviceID":"gwtestdevice","Temperature":"73.58","Humidity":"5                                                                                                                     5.40"}
	sensor.received:  55.40,73.58
	formatter.receive:  55.40,73.58
	printer.receive.properties: { source: 'mapping',
	  deviceName: 'gwtestdevice',
	  deviceKey: 'Y7tOX9yDWKl/uW2s6YYfu+Slz1E0T9e/PFIT76jzIac=' }
	printer.receive - {"DeviceID":"gwtestdevice","Temperature":"73.58","Humidity":"5                                                                                                                     5.40"}
	sensor.received:  55.40,73.58
	formatter.receive:  55.40,73.58
	printer.receive.properties: { source: 'mapping',
	  deviceName: 'gwtestdevice',
	  deviceKey: 'Y7tOX9yDWKl/uW2s6YYfu+Slz1E0T9e/PFIT76jzIac=' }
	printer.receive - {"DeviceID":"gwtestdevice","Temperature":"73.58","Humidity":"5                                                                                                                     5.40"}

	Gateway is quitting
	printer.destroy
	sensor.destroy
	formatter.destroy
	Info: Transport state changed from AMQP_TRANSPORT_STATE_CONNECTED to AMQP_TRANSP                                                                                                                     ORT_STATE_BEING_DESTROYED

To end execution, which to the window that is running the client.js app and hit CTRL-C.  Switch back to the gateway module window and hit \<enter>

### Step 5 - Add edge processing to the gateway

One of the many great uses for an IoT gateway is to do some processing "on the edge" before passing data on to the cloud backend.  Microsoft has announced formal support, in the form of Azure Stream Analytics running on the edge for robust SQL-based processing on the edge (more details -> https://azure.microsoft.com/en-us/blog/announcing-azure-stream-analytics-on-edge-devices-preview/).  At the time of this writing, however, that feature is in private preview, so just to demonstrate the concepts, we will implement a simple edge processor and add it to our gateway.

1.) review the edgeprocessor.js module.  This module, which we will insert between the sensor module and the formatter module, reads the sensor data and, rather than passing along every message from the sensor, takes the 'average' of the temperature and humidity over a configurable number of samples (default:5).  The edgeprocessor module then publishes this average value to the message broker for processing by the formatter module and sending to Azure.

Note that this demonstrates an important concept in gateway behavior.  Not every message has to make it through the pipeline.  Modules can aggregate messages from previous modules, change and republish them, or even drop them completely (filter), all based on the desired behavior of the gateway.

2.) to add the edge processing module into the pipeline requires a simple configuration change.  Edit the gateway_sample_lin.json file  (note it doesn't have .noedgeproc on the end)

	nano gateway_sample_lin.json

as with the previous configuration file, you need to edit and add the \<deviceID>, \<devicekey>, and \<iothubname> parameters.

Note that, in the *modules* section, we've added the details of the edgeprocessor module.  Also note that in the *links* section, we've changed the source and sink details to 'insert' the edgeprocessor module inbetween the sensor module and the formatter module.

save the configuration file and re-run the gateway with the new configuration

	./gw gateway_sample_lin.json

You should see output similar to the below:

		creating sensor
		formatter.create
		Gateway is running. Press return to quit.
		sensor.start - listening on  /home/pi/AzureIoTHandsOnLabs/Module2b/mypipe
		formatter.start
		edgeprocessor.start with sample size5
		creating server
		sensor.received:  55.70,73.22
		edgeprocessor.receive:  55.70,73.22
		sensor.received:  55.80,73.22
		edgeprocessor.receive:  55.80,73.22
		sensor.received:  55.80,73.22
		edgeprocessor.receive:  55.80,73.22
		sensor.received:  55.60,73.04
		edgeprocessor.receive:  55.60,73.04
		sensor.received:  55.80,73.22
		edgeprocessor.receive:  55.80,73.22
		edgeprocessor output: 55.74,73.18
		formatter.receive:  55.74,73.18
		printer.receive.properties: { source: 'mapping',
		  deviceName: 'gwtestdevice',
		  deviceKey: 'Y7tOX9yDWKl/uW2s6YYfu+Slz1E0T9e/PFIT76jzIac=' }
		printer.receive - {"DeviceID":"gwtestdevice","Temperature":"73.18","Humidity":"55.74"}
		sensor.received:  55.80,73.22
		edgeprocessor.receive:  55.80,73.22
		sensor.received:  55.80,73.22
		edgeprocessor.receive:  55.80,73.22
		sensor.received:  55.80,73.22
		edgeprocessor.receive:  55.80,73.22
		sensor.received:  55.80,73.22
		edgeprocessor.receive:  55.80,73.22
		sensor.received:  55.70,73.04
		edgeprocessor.receive:  55.70,73.04
		edgeprocessor output: 55.78,73.18
		formatter.receive:  55.78,73.18
		printer.receive.properties: { source: 'mapping',
		  deviceName: 'gwtestdevice',
		  deviceKey: 'Y7tOX9yDWKl/uW2s6YYfu+Slz1E0T9e/PFIT76jzIac=' }
		printer.receive - {"DeviceID":"gwtestdevice","Temperature":"73.18","Humidity":"55.78"}
		sensor.received:  55.80,73.22
		edgeprocessor.receive:  55.80,73.22

Note that now you only see the average temp and humidity being published after every 5 samples for downstream JSON formatting and sending to iothub.  We've aggregated and filtered data from our "dumb" device via an IoT gateway.

### Step 6 - View the device in the RM-PCS and test sending commands to the device

Now that we have data flowing up to the RM-PCS, we can take a look and interact with the device.  

1. ) navigate to the RM-PCS at (https://\[solutionname\].azurewebsites.net)  
2. ) from the drop down list box in the upper right, choose your device.   After a few minutes to load, you should see your temperature and humidity values from your device graphed on the screen.
3. ) On the left-hand nav, choose "Devices".  Select your device and a 'details' pane should open to the right.  In the upper part of the pane, click on "Commands"
4. ) on the commands screen, in the drop down list box, should be our "ON" and "OFF" commands
5. ) choose "ON" from the list box and click the "Send Command" button that appears
6. ) switch back over to the putty window that contains your running gateway, you should see a message similar to the following indicating that the iothub module has received a command and put it through the message broker (to the printer module) -- space added for emphasis

        edgeprocessor.receive:  58.50,69.62
        sensor.received:  58.60,69.62
        edgeprocessor.receive:  58.60,69.62
        
        printer.receive.properties: { source: 'iothub', deviceName: 'aaGWTest' }
        printer.receive - {"Name":"ON","DeliveryType":0,"MessageId":"6e4852fc-6d19-4416-ad2f-2f4b1793257b","CreatedTime":"2017-05-03T03:16:26.9672297Z","UpdatedTime":"0001-01-01T00:00:00","Result":null,"ReturnValue":null,"ErrorMessage":null,"Parameters":{}}
        
        sensor received command: {"Name":"ON","DeliveryType":0,"MessageId":"6e4852fc-6d19-4416-ad2f-2f4b1793257b","CreatedTime":"2017-05-03T03:16:26.9672297Z","UpdatedTime":"0001-01-01T00:00:00","Result":null,"ReturnValue":null,"ErrorMessage":null,"Parameters":{}}

        sensor.received:  58.60,69.62
        edgeprocessor.receive:  58.60,69.62

7. ) Within a few seconds, you should also see the on-board LED on the Arduinon light up
8. ) Back on the RM-PCS portal, refresh the browser page and notice the "success" status of the command
9. ) repeat step 5 and choose the "OFF" command.  Note the similar debug output from the GW and the LED turning back off

**Congratulations!  You've now connected a "dumb" device through a gateway, to Azure IoT, sending device telemetry data and bi-directional command and control.  The next modules will let you interact with that data further.**

