import sys
import time
import threading
from pybear import Manager
import keyboard  # Requires installation: pip install keyboard

# Initialize BEAR
bear = Manager.BEAR(port="/dev/ttyUSB0", baudrate=8000000)
m_id = 1  # BEAR ID

# Configuration parameters
force_value = 1.0  # Constant force to apply
ticks_forward = 100  # Number of ticks to move forward
ticks_backward = 100  # Number of ticks to move backward
tick_delay = 0.05  # Delay between ticks in seconds

# Set BEAR to force mode
bear.set_mode((m_id, 3))  # Mode 3 for force mode
bear.set_torque_enable((m_id, 1))  # Enable torque

# Flag to control direction
direction = 1  # 1 for forward, -1 for backward
running = True

def listen_for_space():
    global direction, running
    while running:
        if keyboard.is_pressed('space'):
            direction *= -1
            print(f"Direction switched to {'forward' if direction == 1 else 'backward'}")
            time.sleep(0.5)  # Debounce delay

def move_actuator():
    global running
    tick_count = 0
    while running:
        bear.set_force((m_id, force_value * direction))
        tick_count += 1
        if direction == 1 and tick_count >= ticks_forward:
            direction = -1
            tick_count = 0
            print("Reached forward limit. Switching to backward.")
        elif direction == -1 and tick_count >= ticks_backward:
            direction = 1
            tick_count = 0
            print("Reached backward limit. Switching to forward.")
        time.sleep(tick_delay)

try:
    print("Starting actuator control. Press 'space' to switch directions. Press 'Ctrl+C' to exit.")
    
    # Start listening for space bar in a separate thread
    listener_thread = threading.Thread(target=listen_for_space, daemon=True)
    listener_thread.start()
    
    # Start moving the actuator
    move_actuator()

except KeyboardInterrupt:
    print("\nExiting program.")

finally:
    # Disable BEAR
    bear.set_torque_enable((m_id, 0))
    bear.close()
    print("BEAR disabled and connection closed.")