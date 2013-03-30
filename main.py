import sys
import common
import fcfs
import edf
import llfSmartAC
import llfSmart
import llfSimpleAC
import llfSimple
import dsac
import poissonGen
import csvGen
import gc



if len( sys.argv ) != 2:
	print 'Wrong Number of Arguments you sent', sys.argv , " .. just interval" 
	sys.exit()  

interval = int( sys.argv[ 1 ] )
common.setInterval(interval)


simulationData = []

arrivalRate = .1
poissonGen.setArrivalRate( arrivalRate )


simulationInterval = poissonGen.simulateInterval()

# print llfSmartAC.simulateLLF( simulationInterval )
# print llfSmart.simulateLLF( simulationInterval )

print edf.simulateEDFPro( simulationInterval )

# #dsac.simulateDSAC( simulationInterval )

sys.exit()

# ------------------ real simulations -------------------------

# # do tons and tons of simulations
numIterations = 100
maxArrivalRate = 2.0
numRunsPerIteration = 5
for i in range( numIterations ):
	# gc.collect()

	averageRates = [0] * 7    # a spot for every algo

	for k in range( numRunsPerIteration ):
		gc.collect()

		individualRates = []
		poissonGen.setArrivalRate( arrivalRate )

		simulationInterval = poissonGen.simulateInterval()

		# don't want a simulation with no cars
		while common.numberOfVehiclesInSimulation == 0:
			simulationInterval = poissonGen.simulateInterval()


		#fcfs
		fcfsRate = fcfs.simulateFCFS( simulationInterval )
		individualRates.append( fcfsRate )

		#edf
		edfRate = edf.simulateEDF( simulationInterval ) 
		individualRates.append( edfRate )

		#llfSmart
		llfSmartRate = llfSmart.simulateLLF( simulationInterval )
		individualRates.append( llfSmartRate )
		llfSmartACRate = llfSmartAC.simulateLLF( simulationInterval )
		individualRates.append( llfSmartACRate )

		#llfSimple
		llfSimpleRate = llfSimple.simulateLLFSimple( simulationInterval )
		individualRates.append( llfSimpleRate )
		llfSimpleACRate = llfSimpleAC.simulateLLFSimpleAC( simulationInterval )
		individualRates.append( llfSimpleACRate )

		#dsac
		dsacRate = dsac.simulateDSAC( simulationInterval )
		individualRates.append( dsacRate )

		for index, rate in enumerate(individualRates):
			averageRates[index] += rate
	
	for n in range( len(averageRates) ):
		averageRates[n] /= ( numRunsPerIteration * 1.0 )

	simulationData.append( [arrivalRate] + averageRates)
	arrivalRate += (maxArrivalRate / numIterations)

	if i % 10 == 0:
		print "iteration: " , i, " arrival rate: ", arrivalRate
		print averageRates

csvGen.exportSimulationDataToCSV( simulationData )


