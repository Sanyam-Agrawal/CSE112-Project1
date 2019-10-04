import sys
from termcolor import colored, cprint 

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

	for i in data_lines :

		# To remove reduntant whitespace
		line_of_data = (" ".join(i.split())).split(" ")

		# To handle empty instruction correctly
		if i == "" : line_of_data = []

		if len(line_of_data) != 0 :

			line = line_of_data[:]

			if line[0][-1] == ':' :

				if line[0] in symbol_table :

					flag = False
					
					if symbol_table[line[0]][1] == "variable" :
						print ("Syntax Error\nVariable already defined with same name as a label.")
					
					else :
						print("Syntax Error\nLabel is already defined in line " + str (line_counter))
				
				else :
				
					symbol_table[line[0]] = ["label", line_counter]
					line = line[1:]

			if line[0] in opcode_translations :

				if line[0] == "CLA" :

					if len(line) > 1 :
						flag = False
						print ("Syntax Error\nToo many arguments in line " + str (line_counter))

				elif line[0] == "STP" :

					if len(line) > 1 :
						flag = False
						print ("Syntax Error\nToo many arguments in line " + str (line_counter))
					
					elif len(data_lines) != line_counter :
						print ("Warning, STP found before end of Program in line " + str (line_counter))
				
				elif line[0] == "INP" :

					if len(line) > 2 :
						flag = False
						print ("Syntax Error\nToo many arguments in line " + str (line_counter))

					elif len(line) == 1 : 
						flag = False
						print ("Syntax Error\nToo few arguments in line " + str (line_counter))

					elif not line[1].isdigit() :
						if line[1] not in symbol_table:
							symbol_table[line[1]] = ["variable",line_counter]
						elif symbol_table[line[1]][0] == "label" :
								flag = False
								print ("Syntax Error\nLabel already defined with the same name " + str (line_counter))

				elif line[0] == "BRP" or line[0] == "BRN" or line[0] == "BRZ" :

					if len(line) > 2:
						flag = False
						print ("Syntax Error\nToo many arguments in line " + str (line_counter))

					elif len(line) == 1 : 
						flag = False
						print ("Syntax Error\nToo few arguments in line " + str (line_counter))

					elif line[1].isdigit() :
						flag = False
						print ("Syntax Error\nLabel can't be a numeric " + str (line_counter))

				else:

					if len(line) > 2 :
						flag = False
						print ("Syntax Error\nToo many arguments in line " + str (line_counter))

					elif len(line) == 1 :
						flag = False
						print ("Syntax Error\nToo few arguments in line " + str (line_counter))

					elif not line[1].isdigit() :
						flag = False
						if line[1] not in symbol_table :
							print ("Syntax Error\nVariable not defined in line " + str (line_counter))
			
			else :
				ebprint ("Syntax Error\nUnknown Opcode in line " + str (line_counter))
		
		else :

			#TODO: Think deeply about the designed handling of blank lines
			ebprint ("Syntax Error\nEmpty line")
		
		line_counter += 1

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
		       "File with the given name doesn't exist.\n \
		       Possible Reasons: \n \
		       1. Wrong name entered. \n \
		       2. File extension not entered. \n \
		       3. File is in a different directory than the present working directory. \n \
		       4. The file given has strict file permissions, so we are restricted from reading it."
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


	data_lines = data.split("\n")
	if data_lines[-1] == "" : data_lines = data_lines[:-1] # handling last line being empty

	flag = first_pass  (data_lines)
	
	if flag == True :

		second_pass (data_lines)

		cprint ("Program succesfully assembled. :)", 'green', attrs=['bold'])

		#TODO: Print the symbol table
