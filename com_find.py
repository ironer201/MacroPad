import serial.tools.list_ports
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("Scanning for available ports...")
print("-" * 50)

ports = serial.tools.list_ports.comports()

if not ports:
    print("No ports found! Check if Arduino is connected.")
else:
    for port in ports:
        print(f"Port: {port.device}")
        print(f"Description: {port.description}")
        print(f"Hardware ID: {port.hwid}")
        print("-" * 50)
        
        # Check if it might be Arduino
        if 'arduino' in port.description.lower() or 'usb serial' in port.description.lower() or 'ch340' in port.description.lower():
            print(f"✓ This is likely your Arduino on {port.device}")
            print("=" * 50)