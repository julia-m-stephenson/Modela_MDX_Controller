import serial
import time
from pynput import keyboard
import msvcrt

prevX = 0
prevY = 0
x = 0
y = 0
z = 0
step = 100; #steps to move each time
setZeroX = 0
setZeroY = 0
z_at_material_surface=0
exit_flag=0
key_pressed=0
skey_pressed=0
gkey_pressed=0

def writeToMDX(command):
    ser.write(command.encode())
    #time.sleep(1)
    #print("RTS "+str(ser.cts)+"DSR"+str(ser.dsr)+"RI"+str(ser.ri)+"CD"+str(ser.cd))
    while ser.dsr==False:
        print("Zz")
        time.sleep(1)# wait a second and see if printer is ready for more

def setZRange(z1, z2):
    command = "!PZ" + str(z1) + "," + str(z2) +";"
    print(command)
    #print(command.encode())
    writeToMDX(command)

#Open port at “9600,8,E,1”, non blocking HW handshaking:

try:
    ser = serial.Serial('COM1', 9600, timeout=0, parity=serial.PARITY_NONE, rtscts=1)#, rtscts=1, dsrdtr=1
except serial.serialutil.SerialException:
    print ("COM1 not connected")
    exit()
print(ser.name)
#initialize()
setZRange(-1120, 0)

def setMotorMode(mode):
    command = "!MC"+str(mode)+";"
    print(command)
    #print(command.encode())
    writeToMDX(command)
    #ser.write("!MC1;".encode())

def initialize():
    #print("ETX")
    #try:
    #    ser.write(3)
    #except serial.serialutil.SerialException:
    #    print ("Send ETX failed")
    #time.sleep(1)
    #print("IN;!MC1;PA;\r\n".encode())
    #ser.write("IN;!MC1;PA;\r\n".encode())
    print(";IN;!MC1;PA;VS12;!VZ3;!PZ0,6050;PU136,322;")
    ser.write(";IN;!MC1;PA;VS12;!VZ3;!PZ0,6050;PU136,322;\r\n".encode())
    
def home():
    command = "H;"
    print(command)
    #print(command.encode())
    writeToMDX(command)

def setZAtMaterialSurface():
    z_at_material_surface = z;
    print("Set z_at_material_surface to " + str(z_at_material_surface))

def toMM(milli_inch):
    return 0.0254 * milli_inch

def moveXYZ( x1,  y1,  z1):
    global x 
    x = x1
    global y 
    y = y1
    global z 
    z = z1
    command = "Z" + str(x) + ","  + str(y) + "," + str(z) +";"
    print(command)
    #print(command.encode())
    writeToMDX(command)

def goToMaterialSurface():
    print("going to material surface")
    moveXYZ(x,y, z_at_material_surface)

def drillHole(depth):
    global z
    start_z = z;
    end_z = z - depth
    setMotorMode(1)
    while (z > end_z):
        moveXYZ(x, y, z)
        z -= 3;
        time.sleep(1)
    setMotorMode(0);
    #initialize();
    moveXYZ(x, y, start_z)
    
def process_RML(filename):
    if filename=='':
        filename="../test/B_Neale_51x16.prn"
    print("Opening" + filename)
    try:
        with open(filename,"r") as f:
            for line in f:
                #print("GOT "+line)
                cmds = line.split(";")
                for cmd in cmds:
                    if not cmd.isspace():
                        #print("CMD "+cmd)
                        if cmd != str(3) :#and cmd !="PU136,322" :#ETX or Initial Pen up
                            command = cmd+";"
                            print(command)
                            #tmp = input("Hit Enter to proces: ")
                            #if tmp == 's':
                            #    continue
                            ##print(command.encode())
                            writeToMDX(command)
                        else:
                            print("Skipping ETX")
    except (FileNotFoundError, OSError):
        print("Sorry that doesn't exist!.........")

def setZ0():
    global z
    z_at_material_surface = z;
    #myPort.write("!ZM"+z+";");
    #print("!ZM"+z+";");
    #myPort.write("!PZ"+z+";");# After Z0 as it is relative to Z0???
    #print("!PZ"+z+";");
    
    command = "PR;"# Relative Coordinates
    print(command)
    ##print(command.encode())
    writeToMDX(command)

    command = "!ZO 0;"# Zero Here 
    print(command)
    ##print(command.encode())
    writeToMDX(command)

    z = 0;# Because we're in relative mode
#experiment add this hopefully fix weird every key moves down bug.
    
    command = "PA;"# Absolute Coordinates
    print(command)
    ##print(command.encode())
    writeToMDX(command)

    #myPort.write("!ZO"+z+";");# why change it again!!!
    #print("!ZO"+z+";");
def old_keyboad():
    #TODO: Change follwing to a keyboard.listner
    exit_flag=0
    while exit_flag == 0:
        usr = input("Enter command: ")
        while not usr.isalnum():
            print("Unacceptable "+usr)
            usr = input("Enter command: ")    
        match usr.upper():
            case '5':
                if step == 1:
                    step=100
                else:
                    if step==100:
                        step = 10
                    else:
                        if step==10:
                            step = 1
                print("Step ="+str(step))
            case '8':
                z += step
                print("Z ="+str(z))
            case '2':
                z -= step
                print("Z ="+str(z))
            case 'M':
                setZAtMaterialSurface();
                print(str(toMM(z_at_material_surface)) + " mm");
            case 'D':
                print("drilling hole");
                drillHole(150);
                print("drilled hole")
            case 'H':
                home();
                print("homed");
            case 'I':
                initialize();
                print("initialized");
            case 'E':
                print("Exit -- finishing up")
                break;
            case '0':
                setMotorMode(0);
                print("motor off");
            case '1':
                setMotorMode(1);
                print("motor on");
            case 'T':
                goToMaterialSurface();
            case 'L':# Right
                x+=step;
            case 'K':# Left
                x-=step
            case 'U':# Up
                y+=step
            case 'J':#Down
                y-=step
            case 'G':#Goto Z 
                usr = input("Enter Z ABS coordinate: ")
                try:
                    string_int = int(usr)
                    print(string_int)
                    z=string_int
                except ValueError:
                    # Handle the exception
                    print('Please enter an integer')
            case 'S':#Send file
                usr = input("Enter filename ")
                process_RML(usr)
            case 'Z':
                setZ0()
            case _:
                print("WTF? dude!")
                print("E - Exit, 0 - Motor Off, 1 - Motor On")
        print("next loop")
        moveXYZ(x, y, z)

def on_press(key):
    global exit_flag
    global key_pressed, skey_pressed, gkey_pressed
    global x,y,z,step
    try:
        ch=key.char
        mystr=''.join(ch)
        #print("STR="+mystr)
        #print('alphanumeric key {0} pressed'.format(key.char))
        # Actual processing
        match mystr.upper():
            case '5':
                if step == 1:
                    step=100
                else:
                    if step==100:
                        step = 10
                    else:
                        if step==10:
                            step = 1
                print("Step ="+str(step))
            case '8':
                z += step
                print("Z ="+str(z))
            case '2':
                z -= step
                print("Z ="+str(z))
            case 'M':
                setZAtMaterialSurface();
                print(str(toMM(z_at_material_surface)) + " mm");
            case 'D':
                print("drilling hole");
                drillHole(150);
                print("drilled hole")
            case 'H':
                home();
                print("homed");
            case 'I':
                initialize();
                print("initialized");
            case 'E':
                print("Exit -- finishing up")
                exit_flag=1
            case '0':
                setMotorMode(0);
                print("motor off");
            case '1':
                setMotorMode(1);
                print("motor on");
            case 'T':
                goToMaterialSurface();
            case 'L':# Right
                x+=step;
            case 'K':# Left
                x-=step
            case 'U':# Up
                y+=step
            case 'J':#Down
                y-=step
            case 'G':#Goto Z 
                gkey_pressed=1
            case 'S':#Send file
                skey_pressed=1
            case 'Z':
                setZ0()
            case _:
                print("WTF? dude! :"+mystr)
                print("E - Exit, 0 - Motor Off, 1 - Motor On")
        #print("next loop")
        moveXYZ(x, y, z)
        key_pressed=1


    except AttributeError:
        #print('special key {0} pressed'.format(key))
        # Actual processing
        match key:
            case keyboard.Key.page_up:
                z += step
                print("Z ="+str(z))
            case keyboard.Key.page_down:
                z -= step
                print("Z ="+str(z))
            case keyboard.Key.right:# Right
                x+=step;
            case keyboard.Key.left:# Left
                x-=step
            case keyboard.Key.up:# Up
                y+=step
            case keyboard.Key.down:#Down
                y-=step
            case _:
                print("WTF? dude! :")
                print("E - Exit, 0 - Motor Off, 1 - Motor On")
        #print("next loop")
        moveXYZ(x, y, z)
        key_pressed=1


def on_release(key):
    global exit_flag
    global key_pressed
    try:
        #print('{0} released'.format(key))
        if key == keyboard.Key.esc:
            exit_flag=1
            # Stop listener
            return False
        if key.char == 'E':#exit
            exit_flag=1
            # Stop listener
            return False
    except AttributeError:
        #print('special key {0} released'.format(key))
        if key==keyboard.Key.down:
            local_key=key_pressed#just some guff for exception block
# Collect events until released

listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()
listener.wait()

while exit_flag == 0:
    #print(key_pressed,exit_flag)
    if key_pressed==1:
        key_pressed=0
        print ("X= " +str(x) + " Y= " +str(y) + " Z= " +str(z))
    if skey_pressed==1:
        # Send File selected
        skey_pressed=0
        # Stop listener or we cant enter file name
        listener.stop()
        # Try to flush the buffer
        while msvcrt.kbhit():
            msvcrt.getch()
        usr = input("Enter filename ")
        process_RML(usr)
        # start new listener thread
        listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release)
        listener.start()
        listener.wait()
    if gkey_pressed==1:
        # Goto Z selected
        gkey_pressed=0
        # Stop listener or we cant enter file name
        listener.stop()
        # Try to flush the buffer
        while msvcrt.kbhit():
            msvcrt.getch()
        usr = input("Enter Z ABS coordinate: ")
        try:
            string_int = int(usr)
            print(string_int)
            z=string_int
        except ValueError:
            # Handle the exception
            print('Wasn\'t an integer')
        moveXYZ(x, y, z)
        print("You must not press a key until tool has stopped")
        # start new listener thread
        listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release)
        listener.start()
        listener.wait()

    time.sleep (1)

    # Try to flush the buffer
    while msvcrt.kbhit():
        msvcrt.getch()
# we are done close port
try: 
    ser.close()
    print ("COM1 closed")
except serial.serialutil.SerialException:
    print ("COM1 not closed")


