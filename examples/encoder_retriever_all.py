from pybear import Manager
import time
import os
import sys

# Initialize the BEAR manager
bear = Manager.BEAR(port="/dev/ttyUSB0", baudrate=8000000)

# First scan for all available BEARs
print("Scanning for BEAR devices...")
found_bears = []
for m_id in range(101):  # Check IDs 0-100
    sys.stdout.write(f"\rScanning ID: {m_id}")
    sys.stdout.flush()
    data = bear.ping(m_id)[0]
    if data is not None:
        print(f"\nFound BEAR with ID {m_id}")
        found_bears.append(m_id)

if not found_bears:
    print("\nNo BEAR devices found. Please check connections.")
    sys.exit()

print(f"\nFound {len(found_bears)} BEAR devices with IDs: {found_bears}")

# Enable torque on all found BEARs
for m_id in found_bears:
    bear.set_torque_enable((m_id, 1))

try:
    while True:
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=== BEAR Position Monitor ===")
        print("Press Ctrl+C to exit\n")
        
        # Get and display position for each BEAR
        for m_id in found_bears:
            try:
                # Get position data
                position = bear.get_present_position(m_id)[0][0][0]
                # Get velocity data
                velocity = bear.get_present_velocity(m_id)[0][0][0]
                print(f"BEAR ID {m_id:3d}: Position = {position:8.3f} rad, Velocity = {velocity:8.3f} rad/s")
            except:
                print(f"BEAR ID {m_id:3d}: Communication Error")
        
        # Update rate
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nStopping monitoring...")

finally:
    # Disable torque on all BEARs
    for m_id in found_bears:
        try:
            bear.set_torque_enable((m_id, 0))
        except:
            pass
    
    # Close connection
    bear.close()
    print("Connection closed")