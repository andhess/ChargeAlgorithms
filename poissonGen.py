import sys
import math
import random
import Queue

if len(sys.argv) != 2:
    print 'Wrong Number of Arguments you sent', sys.argv
    print 'interval'
    sys.exit()
print 'parameters: ',sys.argv    

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

numChargePorts = 2


class Vehicle:
    numVehicles = 0

    def __init__( self, arrivalTime, depTime, chargeNeeded, currentCharge, chargeRate, maxCapacity ):
        self.id = numVehicles
        numVehicles += 1
        self.arrivalTime = arrivalTime
        self.depTime = depTime
        self.chargeNeeded = chargeNeed
        self.currentCharge = currentCharge
        self.chargeRate = chargeRate
        self.maxCapacity = maxCapacity

#    def getInfo(self):
#        return [self.arrivalTime, self.depTime, self.chargeNeeded, self.currentCharge, self.chargeRate, self.maxCapacity]


def simulateFCFS( arrayOfVehicleArrivals ):
    currentTime = 0
    chargePorts = [None] * numChargePorts;
    queue = Queue(0) # infinite size
    doneCharging = []
    while currentTime < interval:
        for minute in arrayOfVehicleArrivals
            for vehicle in minute
                port = openChargePort( chargePorts )
                if port:
                    chargePorts[port] = vehicle
                else
                    queue.put(vehicle)
        updateVehicles()
        currentTime += 1


        

def openChargePort(chargePorts):
    for index,port in enumerate(chargePorts):
        if port == None
            return index
    return None

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
        arrivalsPerMin[int(arrivalTime)]+=1
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
                vehiclesDuringMin.append( Vehicle( arrival, depart, chargeNeed, currentCharge, chargeRate, maxCapacity) )
            vehicles.append(vehiclesDuringMin)
        else
            vehicles.append( [] )
    return vehicles

print simulateInterval()






### garbage
    # arrivalsPerTimestep = [0] * int(math.ceil(interval / timestep))    
    # for arrivalTime in arrivalTimes:
    #     arrivalsPerTimestep[int(math.floor(arrivalTime/timestep))]+=1
    # print 'total arrivals = ',sum(arrivalsPerTimestep)
    #return arrivalsPerTimestep