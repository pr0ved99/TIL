import asyncio
import json
import time
import random
import serial
import serial.tools.list_ports
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="STM32 Sensor Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

active_connections: list[WebSocket] = []

# Configuration for Serial Connection
BAUDRATE = 115200
# Update this with the actual COM port if known, e.g., "COM3"
# Or let it be None to auto-detect or fail directly to dummy mode
COM_PORT = None 

def generate_dummy_data() -> dict:
    """Generate dummy sensor data adhering to the specified format."""
    return {
        "sensor_id": "sensor_01",
        "value": round(random.uniform(20.0, 30.0), 2),
        "unit": "Celsius",
        "timestamp": round(time.time(), 3)
    }

async def serial_reader():
    """Background task to read serial data or generate dummy data."""
    serial_conn = None
    
    # Try to connect to serial port
    try:
        if COM_PORT:
            serial_conn = serial.Serial(COM_PORT, BAUDRATE, timeout=1)
            print(f"Connected to STM32 on {COM_PORT} at {BAUDRATE} baud.")
        else:
            # Try to auto-detect STM32 or just use dummy mode
            ports = list(serial.tools.list_ports.comports())
            stm32_ports = [p for p in ports if "STM32" in p.description or "STLink" in p.description]
            if stm32_ports:
                serial_conn = serial.Serial(stm32_ports[0].device, BAUDRATE, timeout=1)
                print(f"Auto-detected STM32 on {stm32_ports[0].device}")
            else:
                print("No STM32 port specified or detected. Starting in DUMMY MODE.")
                
    except Exception as e:
        print(f"Failed to connect to STM32. Error: {e}")
        print("Starting in DUMMY MODE.")
        serial_conn = None

    counter = 0
    while True:
        try:
            data_to_send = None
            
            if serial_conn and serial_conn.is_open:
                try:
                    # Read line from serial
                    if serial_conn.in_waiting > 0:
                        line = serial_conn.readline().decode('utf-8').strip()
                        if line:
                            try:
                                # Verify it's valid JSON
                                data_to_send = json.loads(line)
                            except json.JSONDecodeError:
                                print(f"Invalid JSON received from serial: {line}")
                except Exception as e:
                    print(f"Serial communication error: {e}. Switching to DUMMY MODE.")
                    serial_conn.close()
                    serial_conn = None
            
            if not serial_conn or not serial_conn.is_open:
                # Dummy mode
                data_to_send = generate_dummy_data()
                await asyncio.sleep(0.1) # Send dummy data every 0.1 second
                
            if data_to_send:
                counter += 1
                if counter % 50 == 0:
                    print(f"Sent 50 dummy data packets. Connected clients: {len(active_connections)}")
                # Broadcast to all connected clients
                disconnected_clients = []
                for connection in active_connections:
                    try:
                        await connection.send_json(data_to_send)
                    except Exception as e:
                        print(f"Error sending to client: {e}")
                        disconnected_clients.append(connection)
                
                # Clean up disconnected clients
                for client in disconnected_clients:
                    active_connections.remove(client)
            
            # Small sleep to yield control to event loop if reading from serial is fast
            if serial_conn and serial_conn.is_open:
                 await asyncio.sleep(0.01)
        except Exception as e:
            print(f"CRITICAL LOOP ERROR: {e}")
            await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    # Start the background task to read serial / generate dummy data
    asyncio.create_task(serial_reader())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Just keep the connection alive, we primarily send data TO the client
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print("Client disconnected.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
