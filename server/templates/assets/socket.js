var socket;
var host = window.location.host;

window.onload = function () {
  connect();
};

window.onbeforeunload = function () {
  socket.close();
};

var connect = function() {
  socket = new WebSocket('ws://' + host + '/socket');

  socket.onmessage = function (msg) {
    var data = JSON.parse(msg.data);
    var content = data.content.toString();

    messageHandler(content);
  };
};

var messageHandler = function(content) {
  document.querySelector('#message').innerHTML = content;
};

var send = function(message) {
  msg = JSON.stringify(message);
  socket.send(msg);
};

var run = function() {
  var d1 = document.getElementById('digit-1');
  var num1 = d1.options[d1.selectedIndex].value;
  
  var d2 = document.getElementById('digit-2');
  var num2 = d2.options[d2.selectedIndex].value;

  send({"type": "run", "num1": num1, "num2": num2});
};