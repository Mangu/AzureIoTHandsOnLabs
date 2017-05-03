var net = require('net');
var SerialPort = require('serialport');

var PIPE_NAME = "mypipe";
// for Windows...
//var PIPE_PATH = "\\\\.\\pipe\\" + PIPE_NAME;
// for linux
var PIPE_PATH = "./" + PIPE_NAME;

var x = 0;

// EDIT:  update port name
// Windows
//portName = 'COM4';
// linux
portName = '/dev/ttyUSB0';

// open serial port
var myPort = new SerialPort(portName, {
baudRate: 9600,
parser: SerialPort.parsers.readline("\n")
});

// setup callback for getting serial data
myPort.on('data', sendSerialData);

// open named pipe for writing
var client = net.connect(PIPE_PATH, function() {
    console.log('Client: on connection');
})

// if we received a command, and it contains the string "ON", then send the "ON" command down the serial port
// otherwise send "OFF"
client.on('data', function(data) {
    console.log('Received Command:', data.toString());

    if(data.toString().indexOf("ON") > -1)
    {
	myPort.write("ON\n");
	myPort.drain();
	console.log('Sending Command: ON');
    }
    else
    {
	myPort.write("OFF\n");
	myPort.drain();
	console.log('Sending Command: OFF');
    }
    
});

client.on('end', function() {
    console.log('Client: shutting down');
})

//when we receive data from the serial port (i.e. the "dumb" arduino device), send it down the named pipe to the sensor module
function sendSerialData(data) {
	//  this is here because on linux, we don't necessarily start with a clean serial buffer for some reason I'm too lazy to troubleshoot..  :-)
	//  sometimes the first 'read' gets gibberish so we just make sure that what we received on the read is 12 bytes 
	//  (5 bytes of humidity including decimal point, a comma, 5 bytes of temp, and a newline)
	if(data.length == 12) {
		client.write(data.toString());
	}
	console.log(data);
}
