
var fs = require("fs");

//阻塞式编程
//var data = fs.readFileSync('input.txt');

//console.log(data.toString());
//console.log("process end");

//非阻塞式编程
fs.readFile('input.txt', function(err,data) {
        if (err) return console.error(err);
        console.log(data.toString());
        }
        );
console.log("process end")
