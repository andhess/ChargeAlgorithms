import sys
import math
import random
import Queue
from vehicle import *
from chargePorts import *
from operator import attrgetter

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
edfQueue = []
queue = Queue.Queue(0) # infinite size
currentTime = 0 

#### Simulations

#print simulateInterval()


def updateVehiclesFCFS():

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

def listSwap( listA, aIndex, listB, bIndex ):
    tempA = listA[aIndex]
    listA[ aIndex ] = listB[bIndex]
    listB[ bIndex ] = tempA

# The Algorithms

#LLF




def updateLaxities(vehicle):
    


# EDF
earliestDLIndex = -1;
def simulateEDF( arrayOfVehicleArrivals ):
    global currentTime
    global earliestDLIndex
    #interval of arrivals 
    for minute, numVehiclesPerMin in enumerate( arrayOfVehicleArrivals ):
        for vehicle in numVehiclesPerMin:
            port = openChargePort()
            if port is not None:
                chargePorts[ port ] = vehicle
            else:
                edfQueue.append( vehicle )
                if earliestDLIndex == -1 or vehicle.depTime < edfQueue[earliestDLIndex].depTime:
                    earliestDLIndex = len(edfQueue)-1
        updateVehiclesEDF()
        currentTime += 1
    print "status:  " , openChargePort() , "  " , len(edfQueue)==0

    #finishing charging simulation after all vehicles have arrived
    while chargePortsEmpty() == False or not len(edfQueue)==0:
        updateVehiclesEDF()
        currentTime += 1
    print "status:  " , openChargePort() , "  " , len(edfQueue)==0," which evaluated to ", not len(edfQueue)==0 or openChargePort() is None

    print "current time: " , currentTime , "   done charging lot: " , len( doneChargingLot ) , "  failed charing lot: " , len( failedLot ) , "  edfQueue size:  " , len(edfQueue) , " chargePort " , chargePorts
    #for vehicle in failedLot:
    #    vehicle.failedToString()



def updateVehiclesEDF():
    global earliestDLIndex

    # advance 1 minute in the simulation
    for index, vehicle in enumerate( chargePorts ):
        if vehicle is not None:
            vehicle.currentCharge += (vehicle.chargeRate) / 60

            #check if done charging
            print "Charge:  " , vehicle.currentCharge , "   " , vehicle.chargeNeeded
            if vehicle.currentCharge >= vehicle.chargeNeeded:
                doneChargingLot.append( vehicle )
                if len(edfQueue) > 0:
                    chargePorts[index] = edfQueue[earliestDLIndex]
                    del edfQueue[earliestDLIndex]  
                    earliestDLIndex = earliestDL()
                else:
                    chargePorts[index] = None
            print "Timing:  " , currentTime , "   ",  vehicle.depTime 
            
            # check if deadline reached
            if currentTime >= vehicle.depTime:
                failedLot.append( vehicle )
                if len(edfQueue) > 0:
                    chargePorts[index] = edfQueue[earliestDLIndex]
                    del edfQueue[earliestDLIndex] 
                    earliestDLIndex = earliestDL()
                else:
                    chargePorts[index] = None

            # check if all cars in chargePorts still have best deadlines
            if earliestDLIndex != -1 and vehicle.depTime > edfQueue[earliestDLIndex].depTime:
                temp = vehicle
                chargePorts[index] = edfQueue[earliestDLIndex]
                edfQueue[earliestDLIndex] = temp
                #earliestDLIndex will remain the same


def earliestDL():
    if len(edfQueue) == 0:
        return -1
    return edfQueue.index(min(edfQueue,key=attrgetter('depTime')))





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
        updateVehiclesFCFS()
        currentTime += 1
    print "status:  " , openChargePort() , "  " , queue.empty()
    while chargePortsEmpty() == False or not queue.empty():
        updateVehiclesFCFS()
        currentTime += 1
    print "status:  " , openChargePort() , "  " , queue.empty()," which evaluated to ", not queue.empty() or openChargePort() is None

    print "current time: " , currentTime , "   done charging lot: " , len( doneChargingLot ) , "  failed charing lot: " , len( failedLot ) , "  queue size:  " , queue.qsize() , " chargePort " , chargePorts
    #for vehicle in failedLot:
    #    vehicle.failedToString()



simulateEDF( simulateInterval() )


### garbage
    # arrivalsPerTimestep = [0] * int(math.ceil(interval / timestep))    
    # for arrivalTime in arrivalTimes:
    #     arrivalsPerTimestep[int(math.floor(arrivalTime/timestep))]+=1
    # print 'total arrivals = ',sum(arrivalsPerTimestep)
    #return arrivalsPerTimestep