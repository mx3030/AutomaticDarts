import sys
import os
import json
import asyncio
import websockets
from handlers.pipeHandler import PipeHandler

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage: python program.py <PIPE_PATH>")

    pipe_path = sys.argv[1]     
    pipeHandler = PipeHandler(pipe_path)
    pipeHandler.start()

    # conn_string = f"wss://{HOST}:{WS_PORT}/calc" 
    # async with websockets.connect(conn_string) as ws:
        # while True:
            # async for message in ws:
                # temp = json.loads(message)
                # topic = temp.get('topic')
                # data = temp.get('data')

            # except websockets.ConnectionClosed: 
                # break
