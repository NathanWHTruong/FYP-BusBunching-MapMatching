# Program: SUMOmain
# Goal: Permits the user to connect to the Monash SUMOPaint simulation and subsequently paint the vehicle of interest any desired colour.
# Author: Wynita Griggs
# Date: 14th October, 2019
# Tested and works with SUMO 1.2.0.

import os, sys
import traci
import sumolib
import multiprocessing
from multiprocessing import Process, Value
import socket
import time
from pprint import pprint


# server program:  creates the server, handles incoming calls and subsequent user requests
def server(data,latx,longy,bear):
	# size of buffer and backlog
	buffer = 2048 # value should be a relatively small power of 2, e.g. 4096
	backlog = 1 # tells the operating system to keep a backlog of 1 connection; this means that you can have at most 1 client waiting while the server is handling the current client; the operating system will typically allow a maximum of 5 waiting connections; to cope with this, busy servers need to generate a new thread to handle each incoming connection so that it can quickly serve the queue of waiting clients

	# create a socket
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET = IPv4 socket family; SOCK_STREAM = TCP socket type

	# bind the socket to an address and port
	host = '127.0.0.1' # localhost
	port = 8080 # reserve a port for the service (i.e. a large number less than 2^16); the call will fail if some other application is already using this port number on the same machine
	#host = '192.168.43.206' #
	#port = 50000
	server_socket.bind((host, port)) # binds the socket to the hostname and port number
	


	# listen for incoming connections
	server_socket.listen(backlog)

	while True: # infinite loop 1
		client_socket, address = server_socket.accept() # passively accept TCP client connections; the call returns a pair of arguments: client is a new Socket object used to communicate with the client and address is the address of the client
	
		# record client connection time (as seen from the server)
		start_time = time.strftime('%d %b %Y at %H:%M:%S')
		init_time = str(start_time) # convert connection time to a string
		print 'Made a connection with', address, 'on', init_time + '.'
		
		while True: # infinite loop 2
			incoming = client_socket.recv(buffer) # receive client data into buffer
			if (incoming == 'red'):
				data.value = 0.1
			elif (incoming == 'quit'):
				data.value = 0.7
				print 'Client is bored of tracking cars.  Ending session with client.'
				# client_socket.send('Quit message received.  Goodbye.')
				client_socket.close() # close the connection with the client
				break # breaks out of infinite loop 2
			else:
				latx.value = float(incoming.split()[0])
				longy.value = float(incoming.split()[1])
				bear.value = float(incoming.split()[2])

# main program
if __name__ == '__main__':

	net = sumolib.net.readNet('foresthill.net.xml')
	radius = 0.1

	# constants
	endSim = 1800000 # the simulation will be permitted to run for a total of endSim milliseconds; 1800000 milliseconds = 30 minutes
	timeout = 1 # a floating point number specified in seconds

	# initialisations
	step = 0 # time step
	d = Value('d', 0.0) # 'd' is a string containing a type code as used by the array module (where 'd' is a floating point number implemented in double in C) and 0.0 is an initial value for 'd'
	lat = Value('d',0.0)
	long = Value('d',0.0)
	bearing = Value('d',0.0)
	
	print
	print '==========================='
	print 'Beginning the main program.'
	print '==========================='
	print	
	print "Connecting to SUMO via TraCI."
	print
	
	# import TraCI (to use the library, the <SUMO_HOME>/tools directory must be on the python load path)
	if 'SUMO_HOME' in os.environ:
		tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
		sys.path.append(tools)
	else:	
		sys.exit("Please declare environment variable 'SUMO_HOME'.")
		
	# compose the command line to start SUMO-GUI
	sumoBinary = "/Program Files (x86)/Eclipse/Sumo/bin/sumo-gui"
	sumoCmd = [sumoBinary, "-S", "-c", "SUMOmain.sumo.cfg"]
	
	# start the simulation and connect to it with the python script
	traci.start(sumoCmd)
	
	thread = Process(target=server, args=(d,lat,long,bearing)) # represents a task (i.e. the server program) running in a subprocess
	print "Launching the server."
	thread.start()
	print "The server has been launched."
	xnetlist = []
	ynetlist = []
	bearlist = []
	with open('xlistfile.txt','r') as filehandle:
		for line in filehandle:
			currentPlace = line[:-1] #get all but /n
			xnetlist.append(float(currentPlace))
	with open('ylistfile.txt','r') as filehandle:
		for line in filehandle:
			currentPlace = line[:-1] #get all but /n
			ynetlist.append(float(currentPlace))
	with open('bearlistfile.txt','r') as filehandle:
		for line in filehandle:
			currentPlace = line[:-1] #get all but /n
			bearlist.append(float(currentPlace))
	i = 0


	while step < endSim:
		thread.join(timeout) # implicitly controls the speed of the simulation; blocks the main program either until the server program terminates (if no timeout is defined) or until the timeout occurs
		
		print 'Time step [s]: {}'.format(step/1000)
		print 'Current value of d: {}'.format(d.value)
		
		if (step/1000 > 5):
			bear = bearlist[i]
			xnet = xnetlist[i]
			ynet = ynetlist[i]
			i = i + 1
			edges = net.getNeighboringEdges(xnet,ynet,radius)
			while len(edges) == 0:
				radius += 0.1
				edges = net.getNeighboringEdges(xnet,ynet,radius)
			radius = 0.1
			#pick closest edges
			if len(edges) > 0:
				distancesAndEdges = sorted([(dist, edge) for edge, dist in edges])
				dist, closestEdge = distancesAndEdges[0]
										
			traci.vehicle.moveToXY("veh0", edgeID= closestEdge._id, lane = -1, x = xnet, y = ynet, angle = bear, keepRoute = 2)
		
	#	print lat.value, long.value, bearing.value
		# go to the next time step
		step += 1000 # in milliseconds
		traci.simulationStep()
	
	print "Shutting the server down."
	thread.terminate()	
	print "Closing the main program. Goodbye."
	traci.close() # close the connection to SUMO