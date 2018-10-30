# blockchain-simulator

This program seeks to analyze the performance of the Bitcoin blockchain process with varying block sizes. The simulation model is an M/M/1 queue with bulk-service times. I evaluate the difference in arrivals' residence time for block sizes between 1 MB and 8 MB with 0.5 MB increments. The purpose of this simulation is to determine if block size has a significant effect on the time that arrivals remain in the queue. For this project, I use the following parameters:

#N = 500000
This number represents the number of arrivals in the system for each block size.

#s = 600
Service rate is set at 600 seconds (or 10 minutes), which represents the rate that blocks are generated in the system based on Nakamoto's original Bitcoin proposal. 

#average_transaction_size: 0.00025 
The average transaction size is 250 bytes.
