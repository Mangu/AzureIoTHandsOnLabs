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
* Deploy the Azure gateway SDK to Raspberry Pi
* Write gateway modules to read from the Arduino (protocol translation), and convert the data to JSON (formatter), as examples of writing gateway modules
* Configure the gateway to authenticate to Azure IoT and run the solution

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

### Step 2 - Prepare Raspberry Pi as a gateway

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

Copy and paste (execute) the export message that shows up on screen to set the NODE_INCLUDE and NODE_LIB environment variables

    ./build.sh --enable-nodejs-binding
    cd ../samples/nodejs_simple_sample/nodejs_modules/
    npm install

The Node and SDK builds will take quite a while, so grab some coffee (and maybe go out to a long lunch!)

4.) 

