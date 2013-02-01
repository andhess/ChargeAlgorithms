import sys
import math
import random

if len(sys.argv) != 2:
    print 'Wrong Number of Arguments you sent', sys.argv
    print 'interval'
    sys.exit()
print 'parameters: ',sys.argv    

interval = float(sys.argv[1])

# constants

averageArrivalRate = .5

# chargeRateMu
# chargeRateSigma

# chargeNeeded - the charge needed at the end 
chargeNeededMu = 45 #kwh
chargeNeededSigma = 5 #kwh

currentChargeSigma = 3 #kwh
currentChargeMu = 12 #kwh

uniformMaxCapacity = 60 #kwh
uniformChargeRate = 30 #kw


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

def vehicleGen( arrayOfArrivalTimes ):
    vehicles = []
    for arrival in arrayOfArrivalTimes
        depart = arrival + random.randint( 60, 180 )
        chargeNeeded = random.gauss( chargeNeededMu, chargeNeededSigma )
        currentCharge = random.gauss( currentChargeMu, currentChargeSigma )
        chargeRate = uniformChargeRate
        maxCapacity = uniformMaxCapacity
        vehicles.append( Vehicle( arrival, depart, chargeNeed, currentCharge, chargeRate, maxCapacity) )
    return vehicles


def simulateFCFS( arrayOfVehicles ):
    currentTime = 0
    while currentTime < interval:
        for vehicle in arrayOfVehicles


def simulateInterval():
    arrivalTimes = []
    prevArrival = 0
    while True:
        nextArrival = math.floor(vehicleArrives(prevArrival))
        if nextArrival > interval:
            break
        arrivalTimes.append(nextArrival)
        prevArrival = nextArrival

    vehicles = vehicleGen( arrivalTimes )
    return vehicles

def vehicleArrives(prevArrival):
    return prevArrival + random.expovariate( avgArrivalRate )

print simulateInterval()






### garbage
    # arrivalsPerTimestep = [0] * int(math.ceil(interval / timestep))    
    # for arrivalTime in arrivalTimes:
    #     arrivalsPerTimestep[int(math.floor(arrivalTime/timestep))]+=1
    # print 'total arrivals = ',sum(arrivalsPerTimestep)
    #return arrivalsPerTimestep