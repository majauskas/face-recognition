var PythonShell = require('python-shell');
var pyshell = new PythonShell('face_recognition.py', {mode: 'json'});


pyshell.on('message', function (message) {
  console.log(message);
  if (message.hasOwnProperty('face')){
      
  }
      
});


pyshell.end(function (err) {
  if (err) throw err;
  console.log(err);
});






  

