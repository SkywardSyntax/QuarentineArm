from pybear import Manager
import time
import sys

# Initialize the BEAR manager
bear = Manager.BEAR(port="/dev/ttyUSB0", baudrate=8000000)

def main():
    # Ask for BEAR ID
    while True:
        try:
            bear_id = int(input("Enter BEAR ID to monitor (0-100): "))
            if 0 <= bear_id <= 100:
                # Test if BEAR exists
                if bear.ping(bear_id)[0] is not None:
                    break
                else:
                    print(f"No BEAR found with ID {bear_id}. Please try again.")
            else:
                print("Please enter a number between 0 and 100.")
        except ValueError:
            print("Please enter a valid number.")

    print(f"\nMonitoring BEAR ID {bear_id}")
    print("Press Ctrl+C to exit\n")

    try:
        while True:
            try:
                # Get position data
                position = bear.get_present_position(bear_id)[0][0][0]
                print(f"\rPosition: {position:8.3f} rad", end='')
                time.sleep(0.1)
            except:
                print(f"\rCommunication Error", end='')
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nStopping monitor...")
    
    finally:
        bear.close()
        print("Connection closed")

if __name__ == "__main__":
    main()