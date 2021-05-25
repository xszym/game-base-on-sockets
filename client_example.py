import asyncio
import websockets
import os

async def handler():
	async with websockets.connect('ws://localhost:' + str(8881)) as websocket:
		while True:
			message = await websocket.recv()
			print(message)

asyncio.get_event_loop().run_until_complete(handler())