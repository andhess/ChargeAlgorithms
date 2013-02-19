import sys
import fcfs
import edf
import llfSmart
import llfSimple
import poissonGen
import chargePorts
import csv


if len( sys.argv ) != 2:
    print 'Wrong Number of Arguments you sent', sys.argv , " .. just interval" 
    sys.exit()  

interval = int( sys.argv[ 1 ] )


#  -------- Simulations ------------

simulationInterval = poissonGen.simulateInterval( interval )

print "number of vehicles in this simulation: ", poissonGen.numberOfVehiclesInSimulation

fcfs.simulateFCFS( simulationInterval )

# simulateEDF( simulationInterval )

# simulateLLF( simulationInterval )

# simulateLLFSimple( simulationInterval )

# testPoissonDistribution(1000)

print "----------------- end of simulations ------------------------"