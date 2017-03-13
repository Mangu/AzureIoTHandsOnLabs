var net = require('net');
var SerialPort = require('serialport');

var PIPE_NAME = "mypipe";
//var PIPE_PATH = "\\\\.\\pipe\\" + PIPE_NAME;
var PIPE_PATH = "./" + PIPE_NAME;

var x = 0;

//portName = process.argv[2];
//portName = 'COM4';
portName = '/dev/ttyUSB0';

var myPort = new SerialPort(portName, {
baudRate: 9600,
parser: SerialPort.parsers.readline("\n")
});

myPort.on('data', sendSerialData);

var L = console.log;// == Client part == //
var client = net.connect(PIPE_PATH, function() {
    L('Client: on connection');
})

client.on('data', function(data) {
    L('Client: on data:', data.toString());
//    client.end('Thanks!');
});

client.on('end', function() {
    L('Client: on end');
})

//setInterval(function() { 
//	client.write(x.toString());
//	x+=1;
//}, 1000);

function sendSerialData(data) {
	if(data.length == 12) {
		client.write(data.toString());
	}
	console.log(data);
//	console.log(data.length);
}
