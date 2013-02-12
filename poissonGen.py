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

interval = int( sys.argv[ 1 ] )

# ----------- Globals & Constants -------------

# --- poissonStuff ---
avgArrivalRate = .5

# --- charging stuff ---
# chargeRateMu
# chargeRateSigma

# chargeNeeded - the charge needed at the end 
chargeNeededMu = 20 #kwh
chargeNeededSigma = 3 #kwh

currentChargeSigma = 3 #kwh
currentChargeMu = 12 #kwh

uniformMaxCapacity = 30 #kwh
uniformChargeRate = 50 #kw

# ---- storage lots ------

doneChargingLot = []
failedLot = []

# ---- queues ------

#fcfs
queue = Queue.Queue( 0 )

edfQueue = []
llfQueue = []

# ----- global time vars ------
currentTime = 0 

# --- random ----
numberOfVehiclesInSimulation = 0

# ---------- CSV Stuff ------------


# ------------ Poisson Generator ------------

# the main function for generating an interval on which to run an algorithmn
# will create a 2-level array, the top level being the length of the interval
# level 2 contains an array of the vehicle objects that will arrive during that minute
def simulateInterval():
    global numberOfVehiclesInSimulation
    arrivalTimes = []
    prevArrival = 0

    while True:
        nextArrival = math.floor( vehicleArrives( prevArrival ) )
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
    global currentTime
    global llfIndex

    # initialize a CSV document for storing all data
    generateVehicleCSV( "llf" )

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

    print "total number of cars: ", numberOfVehiclesInSimulation , \
          "  current time: " , currentTime , \
          "  done charging lot: " , len( doneChargingLot ) , \
          "  failed charing lot: " , len( failedLot ) , \
          "  llfQueue size:  " , len( llfQueue ) , \
          "  chargePort " , chargePorts
        

# called to update the vehicles for each minute of simulation
def updateVehiclesLLF():
    global currentTime
    global llfIndex
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
                    llfIndex = lowestLaxity()
                else:
                    chargePorts[ index ] = None
            
            

            # check if deadline reached
            if currentTime >= vehicle.depTime:
                exportVehicleToCSV( vehicle, "FAILURE" )
                failedLot.append( vehicle )
                
                if len( llfQueue ) > 0:
                    chargePorts[ index ] = llfQueue[ llfIndex ]
                    del llfQueue[ llfIndex ]
                    llfIndex = lowestLaxity()
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
def lowestLaxity():
    if len( llfQueue ) == 0:
        return -1
    return llfQueue.index( min( llfQueue, key = attrgetter( 'laxity' ) ) )

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

llfIndex = -1

def simulateLLFSimple( arrayOfVehicleArrivals ):
    global currentTime
    global llfIndex

    # initialize a CSV document for storing all data
    generateVehicleCSV( "llfSimple" )

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

    print "total number of cars: ", numberOfVehiclesInSimulation , \
          "  current time: " , currentTime , \
          "  done charging lot: " , len( doneChargingLot ) , \
          "  failed charing lot: " , len( failedLot ) , \
          "  llfQueue size:  " , len( llfQueue ) , \
          "  chargePort " , chargePorts
        

# called to update the vehicles for each minute of simulation
def updateVehiclesLLFSimple():
    global currentTime
    global llfIndex
    # increment the charge for the cars that were charging
    for index, vehicle in enumerate( chargePorts ):

        # add one minute of charge
        if vehicle is not None:
            vehicle.currentCharge += ( vehicle.chargeRate ) / 60

            # print "Charge:  " , vehicle.currentCharge , "   " , vehicle.chargeNeeded
            # print "Timing:  " , currentTime , "   ",  vehicle.depTime 

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
                    llfIndex = lowestLaxity()
                else:
                    chargePorts[ index ] = None
            
            

            # check if deadline reached
            if currentTime >= vehicle.depTime:
                exportVehicleToCSV( vehicle, "FAILURE" )
                failedLot.append( vehicle )
                
                if len( llfQueue ) > 0:
                    chargePorts[ index ] = llfQueue[ llfIndex ]
                    del llfQueue[ llfIndex ]
                    llfIndex = lowestLaxity() # function defined in LLF section, iterates through llfQueue for lowest laxity
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


#  ------ EDF ------

earliestDLIndex = -1;

# the main function for Earliest Deadline First Algorithm
# takes in an array of vehicle interval arrays
def simulateEDF( arrayOfVehicleArrivals ):
    global currentTime
    global earliestDLIndex

    # initialize a CSV document for storing all data
    generateVehicleCSV( "edf" )

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

    print "status:  " , openChargePort() , "  " , len(edfQueue) == 0

    # vehicles done arriving, now continue with the simulation
    while chargePortsEmpty() == False or not len( edfQueue ) == 0:
        updateVehiclesEDF()
        currentTime += 1

    print "status:  " , openChargePort() , \
          "  " , len( edfQueue ) == 0 , \
          " which evaluated to " , \
          not len( edfQueue ) == 0 or openChargePort() is None

    print "total number of cars: ", numberOfVehiclesInSimulation , \
          "  current time: " , currentTime , \
          "  done charging lot: " , len( doneChargingLot ) , \
          "  failed charing lot: " , len( failedLot ) , \
          "  edfQueue size:  " , len( edfQueue ) , \
          "  chargePort " , chargePorts

# called to update the vehicles for each minute of simulation
def updateVehiclesEDF():
    global earliestDLIndex

    # cheack each chargePort
    for index, vehicle in enumerate( chargePorts ):

        # add one minute of charge
        if vehicle is not None:
            vehicle.currentCharge += ( vehicle.chargeRate ) / 60

            print "Charge:  " , vehicle.currentCharge , "   " , vehicle.chargeNeeded
            
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
            
            print "Timing:  " , currentTime , "   ",  vehicle.depTime 

            # check if deadline reached
            if currentTime >= vehicle.depTime:
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
    global currentTime

    # initialize a CSV document for storing all data
    generateVehicleCSV( "fcfs" )

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

    print "status:  " , openChargePort() , "  " , queue.empty()
    
    # run the clock until all vehicles have ran through the simulation
    while chargePortsEmpty() == False or not queue.empty():
        updateVehiclesFCFS()
        currentTime += 1
    
    print "status:  " , openChargePort() , \
          "  " , queue.empty() , \
          " which evaluated to " , \
          not queue.empty() or openChargePort() is None

    print "total number of cars: ", numberOfVehiclesInSimulation , \
          "  current time: " , currentTime , \
          "  done charging lot: " , len( doneChargingLot ) , \
          "  failed charing lot: " , len( failedLot ) , \
          "  fcfsQueue size:  " , queue.qsize() , \
          "  chargePort " , chargePorts
            

# called to update the vehicles for each minute of simulation
def updateVehiclesFCFS():

    # check each chargePort
    for index, vehicle in enumerate( chargePorts ):        

        # add 1 minute of charge
        if vehicle is not None:
            vehicle.currentCharge += ( vehicle.chargeRate ) / 60

            print "Charge:  " , vehicle.currentCharge , "   " , vehicle.chargeNeeded

            # check if done charging
            if vehicle.currentCharge >= vehicle.chargeNeeded:
                exportVehicleToCSV( vehicle, "SUCCESS" )
                doneChargingLot.append( vehicle )
                if not queue.empty():
                    chargePorts[ index ] = queue.get()   #careful
                else:
                    chargePorts[ index ] = None

            print "Timing:  " , currentTime , "   " ,  vehicle.depTime 

            # check if deadline reached            
            if currentTime >= vehicle.depTime:
                exportVehicleToCSV( vehicle, "FAILURE" )
                failedLot.append( vehicle )
                if not queue.empty():
                    chargePorts[ index ] = queue.get()
                else:
                    chargePorts[ index ] = None

# --------- Exporting to CSV -----------

# every time an alrogithm is run, it will create a csv file of every vehicle in directory
# file will be save in /csv/<algorithm name>/timeStamp.csv
# NOTE: folderName must be a String of one of our algorihtm names: "fcfs" , "edf" , or "llf"
def generateVehicleCSV( folderName ):
    global path
    global newCSV

    # generate a unique filename with a time stamp
    timeStamp = datetime.datetime.now().strftime( "%Y%m%d-%H%M%S" )

    # thank stack overflow for making this easy
    # setup file to save in a directory
    script_dir = os.path.dirname( os.path.abspath(__file__) )
    dest_dir = os.path.join( script_dir, 'csv', folderName )    
    try:
        os.makedirs(dest_dir)

    except OSError:
        pass # already exists
    
    # relative file location
    path = os.path.join( dest_dir, timeStamp )
    
    # and now write it up
    newCSV = csv.writer( open( path , "wb" ) )

    # basic stats
    newCSV.writerow( [ "Interval time" , interval , "   Number of vehicles" , numberOfVehiclesInSimulation ] )

    # initialize some columns
    newCSV.writerow( [ "Vehicle ID" , \
                       "Status" , \
                       "Arrival Time" , \
                       "Departure Time" , \
                       "Initial Charge" , \
                       "Current Charge" , \
                       "Charge Rate" , \
                       "Charge Level Needed" , \
                       "Max Capacity" , \
                       "Charge Time Needed" \
                       "Original Free Time" , \
                       "Original Total Time" , \
                       "Original Laxity" \
                        ] )


# when a vehicle is leaving a lot, throw it into the CSV so we can study it
def exportVehicleToCSV( vehicle, status ):
    global path
    global newCSV

    newCSV.writerow( [ vehicle.id , \
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

#  -------- Simulations ------------

interval = simulateInterval()

# simulateFCFS( interval )

# simulateEDF( interval )

# simulateLLF( interval )

simulateLLFSimple( interval )


# -------- GARBAGE -----------

    # arrivalsPerTimestep = [0] * int(math.ceil(interval / timestep))    
    # for arrivalTime in arrivalTimes:
    #     arrivalsPerTimestep[int(math.floor(arrivalTime/timestep))]+=1
    # print 'total arrivals = ',sum(arrivalsPerTimestep)
    #return arrivalsPerTimestep