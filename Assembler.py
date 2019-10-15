import sys
from termcolor import cprint 

# Hack for Windows CLI
if __import__('os').name == "nt" : __import__('os').system('color')

# Easy error reporting
ebprint = lambda x : cprint (x, 'red', attrs=['bold'])
eprint  = lambda x : cprint (x, 'red')

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


	for i in data_lines :

		line = i

		if line[0][-1] == ':' :

			if line[0] in symbol_table :

				flag = False
				
				if symbol_table[line[0]][1] == "variable" :
					eprint ("Syntax Error" + " ---> " + "Variable already defined with same name as a label.")
				
				else :
					eprint("Syntax Error" + " ---> " + "Label already defined in line " + str (line_counter))
			
			else :

				if line[0][:-1] in opcode_translations :
					ebprint ("Syntax Error" + " ---> " + "Label's name cannot be same as opcode "
						+ "in line " + str (line_counter))
				
				else :		
					symbol_table[line[0][:-1]] = ["label", line_counter]
				
				line = line[1:]

		if len(line) == 0 :

			flag = False

			eprint ("Syntax Error" + " ---> " + "Empty line after label in line " + str (line_counter))
				
		elif line[0] in opcode_translations :

			if line[0] == "CLA" :

				if len(line) > 1 :
					flag = False
					ebprint ("Syntax Error" + " ---> " + "Too many arguments in line " + str (line_counter))

			elif line[0] == "STP" :

				if len(line) > 1 :
					flag = False
					ebprint ("Syntax Error" + " ---> " + "Too many arguments in line " + str (line_counter))
				
				elif len(data_lines) != line_counter :
					eprint ("Warning, STP found before end of Program in line " + str (line_counter))

				break

			else :

				if len(line) == 1 :
					flag = False
					ebprint ("Syntax Error" + " ---> " + "Too few arguments in line " + str (line_counter))

				elif len(line) > 2:
					flag = False
					ebprint ("Syntax Error" + " ---> " + "Too many arguments in line " + str (line_counter))

				elif line[0] == "BRP" or line[0] == "BRN" or line[0] == "BRZ" :

					if line[1] in symbol_table and symbol_table[line[1]][0] == "variable" :

						flag = False

						ebprint ("Syntax Error" + " ---> " + "Label already defined as variable " +
							 "in line " + str (line_counter))

					elif line[1] in labels_accessed :
						labels_accessed[line[1]].append(line_counter)

					else :
						labels_accessed[line[1]] = [line_counter]

				else :
					
					if line[1] not in symbol_table and line[1] not in labels_accessed :

						if line[1] in opcode_translations :

							ebprint ("Syntax Error" + " ---> " + "variable's name cannot be same"
								 + " as opcode in line " + str(line_counter))

						else :
							symbol_table[line[1]] = ["variable"]

					elif line[1] in symbol_table and symbol_table[line[1]][0] == "label" or line[1] in labels_accessed:

						flag = False

						ebprint ("Syntax Error" + " ---> " + "Label already defined with the same name "
							 + "in line " + str (line_counter))

		else :

			flag = False

			ebprint ("Syntax Error" + " ---> " + "Unknown Opcode in line " + str (line_counter))
	
		line_counter += 1


	# Check : All labels accessed have been defined.

	for i in labels_accessed :

		if i not in symbol_table :

			flag = False

			line_numbers = " ".join(map(str,labels_accessed[i]))

			ebprint ("Syntax Error" + " ---> " + "Label " + i +
				" is accessed but not in defined in the line(s):- " + line_numbers)


	# Assign memory addresses to variables.

	for i in symbol_table : 

		if symbol_table[i][0] == "variable" :

			symbol_table[i].append(line_counter)

			line_counter+=1


	return flag




if __name__ == '__main__' :


	if len(sys.argv) == 1 :

		print ("Usage Instructions: python3 Assembler.py <name_of_assembly_file>")

		quit()

	if len(sys.argv) > 2 :

		ebprint ("Too many arguments, exiting")

		quit()


	try:

		_file = open (sys.argv[1])

	except:

		ebprint ("ERROR")

		print (
			"File with the given name doesn't exist. \n "
			"Possible Reasons: \n "
			"1. Wrong name entered. \n "
			"2. File extension not entered. \n "
			"3. File is in a different directory than the present working directory. \n "
			"4. The file given has strict file permissions, so we are restricted from reading it. "
		)

		eprint ("Exiting")

		quit()


	try:

		data = _file.read()

	except:

		ebprint ("ERROR")
		print ("Unable to read data, possibly file is corrupted.")
		eprint ("Exiting")

		quit()


	_file.close()


	# Split the code according to newline
	data_lines = data.split("\n")
	# Remove redundant whitespace
	data_lines = [(" ".join(i.split())).split(" ") for i in data_lines]
	# Remove blank lines
	data_lines = [i for i in data_lines if i!=[""]]

	flag = first_pass  (data_lines)

	if flag == True :

		# second_pass (data_lines)

		cprint ("Program succesfully assembled. :)", 'green', attrs=['bold'])

		#TODO: Print the symbol table
