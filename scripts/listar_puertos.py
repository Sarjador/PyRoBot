import serial.tools.list_ports

puertos = serial.tools.list_ports.comports()
for p in puertos:
    print(f"{p.device} - {p.description}")