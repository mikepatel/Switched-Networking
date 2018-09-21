# James Cross, Michael Patel
# ECE 577
# Lab Hw1
# Question 6

# Input:
#	- IP address
#	- number of hosts

# Output:
#	- first available subnet address

# Notes:

############################################################
import numpy as np
import sys


############################################################
def next_power_of_2(x):
    x = np.ceil(np.log2(int(x)))  # return number of bits
    # print(x)
    # x = np.power(2, x)
    return int(x)


############################################################
if __name__ == "__main__":
    args = sys.argv
    # print(args)
    ip_addr = args[1]
    num_hosts = args[2]
    # print(ip_addr)
    # print(num_hosts)
    t = next_power_of_2(num_hosts)
    mask = 32 - t
    print(ip_addr + "/" + str(mask))
