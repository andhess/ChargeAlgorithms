Charging Algorithms
================

# About
This repository is part of a research project that I worked on for a semester with [@samwdon](https://github.com/samwdon) through the School of Engineering and Applied Sciences at Washington University in St. Louis.  The goal of the project was to test different scheduling and queueing algorithms to determine which is most effective in charging electric vehicles.  To test the algorithms, we built out this entire simulation and then compared their performance on a few different metrics.


# The Algorithms
We implemented 11 different algorithms.  These algorithms are built on 5 fundamentally different scheduling approaches.  They are defined as follows:
* FCFS - First Come First Serve - This is just a typical queue, as vehicles are kept in the order in which they arrive.
* EDF - Earliest Deadline First - This is a type of priorty queue.  It prioritizes vehicles based on their deadline.  A vehicle with a deadline approaching will skip up in priority.
* LLF-Simple - Least Laxity First - Laxity is defined as 1 - (time needed to charge / total time available for charging ).  In this version, laxity is calculated when a vehicle enters the simulation and the priority queues use only that initial value for all sorting.
* LLF-Smart - Here laxity is taken slightly differently.  Instead, it is defined as 1 - ( time left to charge / time until deadline ).  The difference between LLF-Smart is that the value of laxity is updated for all vehicles at the end of every discrete interval of simulation.
* DSAC - Decision Scheduling Admission Control - This algorithm was suggested in a [paper](http://acsp.ece.cornell.edu/papers/ChenJiTong12PES.pdf) by researchers at Cornell University.  It adds the ability to admit or decline a vehicle when it arrives.  It will admit a vehicle if it finds that it can increase its projected profit.

Initially, we built FCFS, EDF, and both of the LLF algorithms where they were required to admit all vehicles.  Since DSAC had the power of admission control, we also created a version of each that took advantage of admission control.  Furthermore, our initial 4 algorithms used 1 queue for all charging ports, whereas DSAC had a separate queue for each port.  To fairly compare DSAC, we implemented an additional admission control algorithm for FCFS, EDF, and LLF-Simple.  It didn't make much sense for LLF-Smart in both implementation or practicality.  These additions brought the total algorithm count to 11; they are as follows:
* FCFS (single queue)
* FCFS-AC (single queue)
* EDF-AC-Basic (single queue)
* EDF-AC-Pro (multiple queues)
* LLF-Simple (single queue)
* LLF-Simple-AC-Basic (single queue)
* LLF-Simple-AC-Pro (multiple queues)
* LLF-Smart (single queue)
* LLF-Smart-AC (single queue)
* DSAC (multiple queues)
The reason the multiple queue algorithms are referred to as pro is that they absolutely guarantee that no failure will ever occur when they admit a vehicle.  The basic ones will make a very accurate guess (about 99%, but not definite).