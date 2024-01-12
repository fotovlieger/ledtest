// WebSocket support
var targetUrl = `ws://${location.host}/ws`;
var websocket;
window.addEventListener("load", onLoad);

function onLoad() {
  initializeSocket();
  //setTimeout(onTimeout, 2000);
}

function onTimeout(){
  console.log("onTimeout");
  sendMessage('time');
  setTimeout(onTimeout, 300);
}

function initializeSocket() {
  console.log("Opening WebSocket connection MicroPython Server...");
  websocket = new WebSocket(targetUrl);
  websocket.onopen = onOpen;
  websocket.onclose = onClose;
  websocket.onmessage = onMessage;
}
function onOpen(event) {
  console.log("Starting connection to WebSocket server..");
}
function onClose(event) {
  console.log("Closing connection to server..");
  setTimeout(initializeSocket, 2000);
}

function onMessage(event) {
  console.log("WebSocket message received:", event);
  const obj = JSON.parse(event.data);
  updateValues(obj);
}

function sendMessage(message) {
  console.log("WebSocket send: ", message);
  websocket.send(message);
}

function updateLed(obj, id) {
  if(obj) {
    const val = obj[id];
    //console.log (id, val);
    const but = document.getElementById(id);
    if (but) {
      if (val=='on') {
        but.checked = true;
      }
      else if (val=='off') {
        but.checked = false;
      }
    }
  }
}

function updateColor(obj, id) {
  if(obj) {
    const val = obj[id];
    const  rgb = val.split(',').map(function(num) {
      return parseInt(num);
    });
    if (rgb.length==3) {
      console.log ('upd',id, val);
      const but = document.getElementById(id);
      if (but) {
        but.jscolor.fromString(hexColor(rgb));
      }
    }
  }
}

function onLedClicked(but) {
  console.log (but.id, but.checked);
  var msg = {};
  msg[but.id] = but.checked ? 'on' : 'off';
  sendMessage(JSON.stringify(msg));
};


function hexColor(rgb) {
    return '#' + (
        ('0' + Math.round(rgb[0]).toString(16)).slice(-2) +
        ('0' + Math.round(rgb[1]).toString(16)).slice(-2) +
        ('0' + Math.round(rgb[2]).toString(16)).slice(-2)
    ).toUpperCase();
}

function onColor(but, tgt) {
  var msg = {};
  msg[tgt] = '' +
            Math.round(but.channels.r) + ',' +
			Math.round(but.channels.g) + ',' +
			Math.round(but.channels.b)
  sendMessage(JSON.stringify(msg));

  console.log (JSON.stringify(msg));
}

function updateValues(obj) {
  updateLed(obj, 'led1');
  updateLed(obj, 'led2');
  updateLed(obj, 'led3');
  updateColor(obj, 'hans');
}