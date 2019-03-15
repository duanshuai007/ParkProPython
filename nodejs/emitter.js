var EventEmitter = require('events').EventEmitter;
var event = new EventEmitter();

event.on('some_event', function(){
        console.log('come_event 111111');
        });

console.log('start process');
setTimeout(function() {
        event.emit('some_event');
        }, 1000);

console.log('process end');
