import csv
import os
import datetime
import common
import chargePorts


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
    vehiclePath = os.path.join( dest_dir, "vehicles.csv" )
    chargePortPath = os.path.join( dest_dir, "chargePorts.csv" )
    
    # and now write them up
    vehicleCSV = csv.writer( open( vehiclePath , "wb" ) )
    chargePortCSV = csv.writer( open( chargePortPath , "wb" ) )

    # write some basic info info in vehicleCSV

    # basic stats
    vehicleCSV.writerow( [ "Interval time" , common.interval , "Number of vehicles" , common.numberOfVehiclesInSimulation ] )

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
    chargePortCSV.writerow( [ "Interval time" , common.interval , "Number of charge ports" , chargePorts.numChargePorts ] )

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

    for index, vehicle in enumerate( chargePorts.chargePorts ):
        a = 0
        # chargePortCSV.writerow( [ index , \
        #                           vehicle \
        #                           ] )
