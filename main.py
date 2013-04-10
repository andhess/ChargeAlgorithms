import sys
import common
import fcfs
import fcfs_AC
import edf
import edf_AC_Basic
import edf_AC_Pro
import llfSimple
import llfSimple_AC_Basic
import llfSimple_AC_Pro
import llfSmart
import llfSmart_AC_Basic
import dsac
import poissonGen
import csvGen
import gc
import vehicle



if len( sys.argv ) != 2:
	print 'Wrong Number of Arguments you sent', sys.argv , " .. just interval" 
	sys.exit()  

interval = int( sys.argv[ 1 ] )
common.setInterval(interval)


# ------------------ real simulations -------------------------

# do tons and tons of simulations
arrivalRate = .2
numIterations = 100
maxArrivalRate = 2.0
numRunsPerIteration = 5
simulationData = []
for i in range( numIterations ):

	averageRates = [0] * 11    # a spot for every algo
	averageProfits = [0] * 11
	averageElapsedTimes = [0] * 11

	for k in range( numRunsPerIteration ):
		gc.collect()

		poissonGen.setArrivalRate( arrivalRate )

		simulationInterval = poissonGen.simulateInterval()

		# don't want a simulation with no cars
		while common.numberOfVehiclesInSimulation == 0:
			simulationInterval = poissonGen.simulateInterval()

		# common.vehicleIdsIn2DList( simulationInterval )

		#----------------fcfs----------------
		fcfsData = fcfsRate = fcfs.simulate( simulationInterval )

		fcfsACData = fcfs_AC.simulate( simulationInterval )

		#----------------edf----------------
		edfData = edf.simulate( simulationInterval )

		edfACBasicData = edf_AC_Basic.simulate( simulationInterval )

		edfACProData = edf_AC_Pro.simulate( simulationInterval )

		#----------------llfSimple----------------
		llfSimpleData = llfSimple.simulate( simulationInterval )

		llfSimpleACBasicData = llfSimple_AC_Basic.simulate( simulationInterval )

		llfSimpleACProData = llfSimple_AC_Pro.simulate( simulationInterval )

		#----------------llfSmart----------------
		llfSmartData = llfSimple.simulate( simulationInterval )

		llfSmartACBasicData = llfSmart_AC_Basic.simulate( simulationInterval )

		#----------------dsac----------------
		dsacData = dsac.simulate( simulationInterval )

		# common.vehicleIdsIn2DList( simulationInterval )

		runData = [fcfsData, fcfsACData, edfData , edfACBasicData, edfACProData, llfSimpleData, llfSimpleACBasicData, llfSimpleACProData, llfSmartData , llfSmartACBasicData, dsacData]

		runProfits = []
		runSuccessRates = []
		runElapsedTimes = []
		for algoData in runData:
			print algoData
			runProfits.append( algoData[0] )
			print algoData[0]
			runSuccessRates.append( algoData[1]/ algoData[4] )
			runElapsedTimes.append( algoData[5] )

		for index, rate in enumerate( runSuccessRates ):
			averageRates[index] += rate

		for index, profit in enumerate( runProfits ):
			averageProfits[index] += rate

		for index, time in enumerate( runElapsedTimes ):
			averageElapsedTimes[index] += time

	
	for n in range( len(averageRates) ):
		averageRates[n] /= ( numRunsPerIteration * 1.0 )

	simulationData.append( [arrivalRate] + averageProfits)
	arrivalRate += (maxArrivalRate / numIterations)

	if i % 10 != 0:
		print "iteration: " , i, " arrival rate: ", arrivalRate
		print "averageRates: ",averageRates
		print "averageProfits: ",averageProfits


csvGen.exportSimulationDataToCSV( simulationData )


