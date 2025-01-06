from pybear import Manager
import time
import sys

# Initialize the BEAR manager
bear = Manager.BEAR(port="/dev/ttyUSB0", baudrate=8000000)

# Scan for the BEAR ID
error = True
m_id = 0
while m_id < 10:
    data = bear.ping(m_id)[0]
    if data is not None:
        print("Found BEAR with ID %d." % m_id)
        error = False
        break
    m_id += 1

if error:
    print("No BEAR found. Please check the connection.")
    sys.exit()

# Set PID gains for velocity control
p_gain = 1.0
i_gain = 0.0
d_gain = 0.0
bear.set_p_gain_velocity((m_id, p_gain))
bear.set_i_gain_velocity((m_id, i_gain))
bear.set_d_gain_velocity((m_id, d_gain))

# Set BEAR to velocity control mode
bear.set_mode((m_id, 1))  # Mode 1 for velocity control

# Enable the BEAR
bear.set_torque_enable((m_id, 1))

# Get user input for desired speed
speed = float(input("Enter desired speed in rad/s: "))

# Command the BEAR to move at the specified speed
bear.set_goal_velocity((m_id, speed))

print(f"BEAR is moving at {speed} rad/s. Press Ctrl+C to stop.")

try:
    # Keep the program running to maintain the speed
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    # Stop the BEAR when interrupted
    bear.set_goal_velocity((m_id, 0))
    bear.set_torque_enable((m_id, 0))
    print("BEAR stopped.")