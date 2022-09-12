import asyncio
from websockets import connect
import datetime
from streamz import Stream

source = Stream()
source.sink(print)


async def accelerometer(uri):
    async with connect(uri) as websocket:
        while True:
            data = await websocket.recv()  # push to the deque as the other example
            source.emit(data)


URI = "ws://192.168.1.3:8080/sensor/connect?type=android.sensor.accelerometer"
asyncio.run(accelerometer(URI))
