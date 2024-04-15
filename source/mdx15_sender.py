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
setZeroX = 0# X Offset to move workpiece on build plate
setZeroY = 0# Y Offset to move workpiece on build plate
z_at_material_surface=0
exit_flag=0
key_pressed=0
skey_pressed=0
gkey_pressed=0
bkey_pressed=0
z1=0
z2=6050
default_filename="../test/B_Neale_51x16.prn"
# Used by Box command
maxX=0
maxY=0
minX=0x7FFFFF
minY=0x7FFFFF

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
    command = ";IN;!MC1;PA;VS12;!VZ3;!PZ0,6050;PU136,322;\r\n"
    print(command)
    #print(command.encode())
    writeToMDX(command)
    
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

def displayBox():
    global setZeroX, setZeroY
    global default_filename
    global maxX, maxY, minX, minY
    global z1,z2
    
    setZRange(z1,z2)# Values from file stops us going sky high
    
    # Bottom Left
    command = "PU" + str(minX+setZeroX)+','+str(minY+setZeroY)+";"
    print(command)
    writeToMDX(command)
    
    # Top Left
    command = "PU" + str(minX+setZeroX)+','+str(maxY+setZeroY)+";"
    print(command)
    writeToMDX(command)
    
    # Top Right
    command = "PU" + str(maxX+setZeroX)+','+str(maxY+setZeroY)+";"
    print(command)
    writeToMDX(command)
    
    # Bottom Right
    command = "PU" + str(maxX+setZeroX)+','+str(minY+setZeroY)+";"
    print(command)
    writeToMDX(command)
    
    # Bottom Left
    command = "PU" + str(minX+setZeroX)+','+str(minY+setZeroY)+";"
    print(command)
    writeToMDX(command)
    
    #Origin
    command = "PU" + str(setZeroX)+','+str(setZeroY)+";"
    print(command)
    writeToMDX(command)
    
    setZRange(0,6050)# Default initialisation values.
    command = "PD" + str(setZeroX)+','+str(setZeroY)+";"
    print(command)
    writeToMDX(command)


def getBoxFromRML(filename):
    global setZeroX, setZeroY
    global default_filename
    global maxX, maxY, minX, minY
    global z1,z2
    
    if filename=='':
        filename=default_filename
        if maxX != 0 and maxY !=0:# we have processed a file
            # use stored Box
            displayBox()
            return
    default_filename=filename
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
                            if 'PU' in cmd or 'PD' in cmd:
                                if cmd != 'PU' and cmd != 'PD': # we have x,y values
                                    # need to move X,Y to offset values
                                    cmd=cmd.strip()# remove leading/trailing whitespace
                                    #print("CMD stripped"+cmd)
                                    current_move=cmd[:2]#first two digits
                                    if current_move == 'PD':# only process pen down
                                        current_x,current_y=[int(s) for s in cmd[2:].split(",") if s.isdigit()]#get two values seperated by comma after second letter
                                        #print ("PD", current_x,current_y)
                                        if current_x > maxX:
                                            maxX=current_x
                                        if current_x < minX:
                                            minX=current_x
                                        if current_y > maxY:
                                            maxY=current_y
                                        if current_y < minY:
                                            minY=current_y
                            elif '!PZ' in cmd in cmd:# Extract Z1,Z2 required for this file (only really need Z2 to set PU height)
                                try:
                                    #print(cmd)
                                    cmd=cmd.strip()# remove leading/trailing whitespace
                                    new_z1,new_z2=[int(s) for s in cmd[3:].split(",")]#get two values seperated by comma 
                                    print("Z1,Z2=",new_z1,new_z2)
                                    z1=new_z1
                                    z2=new_z2
                                except ValueError:
                                    # Handle the exception
                                    print('!PZWasn\'t an integer')
                        else:
                            print("Skipping ETX")
            # Show Box
            print("maxX:" + str(maxX) + " maxY:" + str(maxY) + "minX:" + str(minX) + "minY:" + str(minY))
            displayBox()
            
    except (FileNotFoundError, OSError):
        print("Sorry that doesn't exist!.........")

def process_RML(filename):
    global setZeroX, setZeroY
    global default_filename

    if filename=='':
        filename=default_filename
    else:
        default_filename=filename
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
                            if 'PU' in cmd or 'PD' in cmd:
                                if cmd != 'PU' and cmd != 'PD': # we have x,y values
                                    # need to move X,Y to offset values
                                    cmd=cmd.strip()# remove leading/trailing whitespace
                                    #print("CMD stripped"+cmd)
                                    current_move=cmd[:2]#first two digits
                                    current_x,current_y=[int(s) for s in cmd[2:].split(",") if s.isdigit()]#get two values seperated by comma after second letter
                                    #print ("Current move "+current_move+"X:"+str(current_x)+"Y:"+str(current_y))
                                    # Add Work Offsets
                                    cmd = current_move + str(current_x+setZeroX)+','+str(current_y+setZeroY)
                                    #print("CMD new"+cmd)
                            command = cmd+";"
                            print(command)
                            #tmp = input("Hit Enter to proces: ")
                            #if tmp == 's':
                            #    continue
                            ##print(command.encode())
                            writeToMDX(command)
                        else:
                            print("Skipping ETX")
            # Move to workpiece zero x,y, 100 (so a bit above the work piece)
            command="Z"+str(setZeroX)+","+str(setZeroY)+",100;"
            print(command)
            writeToMDX(command)
            # Move to Z0 (so we don't drag accross work piece
            # But can potentially re-machine e.g. add a deeper cut by moving Z0 down a bit
            command="Z"+str(setZeroX)+","+str(setZeroY)+",0;"
            print(command)
            writeToMDX(command)
    except (FileNotFoundError, OSError):
        print("Sorry that doesn't exist!.........")
        
def setX0Y0():
    global setZeroX, setZeroY
    global x,y
    
    setZeroX = x# X Offset to move workpiece on build plate
    setZeroY = y# Y Offset to move workpiece on build plate
    
    print("Work Offsets are X = " + str(setZeroX) + " Y = " + str(setZeroY));
    
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

def on_press(key):
    global exit_flag
    global key_pressed, skey_pressed, gkey_pressed, bkey_pressed
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
            case '9':
                z += step
                print("Z ="+str(z))
            case '3':
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
            case '6':# Right
                x+=step;
            case '4':# Left
                x-=step
                if x<0:
                    x=0
            case '8':# Up
                y+=step
            case '2':#Down
                y-=step
                if y<0:
                    y=0
            case 'G':#Goto Z 
                gkey_pressed=1
            case 'S':#Send file
                skey_pressed=1
            case 'B':#Send file
                bkey_pressed=1
                print("bkey_pressed")
            case 'X':
                setX0Y0()
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
                if x<0:
                    x=0
            case keyboard.Key.up:# Up
                y+=step
            case keyboard.Key.down:#Down
                y-=step
                if y<0:
                    y=0
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
            local_key=key_pressed #just some guff for exception block
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
        usr = input("Enter X,Y,Z ABS coordinate: ")
        try:
            #print(usr)
            new_x,new_y,new_z=[int(s) for s in usr.split(",")]#get three values seperated by comma 
            print(new_x,new_y,new_z)
            x=new_x
            y=new_y
            z=new_z
        except ValueError:
            # Handle the exception
            print('Wasn\'t an integer')
        print("You must not press a key until tool has stopped")
        moveXYZ(x, y, z)
        # start new listener thread
        listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release)
        listener.start()
        listener.wait()
    if bkey_pressed==1:
        # Box File selected
        bkey_pressed=0
        # Stop listener or we cant enter file name
        listener.stop()
        # Try to flush the buffer
        while msvcrt.kbhit():
            msvcrt.getch()
        usr = input("Enter filename ")
        print("You must not press a key until tool has stopped")
        getBoxFromRML(usr)
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


