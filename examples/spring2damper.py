#!usr/bin/env python
__author__ = "Xiaoguang Zhang"
__email__ = "xzhang@westwoodrobotics.io"
__copyright__ = "Copyright 2020 Westwood Robotics"
__date__ = "Aug 20, 2020"
__version__ = "0.1.0"
__status__ = "Production"

# -----------------------------
# BEAR with a bar, spring on one side, damper to the other side, with the 90 degree in the center being free.

from pybear import Manager
import sys
import select
import os
import time

error = False
bear_port = "/dev/ttyUSB0"
bear_baudrate = 8000000
bear = Manager.BEAR(port=bear_port, baudrate=bear_baudrate,timeout=1, bulk_timeout=1)


m_id = 7  # Set motor ID



p_gain = 5  # Set P gain as the K of spring
d_gain = 2  # Set D gain as damper strength
iq_max = 1.5  # Max iq

m_id = 1  # Start scanning from ID 1
error = True  # Initialize error flag

while m_id < 10:
    data = bear.ping(m_id)[0]
    if data:
        print("Found BEAR with ID %d." % m_id)
        print(data)
        error = False  # BEAR found
        break
    m_id += 1

if error:
    print("No BEAR found. Please check the connection.")
    sys.exit()

if not error:
    # BEAR is online
    # Set PID, mode and limit
    print("Welcome aboard, Captain!")
    # PID idiq
    bear.set_p_gain_iq((m_id, 0.02))
    bear.set_i_gain_iq((m_id, 0.02))
    bear.set_d_gain_iq((m_id, 0))
    bear.set_p_gain_id((m_id, 0.02))
    bear.set_i_gain_id((m_id, 0.02))
    bear.set_d_gain_id((m_id, 0))

    # Clear PID direct force
    bear.set_p_gain_force((m_id, 0))
    bear.set_i_gain_force((m_id, 0))
    bear.set_d_gain_force((m_id, 0))

    # Put into torque mode
    bear.set_mode((m_id, 3))

    # Set iq limit
    bear.set_limit_iq_max((m_id, iq_max))

    # Put bar in middle
    # usr = input("Please move the bar to upright position, then press enter to continue.")
    # Get home position
    print("Getting home position.")
    #home = bear.get_present_position(m_id)[0][0][0]
    home = 0
    print("Demo started.")
    #Get user input ()
    run = True
    while run:
        os.system('cls' if os.name == 'nt' else 'clear')
        pos = bear.get_present_position(m_id)[0][0][0]
        if abs(pos - home) < 0.78539816339:  # If distance between present_pos and home is lower than 45 deg
            # Disable and do nothing
            print("BEAR in free range.")
            bear.set_torque_enable((m_id, 0))
        elif (pos - home) > 0.78539816339: # If BEAR on the right side of free range
            # Enable and get into damping only
            print("BEAR in damping.")
            bear.set_p_gain_force((m_id, 0))
            bear.set_i_gain_force((m_id, 0))
            bear.set_d_gain_force((m_id, d_gain))
            bear.set_torque_enable((m_id, 1))

        elif (pos - home) < -0.78539816339:  # If BEAR on the left side of free range
            # Enable and get into spring only
            print("BEAR is now a spring.")
            bear.set_p_gain_force((m_id, p_gain))
            bear.set_i_gain_force((m_id, 0))
            bear.set_d_gain_force((m_id, 0))
            bear.set_torque_enable((m_id, 1))
            bear.set_goal_position((m_id, (home-0.78539816339)))
            # Check if iq_max reached
            iq = bear.get_present_iq(m_id)[0][0]
            if iq > iq_max:
                print("iq max reached.")
        print("Press any key to stop.")
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = input()
            run = False
            print("Demo terminated by user.")
            break
    print("Thanks for using BEAR!")