# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import RPi.GPIO as GPIO
import time
import sys
import json

import Adafruit_DHT

import iothub_client
from iothub_client import *
from iothub_client_args import *

##############   values to change  ##############
deviceID = "<yourdeviceID>"
deviceKey = "<yourdevicekey>"
iotHubHostName = "<youriothubname>.azure-devices.net"  #ex: myiothub.azure-devices.net

######## put the lat and long of your fav place here ##########
######## otherwise we default to the center of the football universe ######
latitude = 33.208350
longitude = -87.550320

# by default, send telemetry messages every 5 seconds
# this property can be adjusted via device management and the device twin's
# 'desired' properties
message_interval = 5

# "constant" for the GPIO pin the LED is connected to.
LED_PIN = 19
# "constants" for the GPIO pin the DHT sensor is connected to and type
# the '22' parameter means we have a DHT22 (vs. a DHT11) sensor..  if you have a DHT11
# change the type to '11' -- otherwise you get inaccurate readings
DHT_TYPE = 22
DHT_PIN = 6

# HTTP options
# these value are only used if HTTP is used as the protocol (not the default)
# Because it can poll "after 9 seconds" polls will happen effectively
# at ~10 seconds.
# Note that for scalabilty, the default value of minimumPollingTime
# is 25 minutes. For more information, see:
# https://azure.microsoft.com/documentation/articles/iot-hub-devguide/#messaging
timeout = 241000
minimum_polling_time = 9

# messageTimeout - the maximum time in milliseconds until a message times out.
# The timeout period starts at IoTHubClient.send_event_async. 
# By default, messages do not expire.
message_timeout = 10000

# global counters - used mostly for debugging
receive_callbacks = 0
send_callbacks = 0
receive_context = 0
twin_callbacks = 0
method_callbacks = 0
twin_context = 0
method_context = 0
send_reported_state_callbacks = 0
send_reported_state_context = 0

# flag to indicate if we are in a high temp situation
# used to indicate whether or not to continue toggling the LED when we send
lockLED = False

# chose HTTP, AMQP or MQTT as transport protocol
# AMQP as the default
#protocol = IoTHubTransportProvider.AMQP
protocol = IoTHubTransportProvider.MQTT

# String containing Hostname, Device Id & Device Key in the format:
# this is the device-specific connection string, as opposed to the general hub
#	connection string
# "HostName=<host_name>;DeviceId=<device_id>;SharedAccessKey=<device_key>"
connection_string = "HostName=%s;DeviceId=%s;SharedAccessKey=%s"

# the parameterized message that we will send to IoTHub (we'll fill in temp and humidity later
msg_txt = "{\"deviceId\":\"%s\",\"Temperature\":%.2f,\"Humidity\":%.2f}"

# function to toggle the LED, just to indicate that we are sending data to IoTHub
def blinkLED(pin):
	global lockLED

	if(lockLED == True):
		return
	else:
		LEDOn(pin)
		time.sleep(.2)
		LEDOff(pin)
		return

# manually turn the LED on
def LEDOn(pin):
	GPIO.output(pin, GPIO.HIGH)
	return

# manually turn the LED off
def LEDOff(pin):
	GPIO.output(pin, GPIO.LOW)
	return

# read in the reported properties config file.  This tells the backend
# what properties we'll be reporting as part of our configuration
# and what 'direct methods' we support for calling.  We replace the
# latitude and longitude with the values specified above
def readReportedProperties():
	global latitude
	global longitude

	f = open("./reportedprops.json", "r")

	s = f.read()

	s = s.replace("%%LATITUDE%%", str(latitude))
	s = s.replace("%%LONGITUDE%%", str(longitude))

	return s

# read in the device info structure that we also send to the backend to
# describe the device to the pre-configured solution UI
def readDeviceInfo():
	global deviceID

	f = open("./deviceinfo.json", "r")

	s = f.read()

	s = s.replace("%%DEVICEID%%", deviceID)

	return s

# this is the 'callback' method for device twin updates.  This method gets invoked
# when the backend changes a 'desired' configuration parameter.  In our case, we
# only implement and respond to changes in the "TelemetryInterval" property (which sets the
# delay between telemetry sends
def device_twin_callback(update_state, payload, user_context):
    global twin_callbacks
    global message_interval
    global send_reported_state_context
    global iotHubClient

    print "\nTwin callback called with:\nupdateStatus = .%s.\npayload = %s\ncontext = %s" % (update_state, payload, user_context)

# the payload is a JSON structure.  Parse it
    j = json.loads(payload)

# when the device first connects, the IoTHub will send the entire configuration structure.  Subsequently
# IoTHub only sends a JSON "fragment" with only the parameters that have changed (i.e. "partial" update)
    if("PARTIAL" in str(update_state)):
	    print("New telemetry interval set to %s seconds" % j['Config']['TelemetryInterval'])
	    message_interval = int(j['Config']['TelemetryInterval'])
    else:
	    print("New telemetry interval set to %s seconds" % j['desired']['Config']['TelemetryInterval'])
	    message_interval = int(j['desired']['Config']['TelemetryInterval'])

# the cheap DHT22 temperature sensor really can't be 'queried' more than once every 2 or 3 seconds.   So we
# limit the miminum read rate
    if(message_interval < 3):
	print("Message interval cannot be < 3 seconds...  changing")
        message_interval = 3

    updated_config = "{\"Config\":{\"TelemetryInterval\":%d}}" % (message_interval)
    print("Sending updated telemetry interval to twin:  %s" % (updated_config))
    iotHubClient.send_reported_state(updated_config, len(updated_config), send_reported_state_callback, send_reported_state_context)

    twin_callbacks += 1

# this callback method gets called when the 'reported state' successfully gets reported
# to iothub via the device twin (an asynchronous process).  We aren't really doing
# anything with it, but it's here for troubleshooting purposes
def send_reported_state_callback(status_code, user_context):
    global send_reported_state_callbacks
#    print "Confirmation for reported state received with:\nstatus_code = [%d]\ncontext = %s" % (status_code, user_context)
    send_reported_state_callbacks += 1

# this callback is raised when the backend invokes a 'direct method' via the device twin. Generally
# you would 'dispatch' the call to the function that implements that functionality.
def device_method_callback(method_name, payload, user_context):
    global method_callbacks
    global lockLED

    print "\nMethod callback called with:\nmethodName = %s\npayload = %s\ncontext = %s\n" % (method_name, payload, user_context)
    method_callbacks += 1
#    print "Total calls confirmed: %d\n" % method_callbacks

# in our case, we only support two 'methods', LEDOn and LEDOff...  so we just dynamically call
# the appropriate function...   

    if('LEDOn' in method_name):
#	print("LEDOn was called")
    	lockLED = True
    else:
#	print("LEDOff was called")
	lockLED = False

    getattr(sys.modules[__name__], method_name)(LED_PIN)

    device_method_return_value = DeviceMethodReturnValue()
    device_method_return_value.response = "{ \"Response\": \"This is the response from the device\" }"
    device_method_return_value.status = 200

    return device_method_return_value

# this is the 'callback' method called whenever the SDK receives a "C2D" message
#	from IoTHub
def receive_message_callback(message, counter):
    global receive_callbacks
    global lockLED
    global LED_PIN

    # get the message that was received and parse it as a string
    buffer = message.get_bytearray()
    size = len(buffer)
    msg = buffer[:size].decode('utf-8')
    print("Received Message [%d]:" % counter)
    print("    Data: <<<%s>>> & Size=%d" % (msg, size))

    #if the message contains the string 'ON', then turn the LED on, else OFF
    if('ON' in msg):
	lockLED = True
	print("turning LED On")
	LEDOn(LED_PIN)
    else:
	lockLED = False
	print("Turning LED off")
	LEDOff(LED_PIN)

    counter += 1
    receive_callbacks += 1
    # tell IoTHub that we successfully processed the message
    return IoTHubMessageDispositionResult.ACCEPTED

# this function is the 'callback' that gets called whenever an event was
#	send to IoTHub (which happens asynchronously on a separate thread
#	we can tell if it was successfully sent or not, etc.  for the lab
#	we aren't doing anything with this 'callback' but if we are having
#	trouble we can uncomment for troubleshooting
def send_confirmation_callback(message, result, user_context):
    global send_callbacks
#    print("    Total calls confirmed: %d" #    print(
#        "Confirmation[%d] received for message with result = %s" %
#        (user_context, result))

# this function makes the actual connection to IoTHub and, depending on the
#	protocol chosen, set some configuration parameters
def iothub_client_init():
    global iotHubHostName
    global deviceID
    global deviceKey
    global connection_string
    global protocol

    connection_string = connection_string % (iotHubHostName, deviceID, deviceKey)
#    print("opening iotHubClient with connection string - %s" % connection_string)
    print("Starting the IoT Hub Python sample...")
    print("    Protocol %s" % protocol)
    print("    Connection string=%s" % connection_string)

    # prepare iothub client
    iotHubClient = IoTHubClient(connection_string, protocol)

    if iotHubClient.protocol == IoTHubTransportProvider.HTTP:
        iotHubClient.set_option("timeout", timeout)
        iotHubClient.set_option("MinimumPollingTime", minimum_polling_time)

    # set the time until a message times out
    iotHubClient.set_option("messageTimeout", message_timeout)

    # to enable MQTT logging set to 1
    # if protocol is MQTT (device twin is only supported on MQTT today)
    #    then set the twin related callbacks
    if iotHubClient.protocol == IoTHubTransportProvider.MQTT:
        iotHubClient.set_option("logtrace", 0)
        iotHubClient.set_device_twin_callback(device_twin_callback, twin_context)
        iotHubClient.set_device_method_callback(device_method_callback, method_context)

    # this is where we set the function that is the 'callback' for received
    #	messages
    iotHubClient.set_message_callback(
        receive_message_callback, receive_context)

    return iotHubClient

# Open the connection to IoTHub
iotHubClient = iothub_client_init()

# this function is the primary function called to get started once the
#	command line parameters have been parsed.
def iothub_client_sample_run():
    global deviceID
    global latitude
    global longitude
    global iotHubClient
    global LED_PIN
    global DHT_TYPE
    global DHT_PIN

    try:

	# initialize the message counter
	i=0

	# set up our LED pin as an output so we can control it
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(LED_PIN, GPIO.OUT)

	# connect to IoTHub
#        iotHubClient = iothub_client_init()

	# this message sends our device 'metadata' to the RM-PCS for display
	#	in the portal, it also sends the list of commands that this
	#	device supports, as well as it's latitude and longitude for
	#	display on the map!
	deviceInfoTxt = readDeviceInfo()
	print("Sending Device Info Message: %s" % deviceInfoTxt)

	# send the 'deviceinfo' message to IoTHub
	deviceInfoMsg = IoTHubMessage(bytearray(deviceInfoTxt, 'utf8'))
	iotHubClient.send_event_async(deviceInfoMsg, send_confirmation_callback, i)	

        #we can also use device twin to send properties to IoT Hub
        if iotHubClient.protocol == IoTHubTransportProvider.MQTT:
	    # load our reported properties from file (easier than building JSON string in code)
	    reported_props = readReportedProperties()
            #print "IoTHubClient is reporting state"
            iotHubClient.send_reported_state(reported_props, len(reported_props), send_reported_state_callback, send_reported_state_context)

	# main loop, run forever
        while True:

	    # read the humidity and temperature from the DHT sensor
	    humidity, temperature = Adafruit_DHT.read_retry(DHT_TYPE,DHT_PIN)

	    # every once in a while we get a bad reading from the sensor
	    #	hey, what do you expect, it costs $3  :-)
	    #	if we do get a bad reading, just delay 10 seconds and repeat
	    #	the loop
	    if((temperature is None) or (humidity is None)):
		print("Bad temperature or humidity reading received - skipping")
		time.sleep(10)
		continue

	    # fill in the humidity and temp in our parameterized template
	    #	string from earlier.  Also, convert temp reading from
	    #	celcius to farenheit
	    msg_txt_formatted = msg_txt % (deviceID, 
		temperature * 9/5 + 32, humidity)

	    print("Sending(%i):%s" % (i, msg_txt_formatted))

	    # create the message object, and send it
            message = IoTHubMessage(bytearray(msg_txt_formatted, 'utf8'))
            iotHubClient.send_event_async(message, send_confirmation_callback, i)
	    
	    # blink the LED attached to pin 19
	    blinkLED(LED_PIN)

            i += 1

	    # sleep for 3 seconds
	    time.sleep(message_interval)

    except IoTHubError as e:
        print("Unexpected error %s from IoTHub" % e)
        return
    except KeyboardInterrupt:
        print("IoTHubClient sample stopped")

def usage():
    print("Usage: iothub_client_sample.py -p <protocol> -c <connectionstring>")
    print("    protocol        : <amqp, http, mqtt>")
    print("    connectionstring: <HostName=<host_name>;DeviceId=<device_id>;SharedAccessKey=<device_key>>")

# the script entry point.  Read the command line and see if we specified
# 	a protocol or a connection string separate from the defaults
if __name__ == '__main__':
    print("\nPython %s" % sys.version)
    print("IoT Hub for Python SDK Version: %s" % iothub_client.__version__)

#    connection_string = connection_string % (iotHubHostName, deviceID, deviceKey)

#    try:
#        (connection_string, protocol) = get_iothub_opt(sys.argv[1:], connection_string, protocol)
#    except OptionError as o:
#        print(o)
#        usage()
#        sys.exit(1)

    # go!
    iothub_client_sample_run()
