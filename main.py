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

arrivalRate = .75
poissonGen.setArrivalRate( arrivalRate )
simulationInterval = poissonGen.simulateInterval()

print fcfs.simulateFCFS( simulationInterval )


#dsac.simulateDSAC( simulationInterval )



sys.exit( 0 )

# ------------------ real simulations -------------------------

# # do tons and tons of simulations
for i in range( 0, 10 ):

	simulationRound = []
	poissonGen.setArrivalRate( arrivalRate )
	simulationRound.append( arrivalRate )

	simulationInterval = poissonGen.simulateInterval()

	# don't want a simulation with no cars
	while common.numberOfVehiclesInSimulation == 0:
		simulationInterval = poissonGen.simulateInterval()

	# print common.vehicleIdsIn2DList( simulationInterval )

	#fcfs
	simulationRound.append( fcfs.simulateFCFS( simulationInterval ) )
	simulationRound.append( fcfs.simulateFCFSAdmin( simulationInterval ) )

	#edf
	# simulationRound.append( edf.simulateEDF( simulationInterval ) )
	# simulationRound.append( edf.simulateEDFAdmin( simulationInterval ) )

	#llfSmart
	# simulationRound.append( llfSmart.simulateLLF( simulationInterval ) )
	# simulationRound.append( llfSmart.simulateLLFAdmin( simulationInterval ) )

	#llfSimple
	# simulationRound.append( llfSimple.simulateLLFSimple( simulationInterval ) )
	# simulationRound.append( llfSimple.simulateLLFSimpleAdmin( simulationInterval ) )

	#dsac
	# simulationRound.append( dsac.simulateDSAC( simulationInterval ) )
	
	# print simulationRound
	
	simulationData.append( simulationRound )
	arrivalRate += .25

	# poissonGen.testPoissonDistribution(1000)
	if i % 10 == 0:
		print "iteration: " , i


csvGen.exportSimulationDataToCSV( simulationData )


