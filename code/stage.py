import serial
import time

class Stage:
    def __init__(self):
        self.ser = serial.Serial('com7',
                        baudrate=921600,
                        timeout=1.0,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS)

    def _write(self, command):
        out = command + "\r\n"
        self.ser.write(out.encode())
        
    def _read(self, command):
        self.ser.readline() #clear buffer
        self._write(command)
        raw_string = self.ser.readline()
        #print(raw_string)
        return raw_string.strip().decode()

    def get_position(self):
        return float(self._read("1TP"))

    def motor_on(self):
        self._write("1MO") #turn motor on
        output = self._read("1MO?")
        #print(output)
        assert output == '1', "Motor is off!"

    def read_velocity(self):
        v = self._read("1TV")
        return float(v)

    def move_absolute(self, x):
        self._write("1PA+{}".format(x))

        vel = self.read_velocity()
        
        while abs(vel) != 0:
            time.sleep(0.001)
            vel = self.read_velocity()
            
        return self.get_position()

    def move_relative(self, dx):
        x0 = self.get_position()
        self._write("1PR{}".format(dx))
        x1 = self.get_position()
        return x1-x0

    def home(self):
        """Calibrate the absolute coordinate system using the limit switches"""
        self._write("")
        

    def get_error_code(self):
        return int(self._read("TE?"))
        

    def close(self):
        self.ser.close()
        print("Bye bye")

if __name__=='__main__':

    import numpy as np
    
    s1 = Stage()
    s1.motor_on()

    #s1.home()

    print(s1.get_error_code())
    
    #print(s1.move_absolute(-0.5))
    print(s1.move_relative(-1.))
    
    s1.close()
    
