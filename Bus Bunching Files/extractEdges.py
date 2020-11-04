file_object  = open("stopdata.txt", "r")
edges =[]
for line in file_object:
	line = line[1:len(line)-3]
	print(line.split(" "))
	edges.append(line.split(" "))
for x in edges:
	x[2] = x[2][6:len(x[2])-1]
	print(x)
major = [] 
minor = []
for x in edges:
	if x[0] == "instantInductionLoop":
		major.append(x[2])
print(major)
for x in edges:
	if x[0] == "busStop" and x[2] not in major:
		minor.append(x[2])
print(minor)