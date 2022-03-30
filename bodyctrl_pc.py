#!/usr/bin/env python

#================================================================
# Author  : Bruno JJE
# Date    : 04/2022
# License : GPL
#================================================================

import sys
import time
import socket
import struct
import pynput

#================================================================
# Keyboard/Mouse action definition
#================================================================
#
#   The following actions are defined (they have been tested
#   with the free to play game 'Destiny2' configured for
#   keyboard/mouse control).
#
#       right    : key 'D'
#       left     : key 'A'
#       forward  : key 'W'
#       backward : key 'S'
#       jump     : key 'SPACE'
#
#       toggle sprint : key 'SHIFT'
#       toggle crouch : key 'CONTROL'
#
#       fire     : left mouse button
#
#================================================================
#
#   By default, the actions associated to the control command
#   are not activated.
#
#   To toggle on and off the 'body control', you must stay about
#   10 seconds in frotn of the webcam in the vitruvian man stand
#   (arm and legs spread appart).
#
#================================================================
#
#   The following body control command are defined
#   (and linked to keyboard/mouse actions).
#
#       'B' : backward       : feet tight
#       'f' : forward        : feet appart
#       'F' : sprint forward : feet wide appart
#       '-' : ...            : feet naturally spread
#
#       'R' : right          : lean right
#       'L' : left           : lean left
#       '|' : ...            : straight standing, no left or right lean
#
#       'J' : jump           : jump (slightly crouch then stand straigth)
#       'C' : crouch         : slightly crouched stand
#
#       'r' : aim ot the right : point arms to the right
#       'l' : aim to the left  : point arms to the left
#
#       'S' : shot           : tighten the arms (join hands)
#       '.' : no shot        : keep your arms appart
#
#================================================================

keyboard = pynput.keyboard.Controller()
mouse = pynput.mouse.Controller()

sprint = 0
crouch = 0

def gen_action(cmd):

    global sprint
    global crouch

    #print("cmd='%s'" % cmd)

    for c in cmd:

        if c=='R': # right
            keyboard.press('d')
            keyboard.release('a')

        if c=='L': # left
            keyboard.press('a')
            keyboard.release('d')

        if c=='|': # neither right or left
            keyboard.release('d')
            keyboard.release('a')

        if c=='F': # sprint forward
            keyboard.press('w')
            keyboard.release('s')
            if sprint==0:
                keyboard.press(pynput.keyboard.Key.shift)
                keyboard.release(pynput.keyboard.Key.shift)
                sprint = 1

        if c=='f': # forward
            keyboard.press('w')
            keyboard.release('s')
            if sprint==1:
                keyboard.press(pynput.keyboard.Key.shift)
                keyboard.release(pynput.keyboard.Key.shift)
                sprint = 0

        if c=='B': # backward
            keyboard.press('s')
            keyboard.release('w')
            sprint = 0

        if c=='-': # neither forward or backward
            keyboard.release('w')
            keyboard.release('s')
            sprint = 0

        if c=='C': # crouch
            sprint = 0
            if crouch==0:
                keyboard.press(pynput.keyboard.Key.ctrl)
                keyboard.release(pynput.keyboard.Key.ctrl)
                crouch = 1

        if c=='J': # jump
            keyboard.press(pynput.keyboard.Key.space)
            keyboard.release(pynput.keyboard.Key.space)
            crouch = 0

        #if c=='u': # up
        #    mouse.move(0, -10)

        #if c=='d': # down
        #    mouse.move(0, 10)

        if c=='r': # right
            mouse.move(10, 0)

        if c=='l': # left
            mouse.move(-10, 0)

        if c=='S': # shot
            mouse.press(pynput.mouse.Button.left)

        if c=='.': # no shot
            mouse.release(pynput.mouse.Button.left)

#================================================================
# Get server IP address
#================================================================
if len(sys.argv) < 2:
    #TCP_IP_SERVER = input("Enter server IP address :")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
        TCP_IP_SERVER = s.getsockname()[0]
        s.close()
    except:
        TCP_IP_SERVER = "127.0.0.1"
else:
    TCP_IP_SERVER = sys.argv[1]

print('PC address:', TCP_IP_SERVER)

#================================================================
# Launch server
#================================================================
TCP_PORT_SERVER = 5007

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP_SERVER, TCP_PORT_SERVER))
s.listen(1)

print("Waiting client connection...")
conn, addr = s.accept()
print('Client connected with address:', addr)

#================================================================
# Main loop
#================================================================
unpacker = struct.Struct('16c')
time_old = time.time()
client_ok = True

while client_ok:
    try:
        data = conn.recv(unpacker.size)
        #print(len(data), data)
        unpacked_data = unpacker.unpack(data)
    except:
        client_ok = False
        break

    time_new = time.time()
    delta = time_new - time_old
    time_old = time_new
    print("DELAY =", int(delta*1000), "ms    FPS =", int(1/delta))

    cmd = b"".join(unpacked_data).decode().rstrip()
    gen_action(cmd)

#================================================================
# End
#================================================================
print("Client disconnected. End.")
conn.close()

