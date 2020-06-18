   #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#
#											CSE - 112 - COMPUTER ORGANISATION
# Simple Implementation of an Assembler for an Accumulator Architecture Machine that handles basic conversion and variable 
# addressing 

# @Authors: Suchet Aggarwal - 2018105
#		  : Ujjwal Singh    - 2018113

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#
import sys
import os
import string
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

#OPCODE TABLE FOR THE GIVEN 12 BIT ACCUMULATOR MACHINE
OPTAB = {}
OPTAB["CLA"] = ["0000",0]
OPTAB["LAC"] = ["0001",1]
OPTAB["SAC"] = ["0010",1]
OPTAB["ADD"] = ["0011",1]
OPTAB["SUB"] = ["0100",1]
OPTAB["BRZ"] = ["0101",1]
OPTAB["BRN"] = ["0110",1]
OPTAB["BRP"] = ["0111",1]
OPTAB["INP"] = ["1000",1]
OPTAB["DSP"] = ["1001",1]
OPTAB["MUL"] = ["1010",1]
OPTAB["DIV"] = ["1011",1]
OPTAB["STP"] = ["1100",0]


#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

#Helper Functions for cleaning and processing data

def isComment(line):
	if line.find("//")!=-1:
		return True
	else:
		return False

def hasVariable(line):
	l = str(line)
	label = False
	tokens = l.split()
	if "DW" in tokens:
		return True
	else:
		return False

def getVariable(line):
	l = str(line)
	label = False
	tokens = l.split()
	if hasVariable(line):
		return [tokens[0],tokens[2]]
	else:
		return False		

def hasLabel(line):
	if line.find(":")!=-1:
		return True
	else:
		return False

def getLabel(line):
	l = str(line)
	label = False
	tokens = l.split()
	if hasLabel(line):
		return hasSymbol(line)
	else:
		return False

def RepresentsInt(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False

def hasSymbol(line):
	l = str(line)
	symbol = False
	tokens = l.split()
	for i in tokens:
		if i not in list(OPTAB.keys()) and not(RepresentsInt(i)):
			symbol = i
			break
	return symbol

def getOpcode(line):
	l = str(line)
	tokens = l.split()
	opcode = None
	noofOpcodes = 0
	if ":" not in tokens:
		if tokens[0] not in OPTAB and "DW" not in tokens:
			print("[Error] Invalid OPCODE Used" , end =' ')
			return -2
	else:
		if tokens[2] not in OPTAB:
			print("[Error] Invalid OPCODE Used" , end =' ')
			return -2
	for i in tokens:
		if i in OPTAB and noofOpcodes<1:
			opcode = i
			noofOpcodes+=1
	if noofOpcodes>1:
		raise Exception("One of the Lines contains multiple OPCODES...")
	else:
		return opcode

def getPsuedoOP(line):
	l = str(line)
	tokens = l.split()
	if "STP" in tokens:
		return "STP"
	elif "START" in tokens:
		return "START"
	else:
		return False

def isEnd(line):
	l = str(line)
	tokens = l.split()
	if "END" in tokens:
		return True
	else:
		return False

def isStart(line):
	l = str(line)
	tokens = l.split()
	if "START" in tokens:
		return True
	else:
		return False

def getStart(line):
	l = str(line)
	tokens = l.split()
	if "START" in tokens and len(tokens)==2:
		if int(tokens[1])>=256:
			return -1
		else:
			return tokens[1]
	elif "START" in tokens and len(tokens)!=2:
		return 0
	else:
		return False	

def getOperand(line):
	l = str(line)
	tokens = l.split()
	opc = None
	error_flag = False
	if ":" not in tokens:
		opc = tokens[0]
		if len(tokens)>4:
			error_flag = True
	else:
		opc = tokens[2]
		if len(tokens)>4:
			error_flag = True

	if "DW" in tokens:
		opc = tokens[1]
	
	if error_flag:
		print("[Error] OPCODE "+str(tokens[0]) +" Supplied with too many arguments thab required at Line" , end =' ')
		return -2
	if OPTAB[opc][1] == 1 and tokens[-1] in OPTAB:
		print("[Error] OPCODE "+str(tokens[-1]) +" Supplied with fewer arguments thab required at Line" , end =' ')
		return -2
	if tokens[-1] not in OPTAB:
		return tokens[-1]
	else:
		return False

OPTAB["START"] = ["",-1]
OPTAB["END"] = ["",-1]
#Assuming opcode for DW
OPTAB["DW"] = ["1101",2]

def delAllFiles():
	os.remove("tempfile.txt")
	os.remove("LABTAB.txt")
	os.remove("SYMTAB.txt")
	os.remove("output.out")

def deleteTempFiles():
	os.remove("tempfile.txt")
	os.remove("LABTAB.txt")
	os.remove("SYMTAB.txt")

def binary(n):
	n = int(n)
	return '{0:08b}'.format(n)

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

def pass_one(linebyline):
	"""
	Working of the first Pass:
	--------------------------
	1.	The location counter is initialised
	2.	Label table and Symbol Tables are initialised
	3.	The input program is processed line by line, wherein only the non-commented lines are processed, and the comments are simply ignored
	4.	If the given line:
		a.	Is a Start Statement, then the address given/specified is used starting value of location counter
		b.	Has a label then it is put in the label table
		c.	Has a Variable then it is put in the symbol table
		d.	Has opcode then the opcode is verified whether it is valid, if not an Error is thrown, and assembly process is terminated.
		e.	If the given opcode is correct then its corresponding operand is read (depending on whether it takes in any operand or not), else an error is thrown.
		f.	If it is a variable declarative then its symbol is checked whether it is present in the symbol table,
		g.	If it is a label then it is checked whether it is present in the symbol table,
	5.	If the code has variables/ symbols that have not been defined but have been used, then the assembler throws an error
	6.	If the code doesn’t encounter any END statement, then the code throws an error, and if it does have any then everything below the END statement is ignored.
	7.	The code prepares several temporary files, 
		a.	File that contains all the lines except the comments
		b.	Label/Variable Address Table 
		c.	Symbol Table
	8.  All errors are handled in the first pass.

	The symbol table and label table are in the form of a python dictionary which are dumped in temperory files.

"""
	LOC_CTR = 0 
	length = 12
	value = 0
	Type = None
	EOS = False
	f=open("tempfile.txt", "a+")
	f1 = open("LABTAB.txt", "a+")
	f2 = open("SYMTAB.txt", "a+")
	LABTAB ={}
	SYMTAB = {}
	err_end_flag = True
	err_start_flag = True
	tok  = 0
	lineno = 0
	for line in linebyline:
		line.strip()
		k = line.split()
		if not(isComment(line)):
			lineno+=1
			label = 0
			symbol = 0
			tok = getStart(line) 
			if isEnd(line):
				err_end_flag = False
				break

			if tok != False:
				LOC_CTR = int(tok)

			if tok == -1:
				print("[Error] Start statement specifies an address that is beyond the memory limit of the system line "+str(lineno))
				sys.exit(-1)
				delAllFiles()


			if isStart(line):
				err_start_flag = False
				continue
			
			if getLabel(line) != False:
				label = getLabel(line)
				if getLabel(line) in LABTAB:
					print("[Error] Multiple Declaration of Symbol "+str(getLabel(line))+" at line "+str(lineno))
					sys.exit(-1)
					delAllFiles()

				if getLabel(line) not in LABTAB:
					LABTAB[getLabel(line)] = LOC_CTR
					f1.writelines(getLabel(line)+" "+str(LOC_CTR)+"\n") 

			if hasSymbol(line) != False:
				symbol = hasSymbol(line)
				if hasSymbol(line) not in SYMTAB:
					SYMTAB[hasSymbol(line)] = LOC_CTR
					f2.writelines(hasSymbol(line)+" "+str(LOC_CTR)+"\n")

			if getVariable(line) != False:
				var = getVariable(line)
				if var[0] in LABTAB:
					print("[Error] Multiple Declaration of Variable "+var[0]+" at line "+str(lineno))
					sys.exit(-1)
					delAllFiles()

				if var[0] not in LABTAB:
					try:
						LABTAB[var[0]] = LOC_CTR
						f1.writelines(var[0]+" "+str(LOC_CTR)+"\n") 
					except:
						print("[Error] No inital value provided at Declaration of Variable "+str(getLabel(var[0]))+" at line "+str(lineno))
						sys.exit(-1)
						delAllFiles()						
					
			opcode = getOpcode(line)
			if opcode == -2:
				print("at line "+str(lineno))
				sys.exit(-1)
				delAllFiles()

			if getOperand(line)	== -2:
				print(str(lineno))
				sys.exit(-1)	
				delAllFiles()

			if "DW" in line:
				f.writelines(str(LOC_CTR)+ " " +line[0]+" " +opcode+ " " + str(getOperand(line)) +"\n")
			else:
				if getOperand(line) != False:
					f.writelines(str(LOC_CTR)+ " " +opcode+ " " + str(getOperand(line)) +"\n")
				else:
					f.writelines(str(LOC_CTR)+ " " +opcode+ " " + "None" +"\n")

			if not(isComment(line)):
				if OPTAB[opcode][1] == 0:
					LOC_CTR += 4
				else:
					LOC_CTR += 12
			

	if err_end_flag:
		print("[Error] Missing END statement...")
		sys.exit(-1)
		delAllFiles()

	if err_start_flag:
		print("[Error] Missing START statement...")
		sys.exit(-1)
		delAllFiles()

	error_flag = False
	var_not_defined = []
	for i in SYMTAB:
		if i not in LABTAB:
			error_flag = True
			var_not_defined.append(i)

	for i in var_not_defined:
		print("[Error] Symbol/Variable "+str(i)+" has been used but has not been defined...")

	if error_flag:
		sys.exit(-1)
		delAllFiles()

	f.close()
	f1.close()
	f2.close()
	pass_two(SYMTAB,LABTAB)

def pass_two(SYMTAB,LABTAB):

	"""
	Working of Pass Two:
	1.	Since the assembler runs this pass only if all the symbols, labels and opcodes have been declared the code can directly processed.
	2.	The Temporary file created during the first pass, is now processed line by line
	3.	The labels and variables are replaced by their corresponding addresses
	4.	The opcodes and the addresses are converted to their binary equivalents and all changes are written off to output.out
	5.	Clean-Up is done, removing all temporary files and symbol and label tables.

	"""
	try:
		symtable = open(source_filename)
		labtable = open(source_filename)
		temp = open("tempfile.txt")
	except:
		print("Problem in Assembly...")
		sys.exit(0)
	byteCode = None
	LOC = 0
	linebyline = temp.readlines()
	final = open("output.out", "a+")
	for i in linebyline:
		line = i.split()
		addr = line[0]
		operand = None
		try:
			opc = OPTAB[line[1]][0]
		except:
			opc = OPTAB[line[2]][0] 
		if opc=="1101":
			opc = binary(line[3])
		else:
			if line[2] in LABTAB:
				operand = LABTAB[line[2]]
				operand = binary(operand)
			elif OPTAB[line[1]][1]==1 and line[2] not in LABTAB:
				operand = binary(int(line[2]))
		l=binary(int(addr))
		if operand != None:
			final.writelines(l[-8:]+" : "+str(opc)+" "+str(operand)+"\n")
		else:
			final.writelines(l[-8:]+" : "+str(opc)+"\n")
	final.close()

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

#opening the input files...
try:
	source_filename = str(sys.argv[1])
	source = open(source_filename)
except:
	print("Please Enter Valid filename as python3 assembler.py <FILENAME>")
	sys.exit(0)

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

#Run the main code...
linebyline = source.readlines()
pass_one(linebyline)
deleteTempFiles()
source.close()