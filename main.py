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
print "---------------- start of simulations -----------------------"

simulationInterval = poissonGen.simulateInterval()

# print common.vehicleIdsIn2DList( simulationInterval )

fcfs.simulateFCFS( simulationInterval )

# edf.simulateEDF( simulationInterval )

# llfSmart.simulateLLF( simulationInterval )

# llfSimple.simulateLLFSimple( simulationInterval )

# poissonGen.testPoissonDistribution(1000)

print "----------------- end of simulations ------------------------"