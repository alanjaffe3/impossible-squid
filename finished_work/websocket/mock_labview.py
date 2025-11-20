import asyncio
import websockets
import json
import random
from datetime import datetime

connected = set()

async def handler(websocket):
    print("Client connected")
    connected.add(websocket)
    try:
        await asyncio.Future()  # just keep it open
    finally:
        connected.remove(websocket)
        print("Client disconnected")

async def data_generator():
    while True:
        data1 = [
            "P1", "AVG", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), round(random.uniform(5, 10), 4), round(random.uniform(0, 1), 4), round(random.uniform(5, 10), 4), round(random.uniform(0, 1), 4), round(random.uniform(0, 1.5), 4), round(random.uniform(-1, 0), 4), round(random.uniform(0, 1), 4), round(random.uniform(-1, 0.5), 4)
        ]
        data2 = [
            "P2", "AVG", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), round(random.uniform(5, 10), 4), round(random.uniform(0, 1), 4), round(random.uniform(5, 10), 4), round(random.uniform(0, 1), 4), round(random.uniform(0, 1.5), 4), round(random.uniform(-1, 0), 4), round(random.uniform(0, 1), 4), round(random.uniform(-1, 0.5), 4)
        ]

        msg1 = ",".join(map(str, data1))
        msg2 = ",".join(map(str, data2))

        if connected:
            await asyncio.gather(
                *(ws.send(msg1) for ws in connected),
                *(ws.send(msg2) for ws in connected)
            )
            
        print("Sent:", msg1)
        print("Sent:", msg2)
        await asyncio.sleep(1)

async def main():
    server = await websockets.serve(handler, "127.0.0.1", 6340)
    print("Server running on ws://127.0.0.1:6340")

    await asyncio.gather(server.wait_closed(), data_generator())

if __name__ == "__main__":
    asyncio.run(main())
