import asyncio
import websockets

async def main():
    path = input("Enter path (P1 or P2): ").strip().upper()
    port = 6341 if path == "P1" else 6342

    async def dummy_server(ws, _):
        await ws.wait_closed()

    server = await websockets.serve(dummy_server, "127.0.0.1", port)

    print(f"Relay server started on port {port}")

    async with websockets.connect("ws://127.0.0.1:6340") as ws_labview:

        toggle = 0
        sampleSize = 2
        maxSig = 7
        minSig = 8

        async for message in ws_labview:
            try:
                #print(f"Raw message: {repr(message)}")

                lvlMsg = message.strip()
                parts = lvlMsg.split(",")

                if parts[0].strip() == path:
                    liveMin = float(parts[minSig])
                    liveMax = float(parts[maxSig])
                    sigPP = liveMax - liveMin
                    sigAv = sigPP / float(sampleSize)

                    if toggle == 0:
                        print("> " + str(sigAv))
                        toggle = 1
                    else:
                        print("< " + str(sigAv))
                        toggle = 0

            except Exception as e:
                # Uncomment for debug
                # print(f"Error: {e}")
                continue

    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())