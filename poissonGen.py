import sys
import math
import random
import Queue
import csv
import os
import datetime
from vehicle import *
from chargePorts import *
from operator import attrgetter

if len( sys.argv ) != 2:
    print 'Wrong Number of Arguments you sent', sys.argv
    print 'interval'
    sys.exit()
#print 'parameters: ',sys.argv   
print "------------------------------------------" 

interval = int( sys.argv[ 1 ] )

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

# ---- storage lots ------

doneChargingLot = []
failedLot = []

# ---- queues ------

#fcfs
queue = Queue.Queue( 0 )

edfQueue = []
llfQueue = []
llfSimpleQueue = []

# ----- global time vars ------
currentTime = 0 

# --- random ----
numberOfVehiclesInSimulation = 0

# function to reset time, failed/done lots etc. Called at start of every algorithm simlulation
def updateGlobals():
    global currentTime
    currentTime = 0
    global doneChargingLot
    doneChargingLot = []
    global failedLot
    failedLot = []
    resetChargePorts()

#visualization of vehicle ids in chargeporst
def printChargePorts():
    output = "["
    for index, vehicle in enumerate(chargePorts):
        if vehicle is None:
            output += "None"
        else:
            output += str(vehicle.id)
        if index != len(chargePorts)-1:
            output += ", "
    output += "]"
    print output


# ------------ Poisson Generator ------------

# the main function for generating an interval on which to run an algorithmn
# will create a 2-level array, the top level being the length of the interval
# level 2 contains an array of the vehicle objects that will arrive during that minute
def simulateInterval():
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
                vehiclesDuringMin.append( Vehicle( minute, depart, chargeNeeded, currentCharge, chargeRate, maxCapacity ) )
            
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

#  ------------- The Algorithms -------------


#  ------ LLF ------

# laxity is defined as freeTime/totalTime where freeTime = (departure - arrival - chargeTime) and totalTime = (departure - arrival) initially )
# laxity needs to be updated each minute where freeTime = ( departure - current time - chargeTime ) and totalTime = ( departure - currentTime )
# 
# for both cases, caluclate totalTime, then free time will just be totalTime - chargeTime.
#
# this is going to work pretty much the same way as EDF, only difference is we need to constantly update the laxity values of each vehicle
# however we are still hanging on to the same index deal as before
#
#    total time =   departure time - current time
#    free time  =  total time - timeToCharge
# 
#   ok, when does laxity need to be updated for each vehicle?
#

llfIndex = -1

def simulateLLF( arrayOfVehicleArrivals ):
    
    # reset global variables such as time, done/failed lots
    updateGlobals()
    global currentTime
    global llfIndex
    llfIndex =  -1

    # initialize a CSV document for storing all data
    generateCSV( "llfSmart" )

    # iterate through each vehicle in each minute
    for minute, numVehiclesPerMin in enumerate( arrayOfVehicleArrivals ):
        for vehicle in numVehiclesPerMin:
            port = openChargePort()

            # there is an open chargePort, add vehicle to it
            if port is not None:
                chargePorts[ port ] = vehicle

            # no open chargePort, append to llfQueue
            else:
                llfQueue.append( vehicle )

                # update the llfIndex if this vehicle is better
                if llfIndex == -1 or vehicle.laxity < llfQueue[ llfIndex ].laxity:
                    llfIndex = len( llfQueue ) - 1

        updateVehiclesLLF()
        currentTime += 1

    # vehicles done arriving, now continue with the simulation
    while chargePortsEmpty() == False or not len( llfQueue ) == 0:
        updateVehiclesLLF()
        currentTime += 1

    print "LLF Complex:  total number of cars: ", numberOfVehiclesInSimulation , \
          "  current time: " , currentTime , \
          "  done charging lot: " , len( doneChargingLot ) , \
          "  failed charing lot: " , len( failedLot ) , \
          "  llfQueue size:  " , len( llfQueue ) , \
          "  chargePort " , chargePorts
        

# called to update the vehicles for each minute of simulation
def updateVehiclesLLF():
    global currentTime
    global llfIndex

    # update chargePortCSV
    exportChargePortsToCSV()

    # increment the charge for the cars that were charging
    for index, vehicle in enumerate( chargePorts ):

        # add one minute of charge
        if vehicle is not None:
            vehicle.currentCharge += ( vehicle.chargeRate ) / 60

            # print "Charge:  " , vehicle.currentCharge , "   " , vehicle.chargeNeeded
            # print "Timing:  " , currentTime , "   ",  vehicle.depTime 
    
    # update the laxity for all the peeps
    updateLaxityForAll()

    # now move cars around so the laxity property is maintained
    for index, vehicle in enumerate( chargePorts ):
        if vehicle is not None:

            #check if done charging
            if vehicle.currentCharge >= vehicle.chargeNeeded:
                exportVehicleToCSV( vehicle, "SUCCESS" )
                doneChargingLot.append( vehicle )
                
                if len( llfQueue ) > 0:
                    chargePorts[ index ] = llfQueue[ llfIndex ]
                    del llfQueue[ llfIndex ]  
                    llfIndex = lowestLaxity("complex")
                else:
                    chargePorts[ index ] = None
            
            

            # check if deadline reached
            if currentTime >= vehicle.depTime:
                exportVehicleToCSV( vehicle, "FAILURE" )
                failedLot.append( vehicle )
                
                if len( llfQueue ) > 0:
                    chargePorts[ index ] = llfQueue[ llfIndex ]
                    del llfQueue[ llfIndex ]
                    llfIndex = lowestLaxity("complex")
                else:
                    chargePorts[ index ] = None

            # print "the laxity index is   :    "  ,  llfIndex  , "    the queue size is   :   "  , len( llfQueue )

            # check if all cars in chargePorts still have lowest laxity
            if llfIndex != -1 and vehicle.laxity > llfQueue[ llfIndex ].laxity:

                # swap vehicle of llfIndex with the current vehicle in the loop
                temp = vehicle
                chargePorts[ index ] = llfQueue[ llfIndex ]
                llfQueue[ llfIndex ] = temp

                # llfIndex is unchanged and still correctly points to the next lowest laxity

# gets index for the vehicle with the lowest laxity from llf
def lowestLaxity(type):
    if type == "complex":
        if len( llfQueue ) == 0:
            return -1
        return llfQueue.index( min( llfQueue, key = attrgetter( 'laxity' ) ) )
    if type == "simple":
        if len( llfSimpleQueue ) == 0:
            return -1
        return llfSimpleQueue.index( min( llfSimpleQueue, key = attrgetter( 'laxity' ) ) )

# laxity constantly changes as time advances and certain cars are charged
def updateLaxityForAll():

    # first do chargePorts
    for index, vehicle in enumerate( chargePorts ):
        if vehicle is not None:
            vehicle.updateLaxity( currentTime )

    # now do the llfQueue
    for index, vehicle in enumerate( llfQueue ):
        vehicle.updateLaxity( currentTime )


#  ------ LLF SIMPLE --------
# This algorithm runs under the same premise as the other LLF algorithm except in this instance laxity is only computed once
# upon arrival
# laxity is still defined as freeTime/totalTime where freeTime = (departure - arrival - chargeTime) and totalTime = (departure - arrival) 
# However, since laxity is only calculated once, if a car has a small laxity there is a good chance that it will never be charged 

llfSimpleIndex = -1

def simulateLLFSimple( arrayOfVehicleArrivals ):
    
    # reset global variables such as time, done/failed lots
    updateGlobals()
    global currentTime
    global llfSimpleIndex

    # initialize a CSV document for storing all data
    generateCSV( "llfSimple" )

    # iterate through each vehicle in each minute
    for minute, numVehiclesPerMin in enumerate( arrayOfVehicleArrivals ):
        for vehicle in numVehiclesPerMin:
            port = openChargePort()

            # there is an open chargePort, add vehicle to it
            if port is not None:
                chargePorts[ port ] = vehicle

            # no open chargePort, append to llfQueue
            else:

                llfSimpleQueue.append( vehicle )

                # update the llfIndex if this vehicle is better
                if llfSimpleIndex == -1 or vehicle.laxity < llfSimpleQueue[ llfSimpleIndex ].laxity:
                    llfSimpleIndex = len( llfQueue ) - 1

        updateVehiclesLLFSimple()
        currentTime += 1

    # vehicles done arriving, now continue with the simulation
    while chargePortsEmpty() == False or len( llfSimpleQueue ) != 0:
        updateVehiclesLLFSimple()
        currentTime += 1

    print "LLF Simple: total number of cars: ", numberOfVehiclesInSimulation , \
          "  current time: " , currentTime , \
          "  done charging lot: " , len( doneChargingLot ) , \
          "  failed charing lot: " , len( failedLot ) , \
          "  llfQueue size:  " , len( llfQueue ) , \
          "  chargePort " , chargePorts
        

# called to update the vehicles for each minute of simulation
def updateVehiclesLLFSimple():
    global currentTime
    global llfSimpleIndex
    print "--------------------"
    print "llfSimpleIndex: ",llfSimpleIndex

    # update chargePortCSV
    exportChargePortsToCSV()

    # increment the charge for the cars that were charging
    for index, vehicle in enumerate( chargePorts ):

        # add one minute of charge
        if vehicle is not None:
            vehicle.currentCharge += ( vehicle.chargeRate ) / 60

    # now move cars around so the laxity property is maintained
    for index, vehicle in enumerate( chargePorts ):
        if vehicle is not None:
            removed = False

            #check if done charging
            if vehicle.currentCharge >= vehicle.chargeNeeded:
                print "vehicle charged", vehicle.id
                exportVehicleToCSV( vehicle, "SUCCESS" )
                doneChargingLot.append( vehicle )
                
                if len( llfSimpleQueue ) > 0:
                    chargePorts[ index ] = llfSimpleQueue[ llfSimpleIndex ]
                    del llfSimpleQueue[ llfSimpleIndex ]  
                    llfSimpleIndex = lowestLaxity("simple")
                else:
                    chargePorts[ index ] = None
                removed = True
            
            

            # check if deadline reached
            if currentTime >= vehicle.depTime and not removed:
                print "vehicle's departure time reached", vehicle.id
                exportVehicleToCSV( vehicle, "FAILURE" )
                failedLot.append( vehicle )
        
                if len( llfSimpleQueue ) > 0:
                    chargePorts[ index ] = llfSimpleQueue[ llfSimpleIndex ]
                    del llfSimpleQueue[ llfSimpleIndex ]
                    llfSimpleIndex = lowestLaxity("simple") # function defined in LLF section, iterates through llfQueue for lowest laxity
                else:
                    chargePorts[ index ] = None

            # print "the laxity index is   :    "  ,  llfSimpleIndex  , "    the queue size is   :   "  , len( llfQueue )

            # check if all cars in chargePorts still have lowest laxity
            if llfSimpleIndex != -1 and vehicle.laxity > llfSimpleQueue[ llfSimpleIndex ].laxity:

                # swap vehicle of llfSimpleIndex with the current vehicle in the loop
                temp = vehicle
                chargePorts[ index ] = llfSimpleQueue[ llfSimpleIndex ]
                llfSimpleQueue[ llfSimpleIndex ] = temp

                # llfIndex is unchanged and still correctly points to the next lowest laxity


#  ------ EDF ------

earliestDLIndex = -1;

# the main function for Earliest Deadline First Algorithm
# takes in an array of vehicle interval arrays
def simulateEDF( arrayOfVehicleArrivals ):
    
    # reset global variables such as time, done/failed lots
    updateGlobals()
    global currentTime
    global earliestDLIndex

    # initialize a CSV document for storing all data
    generateCSV( "edf" )

    # iterate through each vehicle in each minute
    for minute, numVehiclesPerMin in enumerate( arrayOfVehicleArrivals ):
        for vehicle in numVehiclesPerMin:
            port = openChargePort()

            if port is not None:
                chargePorts[ port ] = vehicle
            else:
                edfQueue.append( vehicle )
                if earliestDLIndex == -1 or vehicle.depTime < edfQueue[ earliestDLIndex ].depTime:
                    earliestDLIndex = len( edfQueue ) - 1

        updateVehiclesEDF()
        currentTime += 1

    # vehicles done arriving, now continue with the simulation
    while chargePortsEmpty() == False or not len( edfQueue ) == 0:
        updateVehiclesEDF()
        currentTime += 1

    print "EDF: total number of cars: ", numberOfVehiclesInSimulation , \
          "  current time: " , currentTime , \
          "  done charging lot: " , len( doneChargingLot ) , \
          "  failed charing lot: " , len( failedLot ) , \
          "  edfQueue size:  " , len( edfQueue ) , \
          "  chargePort " , chargePorts

# called to update the vehicles for each minute of simulation
def updateVehiclesEDF():
    global earliestDLIndex

    # update chargePortCSV
    exportChargePortsToCSV()

    # cheack each chargePort
    for index, vehicle in enumerate( chargePorts ):

        # add one minute of charge
        if vehicle is not None:
            vehicle.currentCharge += ( vehicle.chargeRate ) / 60
            removed = False

            #check if done charging
            if vehicle.currentCharge >= vehicle.chargeNeeded:
                exportVehicleToCSV( vehicle, "SUCCESS" )
                doneChargingLot.append( vehicle )
                
                if len( edfQueue ) > 0:
                    chargePorts[ index ] = edfQueue[ earliestDLIndex ]
                    del edfQueue[ earliestDLIndex ]  
                    earliestDLIndex = earliestDL()
                else:
                    chargePorts[ index ] = None
                removed = True

            # check if deadline reached
            if currentTime >= vehicle.depTime and not removed:
                exportVehicleToCSV( vehicle, "FAILURE" )
                failedLot.append( vehicle )
                
                if len( edfQueue ) > 0:
                    chargePorts[ index ] = edfQueue[ earliestDLIndex ]
                    del edfQueue[ earliestDLIndex ] 
                    earliestDLIndex = earliestDL()
                else:
                    chargePorts[ index ] = None

            # check if all cars in chargePorts still have best deadlines
            if earliestDLIndex != -1 and vehicle.depTime > edfQueue[ earliestDLIndex ].depTime:

                # swap index of earliestDLIndex with the current vehicle in the loop
                temp = vehicle
                chargePorts[ index ] = edfQueue[ earliestDLIndex ]
                edfQueue[ earliestDLIndex ] = temp

                # earliestDLIndex is unchanged and still correct

# gets the earliest deadline of all the vehicles in edfQueue
def earliestDL():
    if len( edfQueue ) == 0:
        return -1
    return edfQueue.index( min( edfQueue, key = attrgetter( 'depTime' ) ) )


# ------ FCFS ------

# the main implementation of the First Come First Serve algorithm
# takes in an array of arrays of vehicle minutes ( 2-level )
def simulateFCFS( arrayOfVehicleArrivals ):
    
    # reset global variables such as time, done/failed lots
    updateGlobals()
    global currentTime

    # initialize a CSV document for storing all data
    generateCSV( "fcfs" )

    # iterate through each vehicle in each minute
    for minute, numVehiclesPerMin in enumerate( arrayOfVehicleArrivals ):
        for vehicle in numVehiclesPerMin:       
            port = openChargePort()

            if port is not None:
                chargePorts[ port ] = vehicle
            else:
                queue.put( vehicle )

        updateVehiclesFCFS()
        currentTime += 1

    # print "status:  " , openChargePort() , "  " , queue.empty()
    
    # run the clock until all vehicles have ran through the simulation
    while chargePortsEmpty() == False or not queue.empty():
        updateVehiclesFCFS()
        currentTime += 1

    print "FCFS: total number of cars: ", numberOfVehiclesInSimulation , \
          "  current time: " , currentTime , \
          "  done charging lot: " , len( doneChargingLot ) , \
          "  failed charing lot: " , len( failedLot ) , \
          "  fcfsQueue size:  " , queue.qsize() , \
          "  chargePort " , chargePorts
            

# called to update the vehicles for each minute of simulation
def updateVehiclesFCFS():

    # update chargePortCSV
    exportChargePortsToCSV()

    # check each chargePort
    for index, vehicle in enumerate( chargePorts ):        

        # add 1 minute of charge
        if vehicle is not None:
            vehicle.currentCharge += ( vehicle.chargeRate ) / 60
            removed = False;

            # check if done charging
            if vehicle.currentCharge >= vehicle.chargeNeeded:
                exportVehicleToCSV( vehicle, "SUCCESS" )
                doneChargingLot.append( vehicle )
                if not queue.empty():
                    chargePorts[ index ] = queue.get()   #careful
                else:
                    chargePorts[ index ] = None
                removed = True;


            # check if deadline reached            
            if currentTime >= vehicle.depTime and not removed:
                exportVehicleToCSV( vehicle, "FAILURE" )
                failedLot.append( vehicle )
                if not queue.empty():
                    chargePorts[ index ] = queue.get()
                else:
                    chargePorts[ index ] = None



# --------- Optimal Offline Solution -----------
# need to figure out what algorithm is optimal
# have to take into account that start times and departures times are not all the same

# --------- Exporting to CSV -----------

# every time an alrogithm is run, it will create csv files for vehicles and chargePorts
# files will be save in /csv/<algorithm type>/timeStamp/
# NOTE: folderName must be a String of one of our algorihtm names: "fcfs" , "edf" , or "llfSmart" , "llfSimple"
def generateCSV( folderName ):
    global vehiclePath
    global chargePortPath
    global vehicleCSV
    global chargePortCSV

    # generate a unique filename with a time stamp
    timeStamp = datetime.datetime.now().strftime( "%Y%m%d-%H%M%S" )

    # thank stack overflow for making this easy
    # setup file to save in a directory
    script_dir = os.path.dirname( os.path.abspath(__file__) )
    dest_dir = os.path.join( script_dir, 'csv', folderName , timeStamp )    
    try:
        os.makedirs(dest_dir)

    except OSError:
        pass # already exists
    
    # make a CSV for both Vehicle and ChargePorts
    vehiclePath = os.path.join( dest_dir, "vehicles" )
    chargePortPath = os.path.join( dest_dir, "chargePorts" )
    
    # and now write them up
    vehicleCSV = csv.writer( open( vehiclePath , "wb" ) )
    chargePortCSV = csv.writer( open( chargePortPath , "wb" ) )

    # write some basic info info in vehicleCSV

    # basic stats
    vehicleCSV.writerow( [ "Interval time" , interval , "Number of vehicles" , numberOfVehiclesInSimulation ] )

    # initialize some columns
    vehicleCSV.writerow( [ "Vehicle ID" , \
                       "Status" , \
                       "Arrival Time" , \
                       "Departure Time" , \
                       "Initial Charge" , \
                       "Current Charge" , \
                       "Charge Rate" , \
                       "Charge Level Needed" , \
                       "Max Capacity" , \
                       "Charge Time Needed" , \
                       "Original Free Time" , \
                       "Original Total Time" , \
                       "Original Laxity" \
                        ] )

    # write some basic info in chargePortCSV

    # basic stats
    chargePortCSV.writerow( [ "Interval time" , interval , "Number of charge ports" , numChargePorts ] )

    # initialize some columns for stuff
    chargePortCSV.writerow( [ "ChargePort Number" , \
                              "Vehicle ID" \
                            ])


# when a vehicle is leaving a lot, throw it into the CSV so we can study it
def exportVehicleToCSV( vehicle, status ):
    global vehiclePath
    global vehicleCSV

    vehicleCSV.writerow( [ vehicle.id , \
                       status , \
                       vehicle.arrivalTime , \
                       vehicle.depTime , \
                       vehicle.initialCharge , \
                       vehicle.currentCharge , \
                       vehicle.chargeRate , \
                       vehicle.chargeNeeded , \
                       vehicle.maxCapacity , \
                       vehicle.timeToCharge , \
                       vehicle.freeTime , \
                       vehicle.totalTime , \
                       vehicle.originalLaxity \
                       ] )


def exportChargePortsToCSV():

    for index, vehicle in enumerate( chargePorts ):
        a = 0
        # chargePortCSV.writerow( [ index , \
        #                           vehicle \
        #                           ] )



#  -------- Simulations ------------

simulationInterval = simulateInterval()
print "number of vehicles in this simulation: ", numberOfVehiclesInSimulation

simulateFCFS( simulationInterval )

# simulateEDF( simulationInterval )

# simulateLLF( simulationInterval )

# simulateLLFSimple( simulationInterval )

# testPoissonDistribution(1000)

print "----------------- end of simulations ------------------------"

# -------- GARBAGE -----------

    # arrivalsPerTimestep = [0] * int(math.ceil(interval / timestep))    
    # for arrivalTime in arrivalTimes:
    #     arrivalsPerTimestep[int(math.floor(arrivalTime/timestep))]+=1
    # print 'total arrivals = ',sum(arrivalsPerTimestep)
    #return arrivalsPerTimestep