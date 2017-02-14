## Azure IoT Hub Device Management

### Introduction
In this lab we will focus on two new device management capabilities of IoT Hub, device twin and direct method. We will build on lab 2 and use direct methods and an aternative to cloud to device commnads as well a device twin to change the configuration of the device application.

You use a direct method to initiate device management actions (such as reboot, factory reset, and firmware update) from a back-end app in the cloud. The device is responsible for:

1. Handling the method request sent from IoT Hub.
2. Initiating the corresponding device specific action on the device.
3. Providing status updates through the reported properties to IoT Hub.

You use device twin to maintain a copy of the state of the device in in the cloud. Device twin provides 3 types of properties

1. **Tags**. A JSON document read and written by the solution back end. Tags are not visible to device apps.
2. **Desired properties**. Desired properties can only be set by the solution back end and can be read by the device app. The device app can also be notified in real time of changes on the desired properties.
3. **Reported properties**. Reported properties can only be set by the device app and can be read and queried by the solution back end.

### Step 1 - Add device direct methods and device twin

1. Back to your putty session, CD to *Module5* and open lab5.py 

        cd -
        cd Module5
        nano lab5.py

2. We made several modifications the the code from lab 2. Here is what we added

    1. Imported the json module so we can parse our device twin data
    2. Added several global variables to support our new code
    3. Changed the protocal to MQTT. Device management features are currently only supported via MQTT
    
            protocol = IoTHubTransportProvider.MQTT

    4. Added methods to support the new functionality 

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

    5. Set call back functions for direct methods and device twin

            #currently only available via MQTT
            if iotHubClient.protocol == IoTHubTransportProvider.MQTT:
                iotHubClient.set_device_twin_callback(device_twin_callback, TWIN_CONTEXT)
                iotHubClient.set_device_method_callback(device_method_callback, METHOD_CONTEXT)

    6. Modify the conntection information as you did in lab 2
            
            deviceID = ""
            deviceKey = ""
            iotHubHostName = "<yourhub>.azure-devices.net"  
    7. Exit nano by Ctrl+X then Y then enter
    8. Run the lab5.py script
   
            python lab5.py

### Step 2 - Use device twin to change the frequency of the data collection

1. Connect to IoT Hub via Device Explore. Enter your connection string using the iothubowner policy. Hit update
![Device Explorer](/images/m52.1.PNG)  
2. Click on the **Management** tab, select your device from the list and then click on **Twin Props**.
![Device Explorer](/images/m52.2.PNG)  
2. Add a desired property "frequency" with value of "1"
![Device Explorer](/images/m52.3.PNG)  

### Step 3 - Use direct method to change turn the LED On and Off

1. Using Device Explorer again, click on the **Call Method on Device** tab
2. Change the Method name to LEDOn or LEDOff and click on Call Method. Everything should work just as in lab 2.
![Device Explorer](/images/m53.2.PNG)  
3. Unlike cloud to device commands, direct methods will immidialty return a response. On your putty session, stop the script and repeat step 3.2. You should get an error like this:
![Device Explorer](/images/m53.3.PNG)  