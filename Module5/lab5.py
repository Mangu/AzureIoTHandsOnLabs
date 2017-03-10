   

# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import RPi.GPIO as GPIO
import random
import time
import sys
import json

import Adafruit_DHT

import iothub_client
from iothub_client import *
from iothub_client_args import *

##############   values to change  ##############
deviceID = "rpi-linux"
deviceKey = "3O+d1vc8CAMbQCn0U+9DSQ=="
iotHubHostName = "diaz-rnpcs.azure-devices.net"  #ex: myiothub.azure-devices.net

######## put the lat and long of your fav place here ##########
######## otherwise we default to the center of the football universe ######
latitude = 33.208350
longitude = -87.550320

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

# global counters
receive_callbacks = 0
send_callbacks = 0
receive_context = 0

TWIN_CALLBACKS = 0
METHOD_CALLBACKS = 0
TWIN_CONTEXT = 0
METHOD_CONTEXT = 0
SEND_REPORTED_STATE_CALLBACKS = 0
SEND_REPORTED_STATE_CONTEXT = 0

# flag to indicate if we are in a high temp situation
# used to indicate whether or not to continue toggling the LED when we send
highTemp = False


#data freq.
sleep_time = 3

# chose HTTP, AMQP or MQTT as transport protocol
# AMQP as the default
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
	global highTemp

	if(highTemp == True):
		return
	else:
		LEDOn(pin)
		time.sleep(.2)
		LEDOff(pin)
		return

# manually turn the LED on
def LEDOn(pin):
	global highTemp
	highTemp = True
	GPIO.output(pin, GPIO.HIGH)
	return

# manually turn the LED off
def LEDOff(pin):
	global highTemp
	highTemp = False
	GPIO.output(pin, GPIO.LOW)
	return

#using direct methods to issue commands
def device_method_callback(method_name, payload, user_context):
    global METHOD_CALLBACKS
    print "\nMethod callback called with:\nmethodName = %s\npayload = %s\ncontext = %s" % (method_name, payload, user_context)
    METHOD_CALLBACKS += 1
    print "Total calls confirmed: %d\n" % METHOD_CALLBACKS

    getattr(sys.modules[__name__], method_name)(35)

    device_method_return_value = DeviceMethodReturnValue()
    device_method_return_value.response = "{ \"Response\": \"This is the response from the device\" }"
    device_method_return_value.status = 200
    return device_method_return_value


def olddevice_twin_callback(update_state, payload, user_context):
    global TWIN_CALLBACKS
    print "\nTwin callback called with:\nupdateStatus = %s\npayload = %s\ncontext = %s" % (update_state, payload, user_context)
    TWIN_CALLBACKS += 1
    print "Total calls confirmed: %d\n" % TWIN_CALLBACKS

def device_twin_callback(update_state, payload, user_context):
    global TWIN_CALLBACKS
    global sleep_time

    print "\nTwin callback called with:\nupdateStatus = %s\npayload = %s\ncontext = %s" % (update_state, payload, user_context)
      
    p = json.loads(payload)
    sleep_time = int(p['frequency']) 
    
    TWIN_CALLBACKS += 1
    print "Total calls confirmed: %d\n" % TWIN_CALLBACKS


def send_reported_state_callback(status_code, user_context):
    global SEND_REPORTED_STATE_CALLBACKS
    print "Confirmation for reported state received with:\nstatus_code = [%d]\ncontext = %s" % (status_code, user_context)
    SEND_REPORTED_STATE_CALLBACKS += 1
    print "    Total calls confirmed: %d" % SEND_REPORTED_STATE_CALLBACKS




# this is the 'callback' method called whenever the SDK receives a message
#	from IoTHub
def receive_message_callback(message, counter):
    global receive_callbacks
    global highTemp

    # get the message that was received and parse it as a string
    buffer = message.get_bytearray()
    size = len(buffer)
    msg = buffer[:size].decode('utf-8')
    print("Received Message [%d]:" % counter)
    print("    Data: <<<%s>>> & Size=%d" % (msg, size))

    #if the message contains the string 'ON', then turn the LED on, else OFF
    if('ON' in msg):
	highTemp = True
	print("turning LED On")
	LEDOn(35)
    else:
	highTemp = False
	print("Turning LED off")
	LEDOff(35)

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
    global TWIN_CONTEXT
    global METHOD_CONTEXT

    # prepare iothub client
    iotHubClient = IoTHubClient(connection_string, protocol)
    if iotHubClient.protocol == IoTHubTransportProvider.HTTP:
        iotHubClient.set_option("timeout", timeout)
        iotHubClient.set_option("MinimumPollingTime", minimum_polling_time)
    # set the time until a message times out
    iotHubClient.set_option("messageTimeout", message_timeout)
    # to enable MQTT logging set to 1
    if iotHubClient.protocol == IoTHubTransportProvider.MQTT:
        iotHubClient.set_option("logtrace", 0)


    #set the call backs for device management features. 
    #currently only available via MQTT
    if iotHubClient.protocol == IoTHubTransportProvider.MQTT:
        iotHubClient.set_device_twin_callback(device_twin_callback, TWIN_CONTEXT)
        iotHubClient.set_device_method_callback(device_method_callback, METHOD_CONTEXT)

    # this is where we set the function that is the 'callback' for received
    #	messages
    iotHubClient.set_message_callback(
        receive_message_callback, receive_context)
    return iotHubClient

# this function is the primary function called to get started once the
#	command line parameters have been parsed.
def iothub_client_sample_run():
    global deviceID
    global latitude
    global longitude
    global SEND_REPORTED_STATE_CONTEXT
    global sleep_time

    try:

	# initialize the message counter
	i=0

	# set up our LED pin as an output so we can control it
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(35, GPIO.OUT)

	# connect to IoTHub
        iotHubClient = iothub_client_init()

	# this message sends our device 'metadata' to the RM-PCS for display
	#	in the portal, it also sends the list of commands that this
	#	device supports, as well as it's latitude and longitude for
	#	display on the map!
	deviceInfoTxt = "{\"ObjectType\":\"DeviceInfo\", \"Version\":\"1.0\", \"IsSimulatedDevice\":false, \"DeviceProperties\":{\"DeviceID\":\"%s\", \"HubEnabledState\":true, \"Latitude\":%.6f, \"Longitude\":%.6f}, \"Commands\":[{ \"Name\":\"ON\", \"Parameters\":[]},{ \"Name\":\"OFF\", \"Parameters\":[]}]}"
	deviceInfoTxt = deviceInfoTxt % (deviceID, latitude, longitude)	

	print("Sending Device Info Message: %s" % deviceInfoTxt)

	# send the 'deviceinfo' message to IoTHub
	deviceInfoMsg = IoTHubMessage(bytearray(deviceInfoTxt, 'utf8'))
	iotHubClient.send_event_async(deviceInfoMsg, send_confirmation_callback, i)	

	
        #we can also use device twin to send properties to IoT Hub
        if iotHubClient.protocol == IoTHubTransportProvider.MQTT:
            print "IoTHubClient is reporting state"
            reported_state = "{\"newState\":\"standBy\"}"
            iotHubClient.send_reported_state(reported_state, len(reported_state), send_reported_state_callback, SEND_REPORTED_STATE_CONTEXT)


	# main loop, run forever
        while True:

	    # read the humidity and temperature from the DHT22
	    # 	the '22' parameter means we have a DHT22 (vs. a DHT11) sensor
	    #	the '6' parameter means it is connected to pin 6 on the Pi		
	    humidity, temperature = Adafruit_DHT.read_retry(22,6)

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
	    
	    # blink the LED attached to pin 35
	    blinkLED(35)

            i += 1

	    # sleep for X seconds
	    time.sleep(sleep_time)

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

    connection_string = connection_string % (iotHubHostName, deviceID, deviceKey)

    try:
        (connection_string, protocol) = get_iothub_opt(sys.argv[1:], connection_string, protocol)
    except OptionError as o:
        print(o)
        usage()
        sys.exit(1)

    print("Starting the IoT Hub Python sample...")
    print("    Protocol %s" % protocol)
    print("    Connection string=%s" % connection_string)

    # go!
    iothub_client_sample_run()
