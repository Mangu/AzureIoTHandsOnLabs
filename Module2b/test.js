var SerialPort = require('serialport');

//portName = process.argv[2];
portName = 'COM4';

var myPort = new SerialPort(portName, {
baudRate: 9600,
parser: SerialPort.parsers.readline("\n")
});

//myPort.on('open', showPortOpen);
myPort.on('data', sendSerialData);
//myPort.on('close', showPortClose);
//myPort.on('error', showError);

function showPortOpen() {
console.log('port open. Data rate: ' + myPort.options.baudRate);
}

function sendSerialData(data) {
console.log(data);
}

function showPortClose() {
console.log('port closed.');
}

function showError(error) {
console.log('Serial port error: ' + error);
}