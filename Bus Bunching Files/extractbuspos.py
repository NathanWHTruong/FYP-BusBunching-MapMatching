import csv
import pandas
filenames = ['chelsea','edithvale','haileybury','springvale','brandonpark','glen','bwdhwy','nunawading']
b0 = []
b1 = []
b2 = []
b3 = []
b4 = []
b5 = []
b6 = []
b7 = []

for i in range(len(filenames)):
	file_object  = open(filenames[i], "r")
	for line in file_object:
		tmp = line.split(" ")
		#print(line.split(" "))
		if len(line.split(" ")) >= 12: 
			state = tmp[7].split("=")[1]
			
			#print(state[1:6])
		#	print(state[1:6]=="enter")
			if str(state[1:6]) == "enter" or str(state[1:6])=="leave":
				
				if tmp[8].split("b")[1][0] == "0":
					b0.append(tmp[6].split('"')[1])
				elif tmp[8].split("b")[1][0] == "1":
					b1.append(tmp[6].split('"')[1])
				elif tmp[8].split("b")[1][0] == "2":
					b2.append(tmp[6].split('"')[1])
				elif tmp[8].split("b")[1][0] == "3":
					b3.append(tmp[6].split('"')[1])
				elif tmp[8].split("b")[1][0] == "4":
					b4.append(tmp[6].split('"')[1])
				elif tmp[8].split("b")[1][0] == "5":
					b5.append(tmp[6].split('"')[1])
				elif tmp[8].split("b")[1][0] == "6":
					b6.append(tmp[6].split('"')[1])
				elif tmp[8].split("b")[1][0] == "7":
					b7.append(tmp[6].split('"')[1])
				else:
					pass
			##6,7
			#print(tmp[6],tmp[7])
df = pandas.DataFrame(data={"bus0": b0, "bus1": b1, "bus2": b2, "bus3": b3, "bus4": b4, "bus5": b5, "bus6": b7, "bus7": b7})
df.to_csv("./5file.csv", sep=',',index=False)