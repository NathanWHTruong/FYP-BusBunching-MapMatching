import csv
import pandas
file_object  = open("1balcaptmax5.txt", "r")
b0 =[]
b1 = []
b2 = []
b3 = []
b4 = []
b5 = []
b6 = []
b7 = []
stop = []
for i in range(63):
	stop.append(i)
for line in file_object:
	line = line.split(",") #0 is bus, 1 is cap, 2 is stop 
	if line[0] == '0':
		b0.append(line[1])
	elif line[0] == '1':
		b1.append(line[1])
	elif line[0] == '2':
		b2.append(line[1])
	elif line[0] == '3':
		b3.append(line[1])
	elif line[0] == '4':
		b4.append(line[1])
	elif line[0] == '5':
		b5.append(line[1])
	elif line[0] == '6':
		b6.append(line[1])
	elif line[0] == '7':
		b7.append(line[1])
	else:
		pass 
		
import pandas
filenames = ['chelsea','edithvale','haileybury','springvale','brandonpark','glen','bwdhwy','nunawading']
b00 = []
b11 = []
b22 = []
b33 = []
b44 = []
b55 = []
b66 = []
b77 = []
majors = ['chelsea','chelsea','edithvale','edithvale','haileybury','haileybury','springvale','springvale','brandonpark','brandonpark','glen','glen','bwdhwy','bwdhwy','nunawading','nunawading']
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
					b00.append(tmp[6].split('"')[1])
				elif tmp[8].split("b")[1][0] == "1":
					b11.append(tmp[6].split('"')[1])
				elif tmp[8].split("b")[1][0] == "2":
					b22.append(tmp[6].split('"')[1])
				elif tmp[8].split("b")[1][0] == "3":
					b33.append(tmp[6].split('"')[1])
				elif tmp[8].split("b")[1][0] == "4":
					b44.append(tmp[6].split('"')[1])
				elif tmp[8].split("b")[1][0] == "5":
					b55.append(tmp[6].split('"')[1])
				elif tmp[8].split("b")[1][0] == "6":
					b66.append(tmp[6].split('"')[1])
					print(filenames[i])
				elif tmp[8].split("b")[1][0] == "7":
					b77.append(tmp[6].split('"')[1])
				else:
					pass
			##6,7
			#print(tmp[6],tmp[7])
print(len(b0))
print(len(b1))
print(len(b2))
print(len(b3))
print(len(b4))
print(len(b5))
print(len(b6))
print(len(b7))

df = pandas.DataFrame(data={"b": stop, "cap0": b0, "cap1": b1, "cap2": b2, "cap3": b3, "cap4": b4, "cap5": b5, "cap6": b6, "cap7": b7})
df2 = pandas.DataFrame(data={"sb":majors,"sbus0": b00, "sbus1": b11, "sbus2": b22, "sbus3": b33, "sbus4": b44, "sbus5": b55, "sbus6": b66, "sbus7": b77})
df3 = pandas.concat([df,df2], ignore_index=True, axis=1)
df3.to_csv("./tmax5filebal.csv", sep=',',index=False)

