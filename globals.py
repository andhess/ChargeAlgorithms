# ---- storage lots ------

doneChargingLot = []
failedLot = []


# ----- global time vars ------
currentTime = 0 


# function to reset time, failed/done lots etc. Called at start of every algorithm simlulation
def updateGlobals():
    global currentTime
    currentTime = 0
    global doneChargingLot
    doneChargingLot = []
    global failedLot
    failedLot = []
    resetChargePorts()
