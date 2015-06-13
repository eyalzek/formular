var express = require('express'),
    app = express(),
    fs = require('fs'),
    util = require('util'),
    spawn = require('child_process').spawn,
    tmp = require('tmp'),
    bodyParser = require('body-parser');

app.use(express.static('src'));
app.use(bodyParser.urlencoded({extended: true}));
app.use(bodyParser.json());

app.get('/', function(req, res) {
    res.sendFile('src/index.html');
});

app.post('/enter-info', function(req, res) {
    console.log('received personal info')
    console.log(req.body)
    tmp.file(function _tempFileCreated(err, path, fd, cleanupCallback) {
        if (err) throw err;
        fs.writeFile(path, JSON.stringify(req.body), function (err) {
            if (err) throw err;
            console.log('info save as: ', path);
            // run worker:
            var proc = spawn('python', ['formular.py', path], {stdio: [0, 1, 2]});
            // proc.stdout.on('data', function (data) {
            //   console.log('stdout: ' + data);
            // });

            // proc.stderr.on('data', function (data) {
            //   console.log('stderr: ' + data);
            // });

            // proc.on('exit', function (code) {
            //   console.log('child process exited with code ' + code);
            // });
        });
    });
    res.send('Info received!')
});

var server = app.listen(3000, function() {
    var host = server.address().address;
    var port = server.address().port;

    console.log('Example app listening at http://%s:%s', host, port);
});
