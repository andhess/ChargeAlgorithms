import common
import csvGen
import chargePorts
import chargeEvent
from operator import attrgetter

schedules =  [ [ ] for y in range( chargePorts.numChargePorts ) ]
edfQueue = []

#  ------ EDF ------

earliestDLIndex = -1;

# the main function for Earliest Deadline First Algorithm
# takes in an array of vehicle interval arrays
def simulateEDF( arrayOfVehicleArrivals ):

    # reset global variables such as time, done/failed lots
    common.updateGlobals( arrayOfVehicleArrivals )
    global currentTime
    global earliestDLIndex

    # initialize a CSV document for storing all data
    csvGen.generateCSV( "edf" )

    # iterate through each vehicle in each minute
    for minute, numVehiclesPerMin in enumerate( arrayOfVehicleArrivals ):
        for vehicle in numVehiclesPerMin:
            port = chargePorts.openChargePort()

            # check if it actually needs to be charged
            if vehicle.currentCharge > vehicle.chargeNeeded:
                csvGen.exportVehicleToCSV( vehicle, "Charge Not Needed" )
                common.cantChargeLot.append( vehicle )
                continue

            # a port is open so start charging the vehicle
            if port is not None:

                # add to chargePort
                chargePorts.chargePorts[ port ] = vehicle

                # initialize a listener object for its charging activity
                chargePorts.chargePortListeners[ port ].insert( 0 , chargeEvent.ChargeEvent( vehicle, common.currentTime ) )

            # no ports available so put in queue if it can fit
            else:
                if vehicleCanFitTest( vehicle ):
                    edfQueue.append( vehicle )
                    if earliestDLIndex == -1 or vehicle.depTime < edfQueue[ earliestDLIndex ].depTime:
                        earliestDLIndex = len( edfQueue ) - 1
                else:
                    csvGen.exportVehicleToCSV( vehicle, "DECLINED" )
                    common.declinedLot.append( vehicle )
        
        updateVehiclesEDF()
        common.currentTime += 1

    # vehicles done arriving, now continue with the simulation
    while chargePorts.chargePortsEmpty() == False or not len( edfQueue ) == 0:
        updateVehiclesEDF()
        common.currentTime += 1

    # print "EDF: total number of cars: ", common.numberOfVehiclesInSimulation , \
    #       "  elapsed time: " , common.currentTime , \
    #       "  done charging lot: " , len( common.doneChargingLot ) , \
    #       "  failed charging lot: " , len( common.failedLot ) , \
    #       "  declined lot: ", len( common.declinedLot ), \
    #       "  cant charge lot: " , len( common.cantChargeLot ) , \
    #       "  edfQueue size:  " , len( edfQueue ) , \
    #       "  chargePort " , chargePorts.toString()

    # write a CSV with all the chargePort logs
    csvGen.exportChargePortsToCSV( "edf" )

    return ( 1.0 * len( common.doneChargingLot ) / common.numberOfVehiclesInSimulation )


# called to update the vehicles for each minute of simulation
def updateVehiclesEDF():
    global earliestDLIndex
    global latestChargePortDLIndex

    # cheack each chargePort
    for index, vehicle in enumerate( chargePorts.chargePorts ):

        # add one minute of charge
        if vehicle is not None:
            vehicle.currentCharge += ( vehicle.chargeRate ) / 60.0
            removed = False

            #check if done charging
            if vehicle.currentCharge >= vehicle.chargeNeeded:

                # finish up the listener for this vehicle
                chargePorts.chargePortListeners[ index ][ 0 ].terminateCharge( vehicle , common.currentTime )

                # remove finished vehicle from grid and document it
                csvGen.exportVehicleToCSV( vehicle, "SUCCESS" )
                common.doneChargingLot.append( vehicle )
                
                if len( edfQueue ) > 0:

                    # get next vehicle and throw in chargePort
                    nextVehicle = edfQueue[ earliestDLIndex ]
                    chargePorts.chargePorts[ index ] = nextVehicle

                    # make it a listener
                    chargePorts.chargePortListeners[ index ].insert( 0 , chargeEvent.ChargeEvent( nextVehicle , common.currentTime ) )

                    # update queue
                    del edfQueue[ earliestDLIndex ]  
                    earliestDLIndex = earliestDL()

                else:
                    chargePorts.chargePorts[ index ] = None
                removed = True

            # check if deadline reached
            if common.currentTime >= vehicle.depTime and not removed:

                # this vehicle is on the out, so wrap up its listener
                chargePorts.chargePortListeners[ index ][ 0 ].terminateCharge( vehicle , common.currentTime )

                # remove finished vehicle and document it
                csvGen.exportVehicleToCSV( vehicle, "FAILURE" )
                common.failedLot.append( vehicle )
                
                if len( edfQueue ) > 0:

                    # get nextVehicle
                    nextVehicle = edfQueue[ earliestDLIndex ]
                    chargePorts.chargePorts[ index ] = nextVehicle

                    # make new listener
                    chargePorts.chargePortListeners[ index ].insert( 0 , chargeEvent.ChargeEvent( nextVehicle , common.currentTime ) )

                    # update queue
                    del edfQueue[ earliestDLIndex ]
                    earliestDLIndex = earliestDL()

                else:
                    chargePorts.chargePorts[ index ] = None


    # now we want to make sure that all the cars in the chargePorts are the best choices
    # we want to know the index of the worst car charging and compare that to the index of the best in the queue
    # also need to be able to cycle the queue so that it will put ALL the cars in the queue that are better into the chargePorts

    # edge cases to worry about: queue is empty, earliestDLIndex = -1

    # start out by grabbing the latest chargePort
    latestChargePortDLIndex = latestChargePortDL()

    # prioritize edge cases, loop until swap the top DL are all in the queue
    while len( edfQueue ) > 0 and latestChargePortDLIndex != -1 and edfQueue[ earliestDLIndex ].depTime < chargePorts.chargePorts[ latestChargePortDLIndex ].depTime:

        swappingOut = chargePorts.chargePorts[ latestChargePortDLIndex ]
        swappingIn  = edfQueue[ earliestDLIndex ]

        # close the listener for swappingOut
        chargePorts.chargePortListeners[ latestChargePortDLIndex ][ 0 ].terminateCharge( swappingOut , common.currentTime )

        # swap occurs in the chargePorts
        chargePorts.chargePorts[ latestChargePortDLIndex ] = swappingIn

        # create a new listener for the vehicle that just got swapped in
        chargePorts.chargePortListeners[ latestChargePortDLIndex ].insert( 0 , chargeEvent.ChargeEvent( swappingIn , common.currentTime ) )

        # swap finishes in the queue
        edfQueue[ earliestDLIndex ] = swappingOut

        # now update values for comparison
        earliestDLIndex = earliestDL()
        latestChargePortDLIndex = latestChargePortDL()

        # NOTE: we are explicitly choosing to grab a clean version of each index because accuracy cannot be guaranteed


# gets the index of earliest deadline of all the vehicles in edfQueue
def earliestDL():
    if len( edfQueue ) == 0:
        return -1
    return edfQueue.index( min( edfQueue, key = attrgetter( 'depTime' ) ) )

# gets the index of the vehicle in chargePorts with the latest deadline 
def latestChargePortDL():
    latestIndex = -1
    latestTime = -1
    for index, port in enumerate( chargePorts.chargePorts ):
        if port is not None:
            if port.depTime > latestTime:
                latestTime = port.depTime
                latestIndex = index
    return latestIndex  

# Add up all charging time left for vehicles in chargePorts and for vehicles in queue with an earlier deadline
# then divide by number of chargeports to get average time per charge port
def vehicleCanFitTest( vehicle ):
    totalTime = 0
    for curChargingVehicle in chargePorts.chargePorts:
        if curChargingVehicle is not None:
            totalTime += curChargingVehicle.timeLeftToCharge()
        else:
            raise Exception("Schedule should never be empty here, something is wrong")
    for scheduledVehicle in edfQueue:
        totalTime += scheduledVehicle.timeToCharge

    averageEndTime = (totalTime * 1.0) / chargePorts.numChargePorts
    averageEndTime += common.currentTime

    # returns true if it can fit, false if it cannot
    return averageEndTime < (vehicle.depTime - vehicle.timeToCharge)


# takes in an index to specify which schedule in schedules, and returns an array with predicted 
def genAdmissionFeasiblity( index ):
    
    endTimes = []
    endingTime = common.currentTime

    # iterate through the schedule, for each car, add end time to array
    for i, vehicle in enumerate( schedules[ index ] ):

        # update endingTime for the next vehicle, add it to endTimes
        endingTime += vehicle.timeToCharge
        endTimes.append( endingTime )

    # now have an array of scheduled endTimes for each vehicle
    # index matches with index of vehicle in sorted schedule
    return endTimes


# properly inserts a vehicle into a schedule, returns its index
# maintains a properly sorted schedule, based on deadlines 
def insertIntoSchedule( vehicle, scheduleIndex ):

    reference = -1
    depTime   = vehicle.depTime

    print "schedule length:   : " ,  len( schedules[ scheduleIndex ] )

    if len( schedules[ scheduleIndex ] ) > 0:

        # iterate until it fits, insert, and then break from loop
        for index, car in enumerate( schedules[ scheduleIndex ] ):
            if depTime < car.depTime:
                print "inserted  into " , index
                reference = index
                schedules[ scheduleIndex ].insert( index , vehicle )
                break

            # add it to the end
            else:
                print "adding to end of schedule"
                reference = len( schedules[ scheduleIndex ] )
                schedules[ scheduleIndex ].append( vehicle )
                break

    else:
        "inserting in empty schedule"

        schedules[ scheduleIndex ].insert( 0 , vehicle )
        reference = 0

    # for now, a QA check
    print "----------"
    print scheduleToString( scheduleIndex )
    prev = schedules[ scheduleIndex ][ 0 ]

    if len( schedules[ scheduleIndex ] ) > 1:
        for i in range( 1 , len( schedules[ scheduleIndex ] ) ):
            print "depTimes:  " , prev.depTime ,  "  <   " , schedules[ scheduleIndex ][ i ].depTime
            # the prev car should always have a depTime <= to current
            if prev.depTime > schedules[ scheduleIndex ][ i ].depTime:
                return "insert not working, schedules out of order"
            
            # update prev
            prev = schedules[ scheduleIndex ][ i ]

    print "reference:   "  , reference , " ------- "

    return reference


# takes in an index and a list of scheduled end times for vehicles
# returns False if it can't fit, the "flexibility" if it can
# a lower flexibility indicates a tighter fit
def admissionFeasibility( scheduleIndex , feasibilityArray ):

    # first make sure our comparison arrays match up
    if len( schedules[ scheduleIndex ] ) != len( feasibilityArray ):
        return "comparison arrays aren't same length"

    flexibility = float( "inf" );

    # iterate through arrays, comparing depTimes with predicted end charging times
    for index, vehicle in enumerate( schedules[ scheduleIndex ] ):
        tempFlex = vehicle.depTime - feasibilityArray[ index ]

        # can it finish before depTime?
        if tempFlex < 0:
            return False

        if tempFlex < flexibility:
            flexibility = tempFlex

    return flexibility


# returns True if there more vehicles in the schedules
def schedulesEmpty():
    return all( len( subSchedule ) == 0 for subSchedule in schedules )

# simulates EDF with the queues for each chargePort
def simulateEDFPro( arrayOfVehicleArrivals ):

    #global schedules

    # reset global variables such as time, done/failed lots
    common.updateGlobals( arrayOfVehicleArrivals )
    global currentTime
    # global earliestDLIndex

    # initialize a CSV document for storing all data
    csvGen.generateCSV( "edfPro" )

    # iterate through each vehicle in each minute
    for minute, numVehiclesPerMin in enumerate( arrayOfVehicleArrivals ):
        for vehicle in numVehiclesPerMin:
            port = chargePorts.openChargePort()

            # check if it actually needs to be charged
            if vehicle.currentCharge > vehicle.chargeNeeded:
                csvGen.exportVehicleToCSV( vehicle, "Charge Not Needed" )
                common.cantChargeLot.append( vehicle )
                continue

            # a port is open so start charging the vehicle
            if port is not None:

                # add to chargePort and schedule
                chargePorts.chargePorts[ port ] = vehicle
                schedules[ port ].insert( 0 , vehicle )

                if len( schedules[ port ] ) > 1:
                    print "empty chargePort, but shit was scheduled to be there"
                    break

                # initialize a listener object for its charging activity
                chargePorts.chargePortListeners[ port ].insert( 0 , chargeEvent.ChargeEvent( vehicle, common.currentTime ) )

            # no ports available so try to put it in a queue, but have to find one that will work
            else:

                bestSchedule = -1
                scheduleFlex = float( "inf" );
                
                # iterate through every schedule
                for index, schedule in enumerate( schedules ):

                    # insert a vehicle in the schedule and get its admission feasibility
                    insertLocation =  insertIntoSchedule( vehicle , index )
                    print type( insertLocation ) , " dicks dicks dicks dicks"
                    insertLocation = int( insertLocation )
                    print type( insertLocation ) , " penis penis penis"
                    admissionTest  =  genAdmissionFeasiblity( index )

                    print "++++++------+++++___+++_+_+_+_+_++_"
                    print type( insertLocation )


                    print "insertLocation:  " , insertLocation

                    # will it work?
                    tempFlex = admissionFeasibility( index , admissionTest )

                    # check if it can work for this sched
                    print "tempFlex:  " , tempFlex
                    if tempFlex == False:

                        # if it can't work, delete from schedule and move on
                        del schedules[ index ][ insertLocation ]
                        continue

                    # now check if it's the best one
                    if tempFlex < scheduleFlex:
                        scheduleFlex = tempFlex
                        bestSchedule = index

                    # regardless, delete from schedule for now
                    del schedules[ index ][ insertLocation ]

                # now will we do an official insert? or decline
                if bestSchedule >= 0 or tempFlex < 0:
                    print "bestSchedule index: " , bestSchedule
                    insertIntoSchedule( vehicle , bestSchedule )

                # decline
                else:
                    csvGen.exportVehicleToCSV( vehicle, "DECLINED" )
                    common.declinedLot.append( vehicle )

        updateVehiclesEDFPro()
        common.currentTime += 1

    # vehicles done arriving, now continue with the simulation
    while chargePorts.chargePortsEmpty() == False or not schedulesEmpty():
        updateVehiclesEDFPro()
        common.currentTime += 1

    print "EDFPro: total number of cars: ", common.numberOfVehiclesInSimulation , \
          "  elapsed time: " , common.currentTime , \
          "  done charging lot: " , len( common.doneChargingLot ) , \
          "  failed charging lot: " , len( common.failedLot ) , \
          "  declined lot: ", len( common.declinedLot ), \
          "  cant charge lot: " , len( common.cantChargeLot ) , \
          "  schedules:  " , len( edfQueue ) , \
          "  chargePort " , chargePorts.toString()

    # write a CSV with all the chargePort logs
    csvGen.exportChargePortsToCSV( "edfPro" )

    return ( 1.0 * len( common.doneChargingLot ) / common.numberOfVehiclesInSimulation )

# update vehicles for the pro edf algorithm
def updateVehiclesEDFPro():
    #global schedules

    # cheack each chargePort
    for index, vehicle in enumerate( chargePorts.chargePorts ):

        # add one minute of charge
        if vehicle is not None:
            vehicle.currentCharge += ( vehicle.chargeRate ) / 60.0
            removed = False

            #check if done charging
            if vehicle.currentCharge >= vehicle.chargeNeeded:

                # finish up the listener for this vehicle
                chargePorts.chargePortListeners[ index ][ 0 ].terminateCharge( vehicle , common.currentTime )

                # remove finished vehicle from grid and document it
                csvGen.exportVehicleToCSV( vehicle, "SUCCESS" )
                common.doneChargingLot.append( vehicle )

                print "vehicle done charging....  index:  " ,  index
                print schedules

                del schedules[ index ][ 0 ] # remove the vehicle from the schedule
                
                # the next vehicle
                if len( schedules[ index ] ) > 0:

                    # get next vehicle and throw in chargePort
                    nextVehicle = schedules[ index ][ 0 ]
                    chargePorts.chargePorts[ index ] = nextVehicle

                    # make it a listener
                    chargePorts.chargePortListeners[ index ].insert( 0 , chargeEvent.ChargeEvent( nextVehicle , common.currentTime ) )

                else:
                    chargePorts.chargePorts[ index ] = None
                removed = True


            # check if deadline reached
            # shouldn't run into this with adminControl, but practice safe algorithms
            if common.currentTime >= vehicle.depTime and not removed:

                # this vehicle is on the out, so wrap up its listener
                chargePorts.chargePortListeners[ index ][ 0 ].terminateCharge( vehicle , common.currentTime )

                # remove finished vehicle and document it
                csvGen.exportVehicleToCSV( vehicle, "FAILURE" )
                common.failedLot.append( vehicle )
                del schedules[ index ][ 0 ] # remove the vehicle for the schedule
                
                if len( schedules[ index ] ) > 0:

                    # get nextVehicle
                    nextVehicle = schedules[ index ][ 0 ]
                    chargePorts.chargePorts[ index ] = nextVehicle

                    # make new listener
                    chargePorts.chargePortListeners[ index ].insert( 0 , chargeEvent.ChargeEvent( nextVehicle , common.currentTime ) )

                else:
                    chargePorts.chargePorts[ index ] = None


    # there are cases when a new car arrived with the earliestDL, but all swaps are done at discrete intervals
    # in this case, it is currently at index 0, but not being charged. This part will change that

    # look through each schedule
    for index, schedule in enumerate( schedules ):

        # compare schedule[ 0 ].depTime with that in the chargePort. swap out if different
        if len( schedule ) > 0:
            if schedule[ 0 ].depTime < chargePorts.chargePorts[ index ].depTime:

                print "swap swap baby"

                # close the listener for swappingOut
                chargePorts.chargePortListeners[ index ][ 0 ].terminateCharge( chargePorts.chargePorts[ index ] , common.currentTime )

                # swap occurs in the chargePorts
                chargePorts.chargePorts[ index ] = schedules[ index ][ 0 ]

                # create a new listener for the vehicle that just got swapped in
                chargePorts.chargePortListeners[ index ].insert( 0 , chargeEvent.ChargeEvent( schedules[ index ][ 0 ] , common.currentTime ) )


def scheduleToString( index ):
    statement = "[ "
    for position, vehicle in enumerate( schedules[ index ] ):
        statement += vehicle.toStringID()
        statement += " , "
    return statement + " ] "
    


