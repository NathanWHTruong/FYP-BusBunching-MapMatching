import os, sys
import traci
import random
import numpy as np
import random
import csv
if __name__ == '__main__':
	random.seed(3)

	simCounter = 1

	print '==========================='
	print 'Beginning the main program.'
	print '==========================='
	print	
	print "Connecting to SUMO via TraCI."
	print
	print

	if 'SUMO_HOME' in os.environ:
		tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
		sys.path.append(tools)
		print('SUMO_HOME in load path')
	else:   
		sys.exit("Please declare environment variable 'SUMO_HOME'.")

	# compose the command line to start SUMO-GUI
	#    sumoBinary = "G:/uni/FYP/sumo/bin/sumo-gui"
	sumoBinary = "/Program Files (x86)/Eclipse/Sumo/bin/sumo-gui"

	# sumoCmd = [sumoBinary, "-S", "-c", "exampleTest.sumocfg"]
	sumoCmd = [sumoBinary, "-c", "bus.sumocfg"]

	#pre process edges uses for bus stops
	file_object  = open("stopdata.txt", "r")
	edges =[]
	busEdges = []
	major = [] 
	minor = []
	for line in file_object:
		line = line[1:len(line)-3]
		edges.append(line.split(" "))
	for x in edges:		
		x[2] = x[2][6:len(x[2])-1]
		if x[0] == "instantInductionLoop":
			tmp = x[2]
			major.append(tmp[0:len(tmp)-2])
		else:
			tmp = x[2]
			busEdges.append(tmp[0:len(tmp)-2])
	for x in edges:
		tmp = x[2]
		if x[0] == "busStop" and tmp[0:len(tmp)-2] not in major:
			minor.append(tmp[0:len(tmp)-2])
			
	def personRouteGenerator(edges,minor,major,stops,mobFlag):
		if mobFlag == False:
			stopnum = 100
			#choose starting bus stop thats not the end
			while stopnum >= 60: #few stops before end
				val = random.random()	
				if val < 0.4: 
					startEdge = minor[random.randint(0,len(minor)-1)]
				else: 
					startEdge = major[random.randint(0,len(major)-1)]
				busIndex = edges.index(startEdge)
				stopID=stops[busIndex]
				stopnum = int(stopID.split("_")[1])
		else:
			stopnum = 0
			stopID = "busStop_0"
			startEdge = "-101161164#17"
		#choose end bus stop that is greater than initial 
		#depending on stop num 
		val2 = random.random()
		if val2 < 0.4: #choose within 5-15 stops %40
			stopnum2 = random.randint(min(stopnum+5,62),min(stopnum+15,62))
		elif val2 < 0.7 and val2 >= 0.4: #choose within 15-25 stops 30%
			stopnum2 = random.randint(min(stopnum+15,62),min(stopnum+25,62))
		elif val2 >= 0.7 and val2 < 0.85: #choose within 25-35 stops 15%
			stopnum2 = random.randint(min(stopnum+25,62),min(stopnum+35,62))
		elif val2 >= 0.85 and val2 < 0.95:
			stopnum2 = random.randint(min(stopnum+35,62),min(stopnum+50,62))
		else:
			stopnum2 = random.randint(min(stopnum+1,62),min(stopnum+5,62))
		stopID2 = "busStop_" + str(stopnum2)
		idx = stops.index(stopID2)
		endEdge = edges[idx]
		#print(stopID,stopID2,startEdge,endEdge)
		return stopID, stopID2, startEdge, endEdge 
		
	def revivePerson(deletedPeople,edges,minor,major,stops):
		for i in range(len(deletedPeople)):
			#resurection time
			reviveDetails = deletedPeople.pop(0) #1,0 is edge, 0 is id
		#	print(reviveDetails[0] + ' is back!')

			reviveEdge = reviveDetails[1][0]
			stopIndex = edges.index(reviveEdge)
			stopID1 = busStops[stopIndex]
			reviveDestEdge = reviveDetails[2]
			stopIndex2 = edges.index(reviveDestEdge)
			stopID2 = busStops[stopIndex2]
		#	print(stopID2)
			traci.person.add(reviveDetails[0],reviveEdge,0)
			traci.person.appendWalkingStage(reviveDetails[0],reviveEdge,1,duration=1,speed=5,stopID = stopID1)
			traci.person.appendDrivingStage(reviveDetails[0],reviveDestEdge,"902",stopID=stopID2)
			return
			
	def updateBusPosAndCap(busList,busCapacity,busCurrentStop,busEdges):
		for i in range(len(busList)):
			try:
				busCapacity[i] = traci.vehicle.getPersonNumber(busList[i])
				currBusEdge = traci.vehicle.getRoadID(busList[i])
				if currBusEdge != "": #means bus is on the road
				#busRouteEdges = traci.vehicle.getRoute(busList[i])
				#busRouteIndex = traci.vehicle.getRouteIndex(busList[i])
				#update which stop bus has last past		
					if currBusEdge in busEdges:
						index = busEdges.index(currBusEdge)
						busCurrentStop[i] = busStops[index].split("_")[1]
			except:
				#print('bus done')
				#print(str(busList[i]) +'bus no longer exists')
				pass
			
		return 
	def updateOnBoardStatus(busCapacity,onBoardStopsAmount,busList):
		for i in range(len(busList)):
			try:
				if busCapacity[i] > 0:
					peopleOnBus = traci.vehicle.getPersonIDList(busList[i])
					for j in range(len(peopleOnBus)):
						thisGuyGetsOffAt = traci.person.getStage(peopleOnBus[j],nextStageIndex=0).destStop
						
						#ERROR CHECK 
						if thisGuyGetsOffAt != "": #maybe he just spawned and is still waiting, but sumo will still consider him on board >:( give the man time to board!!
							stopvar = int(thisGuyGetsOffAt.split("_")[1])
						#	print(str(peopleList[j]) + "is getting off at" + str(stopvar) + "using bus" +str(i))
							onBoardStopsAmount[i][stopvar] += 1
			except:
				pass 
				#print(str(busList[i]) +'bus no longer exists')
		return 
	def setBusStops(onBoardStopsAmount,alightTime,majornum,busWaitingPassengersAtStops,busCurrentStop):
		#set stops for buses based on people on board and waiting 
		for i in range(len(onBoardStopsAmount)): #same size for waiting 
			for j in range(len(onBoardStopsAmount[i])): #same size for waiting 
				if onBoardStopsAmount[i][j] + busWaitingPassengersAtStops[i][j] > 0:
					string = "busStop_" + str(j)
				
					if int(busCurrentStop[i]) < int(j): #makes sure that the bus is still before that stop otherwise dont bother setting cuz thats dumb
					#	print("past" + str(busCurrentStop[i]) + "newstop at" + str(j))
					#	print(busCurrentStop)
						if int(j) in majornum: #check if major stop and do max.
							traci.vehicle.setBusStop(busList[i],string,duration=max(45,min(120,alightTime*(onBoardStopsAmount[i][j]+busWaitingPassengersAtStops[i][j])))) #this will overide the major bus stop
						else:
							traci.vehicle.setBusStop(busList[i],string,duration=alightTime*(onBoardStopsAmount[i][j]+busWaitingPassengersAtStops[i][j])) 
						
						#STOP OVERTAKING
						if i % 2 == 0: #leading bus was set
							if int(busCurrentStop[i+1]) == int(busCurrentStop[i]) and busCurrentStop[i] != -1 :  #check follow bus 
								#print('this mofo bus is close')
								#print(busCurrentStop)
								#print(busCurrentStop[i+1],busCurrentStop[i])
							
								traci.vehicle.setBusStop(busList[i+1],string,duration=2) 
								
	
	def updatePeopleWaiting(peopleWaitingInfo,busList,busCurrStop,busEdges,deletedPeople):
	#check if person ready to be swapped 
		for personinfo in peopleWaitingInfo[:]: #use a copy so can modify original 	
			try:
				currPersonEdge = traci.person.getStage(personinfo[0],nextStageIndex=0).edges[0]
				desiredBus = personinfo[2]  
				currBusEdge = traci.vehicle.getRoadID(busList[desiredBus])
				if (currBusEdge not in busEdges) and (int(busCurrentStop[desiredBus]) >= int(personinfo[3])): #implies bus is not at a stop and has moved
					#they can now board!!
					traci.person.removeStages(personinfo[0])
					deletedPeople.append([personinfo[0],traci.person.getEdges(personinfo[0]),personinfo[1]])
					peopleWaitingInfo.remove(personinfo)
					#print('delete him')
				#check that bus pos past edge of thing or not
			except:
				pass 
				#print(str(desiredBus) +" no longer exist")
		return 
	
	def updatePeopleWaitingV2(peopleSpawnInfo,busList,busCurrStop,busEdges,deletedPeople,alpha,Tmax,busCapacity,peopleWaitingInfo,busWaitingPassengersAtStops):
	#check if person ready to be swapped 
		for personinfo in peopleSpawnInfo[:]: #use a copy so can modify original 	
			currPersonEdge = traci.person.getStage(personinfo[0],nextStageIndex=0).edges[0]
			firstBus = personinfo[2]  
			currBusEdge = traci.vehicle.getRoadID(busList[firstBus])
			if int(busCurrStop[firstBus]) >= int(personinfo[3])-1:
				if busCapacity[firstBus] >= 70: #wait for next one instead and append to new peopleSpawnInfo
				#	print(personinfo[0]+ 'I WILL WAIT FOR THE NEXT BUS!' + str(int(firstBus)+1)) 
				#	print(busCurrStop)
					peopleWaitingInfo.append(personinfo)
					peopleSpawnInfo.remove(personinfo)
					busWaitingPassengersAtStops[firstBus+1][personinfo[3]] += 1
				else: #board rightttt now and make em dead 
					traci.person.removeStages(personinfo[0])
					deletedPeople.append([personinfo[0],traci.person.getEdges(personinfo[0]),personinfo[1]])
					peopleSpawnInfo.remove(personinfo)
					busWaitingPassengersAtStops[firstBus][personinfo[3]] += 1
		return 
	
	def mobSpawn(personIDNum,busEdges,minor,major,busStops,numpeople):
		initedge = "-101161164#17"
		print("add 60 people")
		for i in range(numpeople):
			personID = "p" + str(personIDNum)
			unused1,stop2,unused2,destEdge = personRouteGenerator(busEdges,minor,major,busStops,True)
			traci.person.add(personID,initedge,0)
			traci.person.appendWalkingStage(personID,initedge,1,duration=1,speed=5,stopID="busStop_0")
			traci.person.appendDrivingStage(personID,destEdge,"902",stopID=stop2)
			personIDNum += 1
		return personIDNum
		
	def findClosestTwoBuses(theirStop,busCurrStop):
		first = -1
		second = -1
		one = 100
		two = 100
	#	print(theirStop)
		#print(busCurrStop)
		for i in range(len(busCurrStop)):
			if theirStop > int(busCurrStop[i]):
				diff = theirStop-int(busCurrStop[i])
				if diff < one:
					first = i
					one = diff 
				elif diff < two: 
					second = i
					two = diff
				#print(first,second,diff)
		return first,second #first,second is bus 
	
	def addPerson(personIDNum,busEdges,minor,major,busStops,peopleSpawnInfo,busCurrentStop): #WIPPPPPPPPPPPPP
		#edge = "-101161164#17" #start
		#edge = "-101161164#9" #busstop2
		#destedge = "206508268#0" #bus stop 5
		stopID1, stopID2, startEdge, destEdge = personRouteGenerator(busEdges,minor,major,busStops,False)
		waitStop = int(stopID1.split("_")[1]) #THIS IS STOP PERSON IS WAITING AT!!! 
		personID = "pr" + str(personIDNum)
		firstbus,secondbus =findClosestTwoBuses(waitStop,busCurrentStop)
		if firstbus <= 8 and secondbus > 0: #dont want to spawn people if there are no buses to save time 
			traci.person.add(personID,startEdge,0)
			traci.person.appendWalkingStage(personID,startEdge,1,duration=1,speed=5,stopID=stopID1) #put walking 
			peopleSpawnInfo.append([personID,destEdge,firstbus,waitStop])
			traci.person.appendWaitingStage(personID,duration = 10000000,description="waiting",stopID = stopID1) 
			personIDNum += 1
		return personIDNum
		
	def calcTimeForBus(bus,desiredStop):
		currEdge = traci.vehicle.getRoadID(bus)
		busRouteEdges = traci.vehicle.getRoute(bus)
		busRouteIndex = traci.vehicle.getRouteIndex(bus)
		stopIndex = busRouteEdges.index(desiredStop)
		estTime = 0 

		if currEdge == "":
			return 0
		else:	
			for i in range(busRouteIndex,stopIndex+1):
				#print(busRouteEdges[i])
				lane = busRouteEdges[i] + "_1"
				#print(lane)
				speed = traci.lane.getMaxSpeed(lane)
				length = traci.lane.getLength(lane)
				estTime += length/speed 
			return estTime 
			
	def humanModelDecider(timediff,cap,param,tmax):
		prob = param*min(cap/float(70),1) + (1-param)*(1 -(timediff/tmax))
		return prob 
		
	#VARIABLES TO WORK WITH	
	personIDNum =  1
	traci.start(sumoCmd)
	busStops = traci.simulation.getBusStopIDList() #GETS LIST OF BUS STOPS 
	busList = ["b0","b1","b2","b3","b4","b5","b6","b7","b8"] #NAME OF OUR BUSES
	busWaitingPassengersAtStops = [[0 for i in range(len(busStops))] for i in range(len(busList))] #KEEPS TRACK OF PASSENGERS WAITING
	copyBusWaitingPassengersAtStops = busWaitingPassengersAtStops[:] #keep copy 
	onBoardStopsAmount = [[0 for i in range(len(busStops))]for i in range(len(busList))] #KEEPS TRACK OF PASSENGERS ON BOARD OF BUSES
	alightTime = 10 #seconds
	busCurrentStop = [-1 for i in range(8)] #KEEPS TRACK OF WHERE BUS CURRENTLY PAST STOP 
	copyBusCStop = busCurrentStop[:] #copy list
	busCapacity = [0 for i in range(8)] #KEEPS TRACK OF AMOUNT OF PPL ON BOARD OF BUS 
	copyBusCapacity = busCapacity[:] #copy list
	peopleSpawnInfo = [] #KEEPS TRACK OF PERSON GENERATED IF THEY ARE SPAWNED TO WAIT 
	peopleWaitingInfo = [] #KEEPS TRACK OF PERSON GENERATED IF THEY ARE SPAWNED TO WAIT 

	deletedPeople = []
	majornum = [0,4,16,26,34,45,53,62] #ITS JUST THE MAJOR BUS STOPS TO HELP SPEED 
	step = 0
	endSim = 14000000 # the simulation will be permitted to run for a total of endSim milliseconds; 1800000 milliseconds = 30 minutes
	personTimer = 8000 #every 8 second add person
	alpha = 0.2
	Tmax = 15*60 #seconds
	while step < endSim:
	#check if bus still exists to prevent errors 
		peopleList = traci.person.getIDList()		
		if step == 0: #spawn 60 people for 1st bus bunched 
			personIDNum = mobSpawn(personIDNum,busEdges,minor,major,busStops,60)
		if step == 1800*1000 or step == 3600*1000  or step == 5400*1000:
			personIDNum = mobSpawn(personIDNum,busEdges,minor,major,busStops,40)
		if step == 140*1000 or step == 1980*1000  or step == 3780*1000  or step == 5580*1000:
			personIDNum = mobSpawn(personIDNum,busEdges,minor,major,busStops,10)
		updateBusPosAndCap(busList,busCapacity,busCurrentStop,busEdges)
		revivePerson(deletedPeople,busEdges,minor,major,busStops) #function changes waiting to boarding state
		updatePeopleWaitingV2(peopleSpawnInfo,busList,busCurrentStop,busEdges,deletedPeople,alpha,Tmax,busCapacity,peopleWaitingInfo,busWaitingPassengersAtStops)
		updatePeopleWaiting(peopleWaitingInfo,busList,busCurrentStop,busEdges,deletedPeople)
		
		#this should actually only change every bus stop or bus capacity or passengers waiting 
		if busCurrentStop != copyBusCStop or busCapacity != copyBusCapacity or copyBusWaitingPassengersAtStops != busWaitingPassengersAtStops:
			updateOnBoardStatus(busCapacity,onBoardStopsAmount,busList) 
			setBusStops(onBoardStopsAmount,alightTime,majornum,busWaitingPassengersAtStops,busCurrentStop)
		if (step+1000) % personTimer == 0:
		#if step == 0:
			personIDNum = addPerson(personIDNum,busEdges,minor,major,busStops,peopleSpawnInfo,busCurrentStop)
							
		
		#write to file for performance measures
		if busCurrentStop!= copyBusCStop:
			for i in range(len(copyBusCStop)):
				if busCurrentStop[i] != copyBusCStop[i]:
					
					f = open("capacitycontrol.txt","a")
					f.write(str(i)+","+str(copyBusCapacity[i])+","+str(copyBusCStop[i])+"\n")
					#f.write("[" + str(copyBusCapacity) +"," + str(copyBusCStop) +"]" + "\n")
					f.close()
		onBoardStopsAmount = [[0 for i in range(len(busStops))]for i in range(len(busList))] #this is reset cuz some whacky stuff happened to some passengers onboard already
		copyBusCStop = busCurrentStop[:]
		copyBusCapacity = busCapacity[:]
		copyBusWaitingPassengersAtStops = busWaitingPassengersAtStops[:]
		
		
		step += 1000 # in milliseconds
		traci.simulationStep()
	print "Closing the main program. Goodbye."
	traci.close() # close the connection to SUMO