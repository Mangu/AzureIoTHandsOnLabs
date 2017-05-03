## Azure IoT Hub Device Management

### Introduction
In this lab we will focus on two new device management capabilities of IoT Hub; device twin and direct method. We will build on lab 2 and use direct methods and an aternative to cloud to device commnads as well a device twin to change the configuration of the device application.

** NOTE:  Device management via the device twin and direct methods is not (yet) supported through the Azure IoT Gateway SDK.  You cannot do this lab if you connected your device via the gateway (per Module2b) **

You use a direct method to initiate device management actions (such as reboot, factory reset, and firmware update) from a back-end app in the cloud. The device is responsible for:

1. Handling the method request sent from IoT Hub.
2. Initiating the corresponding device specific action on the device.
3. Providing status updates through the reported properties to IoT Hub.

You use device twin to maintain a copy of the state of the device in the cloud. Device twin provides 3 types of properties

1. **Tags**. A JSON document read and written by the solution back end. Tags are not visible to device apps.
2. **Desired properties**. Desired properties can only be set by the solution back end and can be read by the device app. The device app can also be notified in real time of changes on the desired properties.
3. **Reported properties**. Reported properties can only be set by the device app and can be read and queried by the solution back end.

### Step 1 - Review Device Management Code

1. if it's running, stop the lab2.py code and open it in an editor

2. Review the device_twin_callback, device_method_callback, and the code that sends the initial default reported properties around line 323

3. close the editor and start the script running again

### Step 2 - Use device twin to change the frequency of the data collection

1. open the RM-PCS by navigating to http://[solutionname].azurewebsites.net.  Navigate to the devices tab and select your device to open the Device Details pane on the right hand side.

2. In the Desired Properties section of the Device Details pane, click Edit

3. In the Edit Desired Properties page, click in the edit box under "Desired Property Name".  It's likely you only have one desired property called "desired.Config.TemperatureMeanValue".  We are not going to use that.  Instead, type "desired.Config.TelemetryInterval" into the box.  Type '10'  (or any other number > 3) in the "Value" box.  
![Edit Desired Properties](/images/M5.edit_desired_properties.png)  

4. Click "Save Changes to Device Twin" button.   Switch back over to your putty session and notice that a JSON "fragment" has been pushed to the device indicating the desired property change, our changing of our telemetry interval, and the reporting back of the new 'reported' property for the telemetry interval.  Note that the delay between telemetry sends now matches the new desired configuration.
![Updated Desired Properties](/images/M5.updated_desired_props.png)

5. Switch back over to the RM-PCS device details and note that the device has reported it's new 'reported' configuration for the TelemetryInterval value.
![New reported property](/images/M5.new_reported_props.png)  

### Step 3 - Use direct method to change turn the LED On and Off

Like with the previous "C2D" commands, we are going to instruct the device to turn on and off the LED.  In this case, however, we are using direct methods, which are faster, but volatile, meaning the method call will fail if the device is offline.

1. In the Device Details pane for your device, in the upper right hand corner, click "Methods"
2. Change the Method name to LEDOn or LEDOff and click on Call Method. The LED shoudl light, just as in lab 2.  Switch back to the putty session and witness the feedback.
![Direct method call](/images/M5.direct_method_on.png)  
3. Unlike cloud to device commands, direct methods will immediately return a response. To witness this feedback, stop the python script and repeat step 3.2. You should get an error like this:
![Device Explorer](/images/M5.dm_offline_error.png)  
4. Unlike C2D commands, note that direct methods are not persisted.  If you start the python script back, note that the device does NOT pick up the method call like it did at the end of lab 2.

Congratulations - You've completed the labs and have a good IoT sample demo.
