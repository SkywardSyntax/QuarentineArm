from pybear import Manager
import time
import sys
from collections import deque
import numpy as np

# Initialize BEAR
bear = Manager.BEAR(port="/dev/ttyUSB0", baudrate=8000000)

# Find BEAR
error = True
m_id = 0
while m_id < 10:
    data = bear.ping(m_id)[0]
    if data is not None:
        print(f"Found BEAR with ID {m_id}")
        error = False
        break
    m_id += 1

if error:
    print("No BEAR found. Please check connection")
    sys.exit()

# Configure BEAR for velocity control
bear.set_mode((m_id, 1))  # Mode 1 for velocity control
bear.set_p_gain_velocity((m_id, 1.0))
bear.set_i_gain_velocity((m_id, 0.0))
bear.set_d_gain_velocity((m_id, 0.0))

# Set current limit
iq_max = 2.0  # Max current in Amps
bear.set_limit_iq_max((m_id, iq_max))

# Set collision detection parameters
iq_starting_threshold = 0.5  # Initial threshold
iq_asymptote_threshold = 0.4  # Final threshold
decay_rate = 0.3  # Controls how quickly threshold approaches asymptote
velocity = 1.0  # Constant velocity in rad/s
window_size = 5  # Size of rolling window for averaging
iq_window = deque(maxlen=window_size)  # Create rolling window buffer

# Enable BEAR
bear.set_torque_enable((m_id, 1))
bear.set_goal_velocity((m_id, velocity))

print("BEAR is moving. Press Ctrl+C to stop...")
start_time = time.time()

try:
    while True:
        # Calculate current threshold using exponential decay
        elapsed_time = time.time() - start_time
        current_threshold = iq_asymptote_threshold + (iq_starting_threshold - iq_asymptote_threshold) * np.exp(-decay_rate * elapsed_time)
        
        # Get current torque current
        iq = bear.get_present_iq(m_id)[0][0][0]
        iq_window.append(iq)
        
        # Calculate rolling average
        if len(iq_window) == window_size:
            iq_avg = sum(iq_window) / window_size
        else:
            iq_avg = iq
        
        # Get current velocity
        current_velocity = bear.get_present_velocity(m_id)[0][0][0]
        
        print(f"IQ: {iq:.2f} A, IQ Avg: {iq_avg:.2f} A, Threshold: {current_threshold:.2f} A, Velocity: {current_velocity:.2f} rad/s")
        
        # Check for collision using current threshold
        if abs(iq_avg) > current_threshold:
            print(f"Collision detected! Average Current: {iq_avg:.2f} A")
            bear.set_goal_velocity((m_id, 0))
            break
            
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nProgram interrupted by user")
finally:
    bear.set_goal_velocity((m_id, 0))
    bear.set_torque_enable((m_id, 0))
    bear.close()
    print("BEAR stopped")