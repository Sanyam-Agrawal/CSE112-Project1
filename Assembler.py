import sys

# Hack for Windows CLI
if __import__('os').name == "nt" : __import__('os').system('color')

# Easy error reporting
def rprint (statement) : print("\033[91m{}\033[00m" .format(statement))

instruction_length = 12
opcode_length      = 4
address_length     = instruction_length - opcode_length

opcode_translations = {
                       "CLA":"0000" , "LAC":"0001" , "SAC":"0010" ,
                       "ADD":"0011" , "SUB":"0100" , "BRZ":"0101" ,
                       "BRN":"0110" , "BRP":"0111" , "INP":"1000" , 
                       "DSP":"1001" , "MUL":"1010" , "DIV":"1011" ,
                       "STP":"1100"
                      }

symbol_table = {}



def first_pass (data_lines) :

	flag = True

	line_counter = 1

	labels_accessed = {}

	Stp = False

	for i in data_lines :

		line = i[:]

		if line[0][-1] == ':' :

			line[0] = line[0][:-1]

			if line[0] in symbol_table :

				flag = False
				
				if symbol_table[line[0]][0] == "variable" :
					rprint ("Syntax Error in line " + str (line_counter) + " ---> " +
						"Variable already defined with same name as a label.")
				
				else :
					rprint("Syntax Error in line " + str (line_counter) + " ---> " + "Label already defined")

				line = line[1:]
			
			else :

				if line[0] in opcode_translations :

					flag = False

					rprint ("Syntax Error in line " + str (line_counter) + " ---> " + "Label's name"
						+ " cannot be same as opcode")
				
				else :		
					symbol_table[line[0]] = ["label", line_counter]
				
				line = line[1:]

		if len(line) == 0 :

			flag = False

			rprint ("Syntax Error in line " + str (line_counter) + " ---> " + "Empty line after label")
				
		elif line[0] in opcode_translations :

			if line[0] == "CLA" :

				if len(line) > 1 :
					flag = False
					rprint ("Syntax Error in line " + str (line_counter) + " ---> " + "Too many arguments")

			elif line[0] == "STP" :

				Stp = True

				if len(line) > 1 :
					flag = False
					rprint ("Syntax Error in line " + str (line_counter) + " ---> " + "Too many arguments")
				
				elif len(data_lines) != line_counter :
					rprint ("Warning, STP found before end of Program in line " + str (line_counter))

			else :

				if len(line) == 1 :
					flag = False
					rprint ("Syntax Error in line " + str (line_counter) + " ---> " + "Too few arguments")

				elif len(line) > 2:
					flag = False
					rprint ("Syntax Error in line " + str (line_counter) + " ---> " + "Too many arguments")

				elif line[0] == "BRP" or line[0] == "BRN" or line[0] == "BRZ" :

					if line[1] in symbol_table and symbol_table[line[1]][0] == "variable" :

						flag = False

						rprint ("Syntax Error in line " + str (line_counter) + " ---> " +
							"Label already defined as variable")

					elif line[1] in opcode_translations :

						flag = False

						rprint ("Syntax Error in line " + str(line_counter) + " ---> " +
								"label's name cannot be same as opcode")
						
					elif line[1] in labels_accessed :
						labels_accessed[line[1]].append(line_counter)

					else :
						labels_accessed[line[1]] = [line_counter]

				else :

					if line[1] not in symbol_table and line[1] not in labels_accessed :

						if line[1] in opcode_translations :

							flag = False

							rprint ("Syntax Error in line " + str(line_counter) + " ---> " +
								"variable's name cannot be same as opcode")

						else :
							symbol_table[line[1]] = ["variable"]

					elif (line[1] in symbol_table and symbol_table[line[1]][0] == "label") or \
							line[1] in labels_accessed:

						flag = False

						rprint ("Syntax Error in line " + str (line_counter) + " ---> " +
							"Label already defined with the same name")

		else :

			flag = False

			rprint ("Syntax Error in line " + str (line_counter) + " ---> " + "Unknown Opcode")
	
		line_counter += 1



	if not Stp : 

		flag = False

		rprint ("Syntax Error ---> No stop command in the assembly code")

	# Check : All labels accessed have been defined.
	for i in labels_accessed :

		if i not in symbol_table :

			flag = False

			line_numbers = " ".join(map(str,labels_accessed[i]))

			rprint ("Syntax Error" + " ---> " + "Label " + i +
				" is accessed but not in defined in the line(s):- " + line_numbers)


	# Assign memory addresses to variables.

	for i in symbol_table : 

		if symbol_table[i][0] == "variable" :

			symbol_table[i].append(line_counter)

			line_counter+=1


	return flag



def second_pass (data_lines) :

	object_code = []

	for i in data_lines :

		line = i[:]

		#Get rid of label
		if line[0][-1] == ":" : line = line[1:]

		if len(line) == 2 : address = bin( symbol_table[line[1]][1] )[2:]
		else : address = bin(0)[2:]

		address = '0'*(address_length-len(address)) + address

		object_code.append( opcode_translations[line[0]] + address )

	return object_code



if __name__ == '__main__' :


	if len(sys.argv) == 1 :

		print ("Usage Instructions: python3 Assembler.py <name_of_assembly_file>")

		quit()

	if len(sys.argv) > 2 :

		rprint ("Too many arguments, exiting")

		quit()


	try:

		_file = open (sys.argv[1])

	except:

		rprint ("ERROR")

		print (
			"File with the given name doesn't exist. \n "
			"Possible Reasons: \n "
			"1. Wrong name entered. \n "
			"2. File extension not entered. \n "
			"3. File is in a different directory than the present working directory. \n "
			"4. The file given has strict file permissions, so we are restricted from reading it. "
		)

		rprint ("Exiting")

		quit()


	try:

		data = _file.read()

	except:

		rprint ("ERROR")
		print ("Unable to read data, possibly file is corrupted.")
		rprint ("Exiting")

		quit()


	_file.close()


	# Split the code according to newline
	data_lines = data.split("\n")

	# Remove comments
	for i in range(len(data_lines)) :
		pos = data_lines[i].find("#")
		if pos != -1: data_lines[i] = data_lines[i][:pos]

	# Remove redundant whitespace
	data_lines = [(" ".join(i.split())).split(" ") for i in data_lines]
	# Remove blank lines
	data_lines = [i for i in data_lines if i!=[""]]

	flag = first_pass  (data_lines)

	if flag == True :

		object_code = second_pass (data_lines)

		print ("\033[92mProgram succesfully assembled. :)\033[00m")

		# Print the symbol table
		print ("\033[93mSymbol Table\033[00m")
		print ("Symbol\t Type\tAddress\tSize")
		for i in symbol_table:
			print (i, "\t", " "*(8-len(symbol_table[i][0])),symbol_table[i][0], "\t", symbol_table[i][1],end=" ")
			if symbol_table[i][0] == 'variable' : print (" \tword")
			else: print()

		print("\n\n")

		# Print the object code
		print ("\033[95mObject Code\033[00m")
		for i in object_code: print(i)
