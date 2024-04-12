 Modela_MDX_Controller<br>

This is a quick and dirty python program which will connect to MDX-15 Engraver and will allow setting of Z0 and transmission of prn files with H/W flow control

The main core of this program is a port of this repo to python

https://github.com/EDUARDOCHAMORRO/SimplyFab-20

All credit to Eduardo Chamorro Martin he got me 90% there :-)

The three issues this program solves which the above one doesn't is

1) Software setting of Z0 - this means you can use the keyboard to acurately get the cutting tool to just touch the work piece top surface, and then tell the machine that this is Z0. This saves using the UP/DOWN keys on the machine itself - they are very laggy and work with the spindle on which can be a pain.

2) This software reliquishes COM1 when it exits. Unfortunately on Windows 11 Eduardo's software always seems to hold onto the resource handle even when it closes down which causes much annoyance.

3) The software also makes use of the latest pySerial which implements flow control and thus can throttle file sending when the MDX-15 RX buffer is full.

What it doesn't do is give you a fancy GUI interface its just a simple command line program that gets the job done.

Requirements:-

1) A Roland Modela MDX-15 (or MDX-20) others may be compatible.
2) A PC with an actual physical serial port - most USB serial converters do not implement Hardware handshaking. I tested the software using a Dell Latitude E6410 with a Serial port provided by its docking station. This was running Windows 10 Pro 22H2 which is 64Bit.
3) Recent Python 3.x install (I used v3.12.2)
4) PySerial v3.5
5) The Roland 2.5D "printer" driver must not be assigned to the com port in use (currently only COM1 supported). I assigned it to COM2 which meant it could be used for material size and speeds and feeds for the Roland programs but couldn't directly print to the MDX-15. Instead you print to a file and use this program instead.
6) A 9pin to 25pin NULL modem cable to connect the PC and 

Documentation:-

The following keys are accepted.

5 - Change Jog size - Cycles round 100, 10 or 1 step(s)<br>
M - Set Z at material surface - not needed supersceded by "Z"<br>
D – drilling hole (150 steps deep)<br>
H - Move Machine to Home position X=0,Y=0,Z=Zmax - not needed<br>
I - Send standard Initialisation commands - not needed<br>
E - Exit the program gracefully<br>
0 – spindle motor Off<br>
1 – spindle motor On<br>
T - Got material surface - not needed<br>
6 - Move Tool Right (X+)<br>
4 - Move Tool Left (X-)<br>
8 - Move Tool Away (Y+)<br>
2 - Move Tool Towards (Y-)<br>
3 - Move Tool down (Z-) - uses Jog Steps<br>
9 - Move Tool up (Z+) - uses Jog Steps<br>
Z - Set machines Z0 - use this to tell machine that tool is just touching workpiece Z height.<br>
X - Set machine X0 and Y0 to current position. Allows placement of job anywhere on build plate<br>
G - Goto specified Z height e.g G -2000 will move tool down from Zmax to almost touching baseplate use with caution.<br>
S - Send file this is expecting the name of an ASCII text file following the RML-1 standard. e.g. as created by Dr. Engrave supplied by Roland.<br>
<br>
B - Get X,Y (min+max) from a file and move machine around the perimeter, this is expecting the name of an ASCII text file following the RML-1 standard. e.g. as created by Dr. Engrave supplied by Roland. The software will remember the filename and use it as the default. On subsequent calls if no filename provided it will use the previous bounds.<br>
<br>
Typical use would be :-<br>
<br>
MDX-15 Power ON (workpiece moves to Viewing position)<br>
Press View button (LED off) Tool moves to home position (x=0,y=0,z=zmax)<br>
Run mdx15_sender.py<br>
Press 3 to move down<br>
Press 0 to switch off motor<br>
Use 3 (Z down) and 5 (Jog step size) to move Z to correct positiontool just touching workpiece<br>
Press Z to set Z0<br>
Use number or arrow keys to move X,Y position of workpiece.
Press X to set x,y offsets
Press B to set filename and move tool around the X,Y min max points.
Press S to Send file e.g. Filename: ..\test\B_Neale_51x16.prn<br>
Wait while engraving occurs (60 seconds) should see Zz when MDX buffer is full.<br>
E to exit<br>
View (LED on) to unload<br>
<br>
Alternate file ..\test\B_Neale_272_B.prn