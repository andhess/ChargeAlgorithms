import sys
import common
import fcfs
import edf
import llfSmart
import llfSimple
import poissonGen


if len( sys.argv ) != 2:
    print 'Wrong Number of Arguments you sent', sys.argv , " .. just interval" 
    sys.exit()  

interval = int( sys.argv[ 1 ] )
common.setInterval(interval)


#  -------- Simulations ------------

simulationInterval = poissonGen.simulateInterval()

print "number of vehicles in this simulation: ", common.numberOfVehiclesInSimulation

fcfs.simulateFCFS( simulationInterval )

# simulateEDF( simulationInterval )

# simulateLLF( simulationInterval )

# simulateLLFSimple( simulationInterval )

# testPoissonDistribution(1000)

print "----------------- end of simulations ------------------------"