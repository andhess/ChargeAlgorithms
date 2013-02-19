import math
import random
import vehicle
import globals


from operator import attrgetter  # edf, llf, llfS


# ----------- Globals & Constants -------------

# --- poissonStuff ---
avgArrivalRate = 1 # cars per minute

# --- charging stuff ---
# chargeRateMu
# chargeRateSigma

# chargeNeeded - the charge needed at the end 
chargeNeededMu = 20 #kwh
chargeNeededSigma = 20 #kwh

currentChargeMu = 12 #kwh
currentChargeSigma = 6 #kwh

uniformMaxCapacity = 100 #kwh
uniformChargeRate = 59 #kw


# --- random ----
numberOfVehiclesInSimulation = 0

interval = 0

# ------------ Poisson Generator ------------

# the main function for generating an interval on which to run an algorithmn
# will create a 2-level array, the top level being the length of the interval
# level 2 contains an array of the vehicle objects that will arrive during that minute
def simulateInterval():
    global interval
    interval = globals.interval
    global numberOfVehiclesInSimulation
    
    numberOfVehiclesInSimulation = 0
    arrivalTimes = []
    prevArrival = 0

    while True:
        nextArrival = vehicleArrives( prevArrival ) # prev had math.floor here
        if nextArrival >= interval:
            break
        arrivalTimes.append( nextArrival )
        prevArrival = nextArrival

    arrivalsPerMin = [ 0 ] * interval

    for arrivalTime in arrivalTimes:
        arrivalsPerMin[ int( arrivalTime ) ] += 1
    
    # print "total number of vehicles:  " , len( arrivalTimes )

    numberOfVehiclesInSimulation = len( arrivalTimes )
    
    vehicles = vehicleGen( arrivalsPerMin )
    return vehicles

def vehicleArrives( prevArrival ):
    return prevArrival + random.expovariate( avgArrivalRate )

def vehicleGen( arrayOfArrivalsPerMin ):
    vehicles = []

    for minute, arrivalesDuringMin in enumerate( arrayOfArrivalsPerMin ):
        if arrivalesDuringMin != 0 :
            vehiclesDuringMin = []

            for i in range( 0, arrivalesDuringMin ):
                depart = minute + random.randint( 60 , 180 )
                chargeNeeded = random.gauss( chargeNeededMu, chargeNeededSigma )
                currentCharge = random.gauss( currentChargeMu, currentChargeSigma )
                chargeRate = uniformChargeRate
                maxCapacity = uniformMaxCapacity
                vehiclesDuringMin.append( vehicle.Vehicle( minute, depart, chargeNeeded, currentCharge, chargeRate, maxCapacity ) )
            
            vehicles.append( vehiclesDuringMin )

        else:
            vehicles.append( [] )

    return vehicles

# -------- Test simulateInterval() -------------
# we want to make sure that the poisson distribution is working correctly

def testPoissonDistribution( numberOfSimulations ):
    global numberOfVehiclesInSimulation
    numberOfVehiclesInSimulation = 0
    totalNumberOfVehicles = 0
    for i in range(numberOfSimulations):
        simulateInterval()
        # print numberOfVehiclesInSimulation
        totalNumberOfVehicles = totalNumberOfVehicles + numberOfVehiclesInSimulation
        numberOfVehiclesInSimulation = 0
    print numberOfSimulations, " simulations run with avgArrivalRate: ", avgArrivalRate, " interval: ", interval, \
          " total number of cars: ",totalNumberOfVehicles
    print "average number of cars per simulation: ", 1.0*totalNumberOfVehicles/numberOfSimulations

