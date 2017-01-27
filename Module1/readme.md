### Introduction

In this lab, we will create an instance of the Azure IoT Remote Monitoring pre-configured solution (RM-PCS).  We will use this solution to:
* Pre-create some of the Azure infrastructure leveraged in the lab
* Visualize the data from our devices


The Azure IoT RM-PCS is a sample, or reference, IoT implementation that demonstrates how to build a starter solution that allows you to hook up a device, store and display meta-data about that device, ingest device data, apply some simple alerting rules, and visualize the device data.
In this series of labs you will:

1.	Create and navigate the Azure IoT Remote Monitoring Pre-configured Solution (RM-PCS)
2.	Create a device to read a temperature and humidity sensor (and optionally, a light sensor) and send that data to the RM-PCS for display
3.	Create a Stream Analytics job that looks for ‘high temperature’ alerts and outputs that alert to a queue for further processing
4.	Create an Azure Function that takes that alert, and sends a command to the device to turn on or off an LED depending on the alert condition.


#### Step 1 – Create the RM-PCS
1.	Open a browser and navigate to http://www.azureiotsuite.com
2.	Log-in with the credentials that are associated with your Azure Subscription  (most likely your corporate credentials)
3.	You should see the plus button shown below
![New Solution](/images/m1NewSolution.png)


4.	Click on the “+” to create your new solution.
5.	Under the “Remote Monitoring” option, choose the “Select” button
6.	On the “Solution Details” screen
    1. 	Note the Azure items that will be generated on your behalf
    2. 	Type in a unique solution name.  The name has to be globally unique, so typically some combination of your name or     initials, company, etc will help with that.  Once you enter an acceptable name, you will get a green checkbox         indicating that name is free to use and valid
    3. 	Choose our Azure Subscription from the drop down list box.  The components of the solution will be generated in       this subscription
    4. 	Choose your nearest and desired data center (i.e.  East US would be most appropriate for New Jersey)
    ![Add Location](/images/m1EnterLocation.png)
 

7.	Click “Create Solution” to start the solution deployment process
8.	Deployment should take about 15 minutes
9.	Once done, you should be able to click on the solution (click on the picture), and see the pop-out on the left like this one
![Confirmation](/images/m1Confirmation.png)

Congratulations – you have successfully deployed the Azure IoT RM-PCS

#### Step 2 – Review the solution portal
1.	Navigate to http://<<solutionname>>.azurewebsites.net where solutionname = the name chosen for the solution in step 1.6.2
2.	Log in with the same credentials used in above in step 1.2 above
3.	Reviewing the solution:
    1.	The home page shows you a map that includes four “sample” devices that are deployed with the solution
    2.	Choosing a sample device from the drop down list box shows telemetry being ingested, real-time, from that sample device
    3.	On the “devices” tab, you can click on one of the devices and display the metadata stored for that device
    4.	Clicking “commands” shows a list of commands that the device supports
    5.	Feel free to click around the rest of the portal.  In the next lab, we will explore adding a physical device to this portal and display it’s telemetry on the portal

Congratulations – you have completed Modele 1

