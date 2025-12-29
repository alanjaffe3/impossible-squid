import websocket
from time import sleep
import numpy as np
from move import *

# --------------------
# Configuration
# --------------------
sigSearchSize = 40000  # motor steps from center in each direction
sigSearchSteps = 200  # motor steps per move

ipTarget = "ws://192.168.1.83:6340"
searchDelay = 0.1

MAX_READS = 400  # keep last 100 signal reads

sigSearchArray = np.zeros((MAX_READS, 2))
sigIndex = 0

channel = 1
samples = 3

# --------------------
# Channel data parse settings
# --------------------
if channel == 1:
    min_idx = 8
    max_idx = 7
else:
    min_idx = 10
    max_idx = 9

# --------------------
# WebSocket setup
# --------------------
print("Connecting to websocket at", ipTarget)
ws = websocket.WebSocket()
ws.connect(ipTarget)
print(ws.recv())


# --------------------
# Data grab function
# --------------------
def dataGrab():
    totalSum = 0.0

    for _ in range(samples):
        lvlMsg = ws.recv()
        parts = lvlMsg.split(",")

        sigValue = float(parts[max_idx]) - float(parts[min_idx])
        totalSum += sigValue

        sleep(searchDelay)

    return totalSum / float(samples)


# --------------------
# Signal search routine
# --------------------
def sigSearch():
    global sigSearchArray, sigIndex

    x = 0
    y = 0
    i = 0
    j = 0

    sigMax = 0.0
    sigMaxX = 0
    sigMaxY = 0

    while j <= 2 * sigSearchSize:
        while i <= 2 * sigSearchSize:
            sigValue = dataGrab()

            if sigValue > sigMax:
                sigMax = sigValue
                sigMaxX = i
                sigMaxY = j

            # sigSearchArray[x][y] = sigValue
            sigSearchArray[sigIndex % MAX_READS, 0] = sigValue
            sigSearchArray[sigIndex % MAX_READS, 1] = sigMax
            sigIndex += 1

            print(f"{x},{y} sig: {sigValue}  sigMax: {sigMax} @ {sigMaxX},{sigMaxY}")
            if sigMax > 0.1:
                break
            mover(sigSearchSteps, 0, True)
            x += 1
            i += sigSearchSteps

        mover(0, sigSearchSteps, True)
        y += 1
        j += sigSearchSteps

        while i >= 0:
            sigValue = dataGrab()

            if sigValue > sigMax:
                sigMax = sigValue
                sigMaxX = i
                sigMaxY = j

            # sigSearchArray[x][y] = sigValue
            sigSearchArray[sigIndex % MAX_READS, 0] = sigValue
            sigSearchArray[sigIndex % MAX_READS, 1] = sigMax
            sigIndex += 1

            print(f"{x},{y} sig: {sigValue}  sigMax: {sigMax} @ {sigMaxX},{sigMaxY}")
            if sigMax > 0.1:
                break
            mover(sigSearchSteps, 0, False)
            x -= 1
            i -= sigSearchSteps

        mover(0, sigSearchSteps, True)
        y += 1
        j += sigSearchSteps

    print(f"Global sigMax: {sigMax} @ {sigMaxX},{sigMaxY}")
    print("Returning to center...")

    if x <= sigSearchSteps:
        mover(sigSearchSize, 0, True)
        mover(0, sigSearchSize, False)
    else:
        mover(sigSearchSize, 0, False)
        mover(0, sigSearchSize, False)

    print("...done moving back to approximate center")


# --------------------
# Run sequence
# --------------------
# mover((sigSearchSteps*sigSearchSize)/10, (sigSearchSteps*sigSearchSize)/10, False)

# moveToUpperLeftCorner()
sigSearch()
