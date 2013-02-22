import Queue
import common
import csvGen
import chargePorts

#fcfs
queue = Queue.Queue( 0 )


# ------ FCFS ------

# the main implementation of the First Come First Serve algorithm
# takes in an array of arrays of vehicle minutes ( 2-level )
def simulateFCFS( arrayOfVehicleArrivals ):
    
    # reset global variables such as time, done/failed lots
    common.updateGlobals()
    global currentTime

    # initialize a CSV document for storing all data
    csvGen.generateCSV( "fcfs" )

    # iterate through each vehicle in each minute
    for minute, numVehiclesPerMin in enumerate( arrayOfVehicleArrivals ):
        for vehicle in numVehiclesPerMin:       
            port = chargePorts.openChargePort()

            # a port is open so start charging the vehicle
            if port is not None:
                chargePorts.chargePorts[ port ] = vehicle
                
            # no ports are available so put the vehicle in the queue
            else:
                queue.put( vehicle )

        updateVehiclesFCFS()
        common.currentTime += 1

    # print "status:  " , openChargePort() , "  " , queue.empty()
    
    # run the clock until all vehicles have ran through the simulation
    while chargePorts.chargePortsEmpty() == False or not queue.empty():
        updateVehiclesFCFS()
        common.currentTime += 1

    print "FCFS: total number of cars: ", common.numberOfVehiclesInSimulation , \
          "  elapsed time: " , common.currentTime , \
          "  done charging lot: " , len( common.doneChargingLot ) , \
          "  failed charging lot: " , len( common.failedLot ) , \
          "  fcfsQueue size:  " , queue.qsize() , \
          "  chargePort " , chargePorts.toString()
            

# called to update the vehicles for each minute of simulation
def updateVehiclesFCFS():

    # update chargePortCSV
    csvGen.exportChargePortsToCSV()

    # check each chargePort
    for index, vehicle in enumerate( chargePorts.chargePorts ):        

        # add 1 minute of charge
        if vehicle is not None:
            vehicle.currentCharge += ( vehicle.chargeRate ) / 60
            removed = False;

            # check if done charging
            if vehicle.currentCharge >= vehicle.chargeNeeded:
                csvGen.exportVehicleToCSV( vehicle, "SUCCESS" )
                common.doneChargingLot.append( vehicle )
                if not queue.empty():
                    chargePorts.chargePorts[ index ] = queue.get()   #careful
                else:
                    chargePorts.chargePorts[ index ] = None
                removed = True;


            # check if deadline reached            
            if common.currentTime >= vehicle.depTime and not removed:
                csvGen.exportVehicleToCSV( vehicle, "FAILURE" )
                common.failedLot.append( vehicle )
                if not queue.empty():
                    chargePorts.chargePorts[ index ] = queue.get()
                else:
                    chargePorts.chargePorts[ index ] = None
