
var fs = require("fs");

//����ʽ���
//var data = fs.readFileSync('input.txt');

//console.log(data.toString());
//console.log("process end");

//������ʽ���
fs.readFile('input.txt', function(err,data) {
        if (err) return console.error(err);
        console.log(data.toString());
        }
        );
console.log("process end")
