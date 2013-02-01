import sys
import math
import random

if len(sys.argv) != 6:
    print 'Wrong Number of Arguments you sent', sys.argv
    print '[avgArrivalRate, avgStay, avgChargeNeed, timestep, interval]'
    sys.exit()
print 'parameters: ',sys.argv    

avgArrivalRate = float(sys.argv[1])
avgStay = float(sys.argv[2])
avgChargeNeed = float(sys.argv[3])
timestep = float(sys.argv[4])
interval = float(sys.argv[5])

# constants
# chargeRateMu
# chargeRateSigma 
chargeNeedMu
chargeNeedSigma
currentChargeSigma = 3 #kwh
currentChargeMu = 12 #kwh

uniformMaxCapacity = 60 #kwh
uniformChargeRate = 30 #kw


class Vehicle:
    numVehicles = 0

    def __init__(self, arrivalTime, depTime, chargeNeed, currentCharge, chargeRate, maxCapacity):
        self.id = numVehicles
        numVehicles+=1
        self.arrivalTime = arrivalTime
        self.depTime = depTime
        self.chargeNeed = chargeNeed
        self.currentCharge = currentCharge
        self.chargeRate = chargeRate
        self.maxCapacity = maxCapacity

    def getInfo(self):
        return [self.arrivalTime, self.depTime, self.chargeNeed, self.currentCharge, self.chargeRate, self.maxCapacity]

def simulateFCFS( arrayOfVehicles ):


def simulateInterval():
    arrivalTimes = []
    prevArrival = 0
    while True:
        nextArrival = math.floor(vehicleArrives(prevArrival))
        if nextArrival > interval:
            break
        arrivalTimes.append(nextArrival)
        prevArrival = nextArrival
    # arrivalsPerTimestep = [0] * int(math.ceil(interval / timestep))    
    # for arrivalTime in arrivalTimes:
    #     arrivalsPerTimestep[int(math.floor(arrivalTime/timestep))]+=1
    # print 'total arrivals = ',sum(arrivalsPerTimestep)
    #return arrivalsPerTimestep
    vehicles = vehicleGen( arrivalTimes )
    return vehicles

def vehicleGen( arrayOfArrivalTimes ):
    vehicles = []
    for arrival in arrayOfArrivalTimes
        depart = arrival + random.randint( 60, 180 )
        chargeNeed = 
        currentCharge = 
        chargeRate = 
        maxCapacity = 
        vehicles.append( Vehicle( arrival, depart, chargeNeed, currentCharge, chargeRate, maxCapacity) )
    return vehicles

def vehicleArrives(prevArrival):
    return prevArrival + random.expovariate( avgArrivalRate )

print simulateInterval()

