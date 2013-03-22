import sys
import common
import fcfs
import edf
import llfSmart
import llfSimple
#import dsac
import poissonGen
import csvGen


if len( sys.argv ) != 2:
    print 'Wrong Number of Arguments you sent', sys.argv , " .. just interval" 
    sys.exit()  

interval = int( sys.argv[ 1 ] )
common.setInterval(interval)


# simulationData = []

# arrivalRate = .02

# # do tons and tons of simulations
# for i in range(0, 10000):

# 	poissonGen.setArrivalRate( arrivalRate )

# 	simulationRound = []

# 	simulationRound.append( arrivalRate )

# 	simulationInterval = poissonGen.simulateInterval()

# 	# print common.vehicleIdsIn2DList( simulationInterval )

# 	simulationRound.append( fcfs.simulateFCFS( simulationInterval ) )
# 	simulationRound.append( edf.simulateEDF( simulationInterval ) )
# 	simulationRound.append( llfSmart.simulateLLF( simulationInterval ) )
# 	simulationRound.append( llfSimple.simulateLLFSimple( simulationInterval ) )
# 	#simulationRound.append( dsac.simulateDSAC( simulationInterval ) )

# 	simulationData.append( simulationRound )
# 	arrivalRate += .001

# 	# poissonGen.testPoissonDistribution(1000)

# csvGen.exportSimulationDataToCSV( simulationData )


simulationInterval = poissonGen.simulateInterval()
fcfs.simulateFCFS( simulationInterval )
