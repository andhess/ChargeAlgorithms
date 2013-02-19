import Queue
import globals
import csvGen

#fcfs
queue = Queue.Queue( 0 )


# ------ FCFS ------

# the main implementation of the First Come First Serve algorithm
# takes in an array of arrays of vehicle minutes ( 2-level )
def simulateFCFS( arrayOfVehicleArrivals ):
    
    # reset global variables such as time, done/failed lots
    globals.updateGlobals()
    global currentTime

    # initialize a CSV document for storing all data
    csvGen.generateCSV( "fcfs" )

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
                csvGen.exportVehicleToCSV( vehicle, "SUCCESS" )
                doneChargingLot.append( vehicle )
                if not queue.empty():
                    chargePorts[ index ] = queue.get()   #careful
                else:
                    chargePorts[ index ] = None
                removed = True;


            # check if deadline reached            
            if currentTime >= vehicle.depTime and not removed:
                csvGen.exportVehicleToCSV( vehicle, "FAILURE" )
                failedLot.append( vehicle )
                if not queue.empty():
                    chargePorts[ index ] = queue.get()
                else:
                    chargePorts[ index ] = None
