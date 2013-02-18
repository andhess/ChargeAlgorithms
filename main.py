import sys
import fcfs
import edf
import llfSmart
import llfSimple
import poissonGen
import chargePorts
import vehicle
import csv


if len( sys.argv ) != 2:
    print 'Wrong Number of Arguments you sent', sys.argv , " .. just interval" 
    sys.exit()  

interval = int( sys.argv[ 1 ] )


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


#  -------- Simulations ------------

simulationInterval = poissonGen.simulateInterval()

print "number of vehicles in this simulation: ", numberOfVehiclesInSimulation

fcfs.simulateFCFS( simulationInterval )

# simulateEDF( simulationInterval )

# simulateLLF( simulationInterval )

# simulateLLFSimple( simulationInterval )

# testPoissonDistribution(1000)

print "----------------- end of simulations ------------------------"