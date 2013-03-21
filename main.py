import sys
import common
import fcfs
import edf
import llfSmart
import llfSimple
import poissonGen
import csvGen


if len( sys.argv ) != 2:
    print 'Wrong Number of Arguments you sent', sys.argv , " .. just interval" 
    sys.exit()  

interval = int( sys.argv[ 1 ] )
common.setInterval(interval)


simulationData = []

arrivalRate = .1

# do tons and tons of simulations
for i in range(0, 10):

	poissonGen.setArrivalRate( arrivalRate )

	simulationRound = []

	simulationRound.append( arrivalRate )

	#  -------- Simulations ------------
	#print "---------------- start of simulations -----------------------"

	simulationInterval = poissonGen.simulateInterval()

	# print common.vehicleIdsIn2DList( simulationInterval )

	simulationRound.append( fcfs.simulateFCFS( simulationInterval ) )

	simulationRound.append( edf.simulateEDF( simulationInterval ) )

	simulationRound.append( llfSmart.simulateLLF( simulationInterval ) )

	simulationRound.append( llfSimple.simulateLLFSimple( simulationInterval ) )

	#simulationRound.append( dsac.simulateDSAC( simulationInterval ) )

	# print "----------------- end of simulations ------------------------"

	simulationData.append( simulationRound )
	arrivalRate += .2

	# poissonGen.testPoissonDistribution(1000)


csvGen.exportSimulationDataToCSV( simulationData )

