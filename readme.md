## Azure IoT Hands On Labs

### Overview

This hands-on lab demonstrates what is involved in connecting a physical custom device up to the Azure IoT Remote Monitoring pre-configured solution, to both display the telemetry data sent from the device, but also demonstrate management of the device through that portal.  Additionally, we show you how to do simple "real time analytics" with Azure Stream Analytics to sense high temperatures and 'act' upon the high temperature alert by sending a command to light a warning light on the device.  The idea is to show how straightforward it is to 'round trip' data from a device, to Azure, through Stream Analytics, and back to the device

There are two different available methods for connecting the device to IoTHub, which can be used to demonstrate "smart devices" that are capable of talking directly to IoTHub, or "dumb" devices that communicate to the gateway through Azure IoT's Gateway SDK (http://github.com/azure/azure-iot-gateway-sdk).


In this workshop you will:

* Generate an instance of the Azure IoT Remote Monitoring solution
* Connect a temperature/humidity sensor to a Raspberry PI running Linux
    * optionally connect the sensor to an arduino device that emulates a "dumb" device and leverages the Raspberry Pi as a gateway
* Used the Azure IoT Python SDK to connect the Pi to Azure IotHub
    * Including the new device management features 
* Used Azure Stream Analytics to look for “high temperature” alerts
* Leveraged an Azure Function to send a command back to the alerting device

### Hardware

For the lab hardware, you need at a minimum, a RaspberryPi (2, 3, or ZeroW), a DHT22 temperature and humidity sensor, LED, resistors, breadboard and wires.  If you don't already have hardware, you can buy the kits from the links below (among many other places)

*	Raspberry PI 3 kit - https://www.adafruit.com/products/3058
*	DHT 22  Temperature and Humidity Sensor - https://www.adafruit.com/products/385
    *   (optional) - if you want to experience the gateway SDK, you need an Arduino device - https://www.adafruit.com/product/50 (feel free to substitute any other Arduino device with a USB port, like a Nano, for example).  You also need th correct USB cable to hook your arduino up to the Raspberry Pi

### Modules

* [Module 1 - Azure IoT Remote Monitoring pre-configured solution](Module1) 
* [Module 2 - Connect Device to IoT Hub](Module2)
    * [(optional) Module 2b - Connect Device to IoTHub via Gateway](Module2b)
* [Module 3 - Azure Stream Analytics](Module3)
* [Module 4 - Azure Functions](Module4)
* [Module 5 - Device Management](Module5)

### Prerequisites

* Install python 2.7 https://www.python.org/downloads/
* Install the Device Explorer tool from https://github.com/Azure/azure-iot-sdks/releases/download/2016-11-17/SetupDeviceExplorer.msi
* Install Putty (if on a Windows PC) - http://www.putty.org/ 
* If you want to do the Gateway SDK module (2b), install the Arduino IDE at http://arduino.cc
* Install drivers for the USB to Serial cable (we provide the actual cable) - https://learn.adafruit.com/adafruits-raspberry-pi-lesson-5-using-a-console-cable?view=all 
* Access to an Azure Subscription

### Useful Resources 

#### Azure IoT Reference Architecture
The reference architecture provides guidance for building secure and scalable, device-centric solutions for connecting devices, conducting analysis, and integrating with back-end systems.

http://download.microsoft.com/download/A/4/D/A4DAD253-BC21-41D3-B9D9-87D2AE6F0719/Microsoft_Azure_IoT_Reference_Architecture.pdf

#### Azure IoT Preconfigured Solutions
The Azure IoT Suite preconfigured solutions are implementations of common IoT solution patterns that you can deploy to Azure using your subscription. You can use the preconfigured solutions: As a starting point for your own IoT solutions. To learn about common patterns in IoT solution design and development.

https://azure.microsoft.com/en-us/documentation/articles/iot-suite-what-are-preconfigured-solutions/

https://github.com/Azure/azure-iot-remote-monitoring 

#### SDKs

https://github.com/Azure/azure-iot-sdks - device sdk

https://github.com/azure/azure-iot-gateway-sdk - device gateway sdk

https://github.com/Azure/azure-iot-protocol-gateway/blob/master/README.md - protocol gateway

#### Security
[Securing Your Internet of Things from the Ground Up](http://download.microsoft.com/download/8/C/4/8C4DEF9B-041B-47F3-AD7F-52F391B1D0AB/Securing_your_Internet_of_Things_from_the_ground_up_white_paper_EN_US.pdf)

[How enterprises can enable IoT security]( http://blogs.microsoft.com/iot/2016/03/07/how-enterprises-can-enable-iot-security/#QoDqUlfc7CWlYhHf.99)

#### Other Services
[Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/)

[Azure Stream Analytic](https://docs.microsoft.com/en-us/azure/stream-analytics/stream-analytics-introduction )

[Azure App services](https://docs.microsoft.com/en-us/azure/app-service/app-service-value-prop-what-is) 

[Azure logic app](https://docs.microsoft.com/en-us/azure/logic-apps/) 

[Azure HDInsight](https://docs.microsoft.com/en-us/azure/hdinsight/ )

[Azure Machine Learning](https://studio.azureml.net/)

[PowerBi](https://powerbi.microsoft.com/en-us/documentation/powerbi-azure-and-power-bi/ )

[SignalR](https://www.asp.net/signalr/overview/deployment/using-signalr-with-azure-web-sites) 
