import sys
import common
import fcfs
import edf
import llfSmart
import llfSimple
import dsac
import poissonGen
import csvGen


if len( sys.argv ) != 2:
	print 'Wrong Number of Arguments you sent', sys.argv , " .. just interval" 
	sys.exit()  

interval = int( sys.argv[ 1 ] )
common.setInterval(interval)


simulationData = []

arrivalRate = 1
poissonGen.setArrivalRate( arrivalRate )
simulationInterval = poissonGen.simulateInterval()
dsac.simulateDSAC( simulationInterval )



sys.exit(0)

# ------------------ real simulations -------------------------

# # do tons and tons of simulations
for i in range(0, 200):


	poissonGen.setArrivalRate( arrivalRate )

	simulationRound = []

	simulationRound.append( arrivalRate )

	simulationInterval = poissonGen.simulateInterval()

	# don't want a simulation with no cars
	while common.numberOfVehiclesInSimulation == 0:
		simulationInterval = poissonGen.simulateInterval()

	# print common.vehicleIdsIn2DList( simulationInterval )

	# simulationRound.append( fcfs.simulateFCFS( simulationInterval ) )
	# simulationRound.append( edf.simulateEDF( simulationInterval ) )
	# simulationRound.append( llfSmart.simulateLLF( simulationInterval ) )
	simulationRound.append( llfSimple.simulateLLFSimple( simulationInterval ) )
	#simulationRound.append( dsac.simulateDSAC( simulationInterval ) )
	# print simulationRound
	simulationData.append( simulationRound )
	arrivalRate += .025

	# poissonGen.testPoissonDistribution(1000)
	if i % 10 == 0:
		print "iteration: ",i


csvGen.exportSimulationDataToCSV( simulationData )


