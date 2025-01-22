import sys
import time
from pybear import Manager

def main():
    # Initialize the BEAR manager
    bear = Manager.BEAR(port="/dev/ttyUSB0", baudrate=8000000)
    
    # Ask for BEAR ID
    while True:
        try:
            bear_id = int(input("Enter BEAR ID to move (0-100): "))
            if 0 <= bear_id <= 100:
                if bear.ping(bear_id)[0] is not None:
                    break
                else:
                    print(f"No BEAR found with ID {bear_id}. Please try again.")
            else:
                print("Please enter a number between 0 and 100.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Set PID gains
    p_gain = 0.02
    i_gain = 0.02
    d_gain = 0.0
    bear.set_p_gain_position((bear_id, p_gain))
    bear.set_i_gain_position((bear_id, i_gain))
    bear.set_d_gain_position((bear_id, d_gain))
    
    # Set target position
    try:
        target_position = float(input("Enter target position in radians: "))
    except ValueError:
        print("Invalid input. Exiting.")
        sys.exit()
    
    bear.set_goal_position((bear_id, target_position))
    bear.set_mode((bear_id, 2))  # Mode 2 for position control
    bear.set_torque_enable((bear_id, 1))
    
    print(f"Moving BEAR ID {bear_id} to {target_position} radians.")
    
    try:
        while True:
            current_position = bear.get_present_position(bear_id)[0][0][0]
            error = target_position - current_position
            print(f"Current Position: {current_position:.2f} rad, Error: {error:.2f} rad")
            if abs(error) < 0.01:
                print("Target position reached.")
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
    finally:
        bear.set_goal_position((bear_id, current_position))
        bear.set_torque_enable((bear_id, 0))
        bear.close()
        print("BEAR stopped.")

if __name__ == "__main__":
    main()