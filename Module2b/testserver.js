var net = require('net');

var PIPE_NAME = "mypipe";
var PIPE_PATH = "./" + PIPE_NAME;

var L = console.log;

var bToggle = 0;

var server = net.createServer(function(stream) {
    L('Server: on connection')

    stream.on('data', function(c) {
        L('Server: on data:', c.toString());
    });

    stream.on('end', function() {
        L('Server: on end')
        server.close();
    });

    stream.write('Take it easy!');
	
	setInterval(function(){

		if(bToggle == 0)
		{
			bToggle=1;
			stream.write("ON");
		}
		else
		{
			bToggle=0;
			stream.write("OFF");
		}
	},20000);

});

server.on('close',function(){
    L('Server: on close');
})

server.listen(PIPE_PATH,function(){
    L('Server: on listening');
})



