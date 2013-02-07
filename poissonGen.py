import sys
import math
import random
import Queue
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
chargeNeededMu = 45 #kwh
chargeNeededSigma = 5 #kwh

currentChargeSigma = 3 #kwh
currentChargeMu = 12 #kwh

uniformMaxCapacity = 60 #kwh
uniformChargeRate = 30 #kw

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

# ------------ Poisson Generator ------------

# the main function for generating an interval on which to run an algorithmn
# will create a 2-level array, the top level being the length of the interval
# level 2 contains an array of the vehicle objects that will arrive during that minute
def simulateInterval():
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
    
    print "total number of vehicles:  " , len( arrivalTimes )
    
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

def simulateLLF( arrayOfVehicleArrivals ):
    global currentTime
    global llfIndex

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

    print "status:  " , openChargePort() , "  " , len(edfQueue) == 0

    # vehicles done arriving, now continue with the simulation
    while chargePortsEmpty() == False or not len( edfQueue ) == 0:
        updateVehiclesEDF()
        currentTime += 1

    print ( "status:  " , openChargePort() ,
            "  " , len( edfQueue ) == 0 ,
            " which evaluated to " , 
            not len( edfQueue ) == 0 or openChargePort() is None
            )

    print ( "current time: " , currentTime , 
            "  done charging lot: " , len( doneChargingLot ) ,
            "  failed charing lot: " , len( failedLot ) ,
            "  edfQueue size:  " , len( edfQueue ) ,
            "  chargePort " , chargePorts
            )
        

# called to update the vehicles for each minute of simulation
def updateVehiclesLLF():
    global llfIndex
    # increment the charge for the cars that were charging
    for index, vehicle in enumerate( chargePorts ):

        # add one minute of charge
        if vehicle is not None:
            vehicle.currentCharge += ( vehicle.chargeRate ) / 60

            print "Charge:  " , vehicle.currentCharge , "   " , vehicle.chargeNeeded
    
    # update the laxity for all the peeps
    updateLaxityForAll()

    # now move cars around so the laxity property is maintained
    for index, vehicle in enumerate( chargePorts ):
        if vehicle is not None:

            #check if done charging
            if vehicle.currentCharge >= vehicle.chargeNeeded:
                doneChargingLot.append( vehicle )
                
                if len( llfQueue ) > 0:
                    chargePorts[ index ] = llfQueue[ llfIndex ]
                    del llfQueue[ llfIndex ]  
                    llfIndex = lowestLaxity()
                else:
                    chargePorts[ index ] = None
            
            print "Timing:  " , currentTime , "   ",  vehicle.depTime 

            # check if deadline reached
            if currentTime >= vehicle.depTime:
                failedLot.append( vehicle )
                
                if len( llfQueue ) > 0:
                    chargePorts[ index ] = llfQueue[ llfIndex ]
                    del llfQueue[ llfIndex ] 
                    llfIndex = lowestLaxity()
                else:
                    chargePorts[ index ] = None

            # check if all cars in chargePorts still have lowest laxity
            if lffIndex != -1 and vehicle.laxity > llfQueue[ llfIndex ].laxity:

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

#FIXME : ran into issue here. the queue seems to have null spaces. fuck.
    # now do the llfQueue
    for index, vehicle in enumerate( chargePorts ):
        if vehicle is not None:
            vehicle.updateLaxity( currentTime )


#  ------ EDF ------
earliestDLIndex = -1;

# the main function for Earliest Deadline First Algorithm
# takes in an array of vehicle interval arrays
def simulateEDF( arrayOfVehicleArrivals ):
    global currentTime
    global earliestDLIndex

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

    print ( "status:  " , openChargePort() ,
            "  " , len( edfQueue ) == 0 ,
            " which evaluated to " , 
            not len( edfQueue ) == 0 or openChargePort() is None
            )

    print ( "current time: " , currentTime , 
            "  done charging lot: " , len( doneChargingLot ) ,
            "  failed charing lot: " , len( failedLot ) ,
            "  edfQueue size:  " , len( edfQueue ) ,
            "  chargePort " , chargePorts
        )

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
    
    print ( "status:  " , openChargePort() ,
            "  " , queue.empty() ,
            " which evaluated to " ,
            not queue.empty() or openChargePort() is None
            )

    print ( "current time: " , currentTime ,
            "  done charging lot: " , len( doneChargingLot ) ,
            "  failed charing lot: " , len( failedLot ) ,
            "  queue size:  " , queue.qsize() ,
            " chargePort " , chargePorts
            )

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
                doneChargingLot.append( vehicle )
                if not queue.empty():
                    chargePorts[ index ] = queue.get()   #careful
                else:
                    chargePorts[ index ] = None

            print "Timing:  " , currentTime , "   " ,  vehicle.depTime 

            # check if deadline reached            
            if currentTime >= vehicle.depTime:
                failedLot.append( vehicle )
                if not queue.empty():
                    chargePorts[ index ] = queue.get()
                else:
                    chargePorts[ index ] = None


#  -------- Simulations ------------

# print simulateInterval()

#simulateFCFS( simulateInterval() )

simulateEDF( simulateInterval() )

#simulateLLF( simulateInterval() )


# -------- GARBAGE -----------

    # arrivalsPerTimestep = [0] * int(math.ceil(interval / timestep))    
    # for arrivalTime in arrivalTimes:
    #     arrivalsPerTimestep[int(math.floor(arrivalTime/timestep))]+=1
    # print 'total arrivals = ',sum(arrivalsPerTimestep)
    #return arrivalsPerTimestep