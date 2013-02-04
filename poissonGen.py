import sys
import math
import random
import Queue
from vehicle import *
from chargePorts import *

if len(sys.argv) != 2:
    print 'Wrong Number of Arguments you sent', sys.argv
    print 'interval'
    sys.exit()
#print 'parameters: ',sys.argv    

interval = int(sys.argv[1])

# constants

avgArrivalRate = .5

# chargeRateMu
# chargeRateSigma

# chargeNeeded - the charge needed at the end 
chargeNeededMu = 45 #kwh
chargeNeededSigma = 5 #kwh

currentChargeSigma = 3 #kwh
currentChargeMu = 12 #kwh

uniformMaxCapacity = 60 #kwh
uniformChargeRate = 30 #kw

doneChargingLot = []
failedLot = []
queue = Queue.Queue(0) # infinite size
currentTime = 0 

#### Simulations

#print simulateInterval()

simulateFCFS( simulateInterval() )


def updateVehicles():

    # advance 1 minute in the simulation
    for index, vehicle in enumerate(chargePorts):
        if vehicle is not None:
            vehicle.currentCharge += (vehicle.chargeRate) / 60

            #check if done charging
            print "Charge:  " , vehicle.currentCharge , "   " , vehicle.chargeNeeded
            if vehicle.currentCharge >= vehicle.chargeNeeded:
                doneChargingLot.append( vehicle )
                if not queue.empty():
                    chargePorts[index] = queue.get()  #careful
                else:
                    chargePorts[index] = None

            print "Timing:  " , currentTime , "   ",  vehicle.depTime 
            #  check if deadline reached
            if currentTime >= vehicle.depTime:
                failedLot.append( vehicle )
                if not queue.empty():
                    chargePorts[index] = queue.get()
                else:
                    chargePorts[index] = None


def simulateInterval():
    arrivalTimes = []
    prevArrival = 0
    while True:
        nextArrival = math.floor(vehicleArrives(prevArrival))
        if nextArrival >= interval:
            break
        arrivalTimes.append(nextArrival)
        prevArrival = nextArrival

    arrivalsPerMin = [0] * interval
    for arrivalTime in arrivalTimes:
        arrivalsPerMin[int(arrivalTime)]+= 1
    print "total number of vehicles:  " , len(arrivalTimes)
    vehicles = vehicleGen( arrivalsPerMin )
    return vehicles

def vehicleArrives(prevArrival):
    return prevArrival + random.expovariate( avgArrivalRate )

def vehicleGen( arrayOfArrivalsPerMin ):
    vehicles = []
    for minute,arrivalesDuringMin in enumerate(arrayOfArrivalsPerMin):
        if arrivalesDuringMin != 0 :
            vehiclesDuringMin = []
            for i in range(0, arrivalesDuringMin):
                depart = minute + random.randint( 60, 180 )
                chargeNeeded = random.gauss( chargeNeededMu, chargeNeededSigma )
                currentCharge = random.gauss( currentChargeMu, currentChargeSigma )
                chargeRate = uniformChargeRate
                maxCapacity = uniformMaxCapacity
                vehiclesDuringMin.append( Vehicle( minute, depart, chargeNeeded, currentCharge, chargeRate, maxCapacity) )
            vehicles.append(vehiclesDuringMin)
        else:
            vehicles.append( [] )
    return vehicles


# The Algorithms

# EDF


# FCFS

def simulateFCFS( arrayOfVehicleArrivals ):
    global currentTime
    for minute, numVehiclesPerMin in enumerate( arrayOfVehicleArrivals ):
        for vehicle in numVehiclesPerMin:
            port = openChargePort()
            if port is not None:
                chargePorts[ port ] = vehicle
            else:
                queue.put(vehicle)
        updateVehicles()
        currentTime += 1
    print "status:  " , openChargePort() , "  " , queue.empty()
    while chargePortsEmpty() == False or not queue.empty():
        updateVehicles()
        currentTime += 1
    print "status:  " , openChargePort() , "  " , queue.empty()," which evaluated to ", not queue.empty() or openChargePort() is None

    print "current time: " , currentTime , "   done charging lot: " , len( doneChargingLot ) , "  failed charing lot: " , len( failedLot ) , "  queue size:  " , queue.qsize() , " chargePort " , chargePorts
    #for vehicle in failedLot:
    #    vehicle.failedToString()






### garbage
    # arrivalsPerTimestep = [0] * int(math.ceil(interval / timestep))    
    # for arrivalTime in arrivalTimes:
    #     arrivalsPerTimestep[int(math.floor(arrivalTime/timestep))]+=1
    # print 'total arrivals = ',sum(arrivalsPerTimestep)
    #return arrivalsPerTimestep