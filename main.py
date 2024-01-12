from math import *
import time
from utime import ticks_diff, ticks_ms
import asyncio
import json				# for cfg
import sys				# for exit
from machine import Pin
from neopixel import NeoPixel

from microdot_asyncio import Microdot, Response, send_file
from microdot_asyncio_websocket import with_websocket

state = {
    'led1':       'on',
    'led2':       'off',
    'led3':       'on',
    'hans':       '40,40,40',
}

connections = {
}

app = Microdot()
Response.default_content_type = 'text/html'

LEDS    = 12
strip1  = NeoPixel(Pin(26), LEDS, 3, 1)  #400kHz 0->800kHz
    
async def update_strip():
    while True:
        numbers = [int(num) for num in state['hans'].split(",")]
        if len(numbers)!=3:
            numbers = [10,10,10]
        strip1.fill((0, 0, 0))
        if state['led1']=='on':
            strip1[1]=(80,0,0)
        if state['led2']=='on':
            strip1[4]=numbers
        if state['led3']=='on':
            strip1[8]=(0,80,0)
        strip1.write()
        
        await asyncio.sleep(.2)  # Sleep before next iteration 

async def update_websockets():
    oldVal = ''
    while True:
        newVal = json.dumps(state)
        if oldVal != newVal:
            oldVal = newVal
            for ip, ws in connections.items():
                try:
                    print('update',ip)
                    await ws.send(json.dumps(state))
                except:
                    print('cancel',ip)
                    connections.pop(ip)

        await asyncio.sleep(.2)  # Sleep before next iteration

loop = asyncio.get_event_loop()
loop.create_task(update_strip())
loop.create_task(update_websockets())

@app.route('/')
async def index(request):
    print('index')
    return send_file("button.html")

@app.get('/shutdown')
def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'

def updateLed(data, id):
    try: 
        state[id] = data[id]
    except:
        pass
    
def updateColor(data, id):
    try: 
        state[id] = data[id]
    except:
        pass
    
def onUpdate(data):
    updateLed(data, 'led1')
    updateLed(data, 'led2')
    updateLed(data, 'led3')
    updateColor(data, 'hans')

@app.route('/ws')
@with_websocket
async def updater(request, ws):
    print('updater start', ws.request.client_addr)
    connections[ws.request.client_addr] = ws
    await ws.send(json.dumps(state))

    while True:
        msg = await ws.receive()
        try:
            data = json.loads(msg)
            print(json.dumps(data))
            onUpdate(data)
            
        except ValueError:  # includes simplejson.decoder.JSONDecodeError
            pass

         #time.sleep(0.1)
    print('updater end')

@app.route("/<path:path>")
def static(request, path):
    if ".." in path:
         return "Not found", 404
    try:
        os.stat(path)
    except:
        return "Not found", 404
    
    return send_file(path)

if __name__ == "__main__":
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        pass
