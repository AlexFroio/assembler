import json, re, ast, argparse
from pprint import pprint
comment = re.compile('^;')
inDirectives = False
inConstants = False
inCode = False
opcode = 0
Ri = 0
Rj = 0
AsmLine = list()
directives = dict()
constants = dict()
wordCheck = str()
romOut = ["-- Memory File output by ahf_asm.py",
"-- This is machine code generated for single core,",
"-- non-pipelined ahfRISC521 test",
"WIDTH=14",
"DEPTH=1024",
"ADDRESS_RADIX=HEX",
"DATA_RADIX=HEX",
"CONTENT BEGIN"]
ramOut = ["-- Memory File output by ahf_asm.py",
"-- This is machine code generated for single core,",
"-- non-pipelined ahfRISC521",
"WIDTH=14",
"DEPTH=1024",
"ADDRESS_RADIX=HEX",
"DATA_RADIX=HEX",
" ",
"CONTENT BEGIN"]
romTemp = list()
ramTemp = list()
jmpTemp = dict()
newdict = dict()
parser = argparse.ArgumentParser(description='Take in user generated Assembly, optional for user OpCode JSON')
parser.add_argument('asm_file', help='Sets the asm input file for the assembler to deconstruct into .mif')
parser.add_argument('opCode_json', help='insert path file to custom json OpCode file', nargs='?')
parser.add_argument('-v', '--verbose', help="Verbose mode is enabled")
args = parser.parse_args()
if args.opCode_json:
    with open(args.opCode_json) as OpData:
        OpDict = json.load(OpData)
else:
    OpDict = {
	"LD"  	: "0",
	"ST" 	: "1",
	"CPY"	: "2",
	"SWAP"	: "3",
	"JMP"	: "4",
	"ADD"	: "5",
	"SUB"	: "6",
	"ADDC"	: "7",
	"SUBC"	: "8",
	"NOT"	: "9",
	"AND"	: "10",
	"OR"	: "11",
	"SHRA"	: "12",
	"ROTR"	: "13",
    "ADDV"  : "14"
	}

for i in OpDict:
	newdict[str(i)] = (int(OpDict[i]))
	

OpDict = newdict
pprint(OpDict)

with open(args.asm_file) as AsmInput:
    for line in AsmInput:
        if re.search(comment, line.strip()):
            Ri = Ri
        else:
            AsmLine.append(line.strip())
pprint(AsmLine)	
#for i in range (0, len(AsmLine)):
#    AsmLine[i] = re.sub('\t', ' ', AsmLine[i])

j = 0x0
try:
    for constCheck in AsmLine:    
        if constCheck.startswith('.directives'):
            inDirectives = True
            pprint("I'm in Directives!")
            j = 0
        elif constCheck.startswith('.enddirectives'):
            inDirectives = False
            j = 0
            pprint("I'm out of directives!")
        elif constCheck.startswith('.equ') and inDirectives:
            directives[re.search('(?<=\s)[a-zA-Z]+', constCheck).group(0)] = re.search( '([0-9xA-F]+)',constCheck).group(1)
            constant = re.findall('0x[0-9A-Fa-f]+', constCheck)
            ramTemp.append('{:03x}'.format(j) + " : " + '{:04x}'.format(int(constant[0],16)))
            j = j + 1
            pprint(directives)
        elif constCheck.startswith('.array') and inDirectives:
            arrayStuff = re.findall('..;|[a-zA-Z]+', constCheck)
            directives[arrayStuff[1]] = {}
            for i in arrayStuff[2:]:
                pprint(hex((ord(i[0]) << 7) + ord(i[1])))
                directives[(arrayStuff[1] + str(j))] = (hex((ord(i[0]) << 7) + ord(i[1])))
                directiveHold = int(hex((ord(i[0]) << 7) + ord(i[1])),16)
                pprint(directiveHold)
                ramTemp.append('{:03x}'.format(j) + " : " + '{:04x}'.format(directiveHold))
                j = j + 1
            pprint(directives)
        elif constCheck.startswith('.narray') and inDirectives:
            arrayStuff = re.findall('\d+|[0-9a-zA-Z]+' , constCheck)
            directives[arrayStuff[1]] = {}
            for i in arrayStuff[2:]:
                directiveHold = int(i)
                directives[arrayStuff[1]] = directiveHold
                ramTemp.append('{:03x}'.format(j) + " : " + '{:04x}'.format(directiveHold))
                j = j + 1
            print(directives)
        elif constCheck.startswith('.constants'):
            inConstants = True
            pprint("In Constants!")
        elif constCheck.startswith('.endconstants'):
            inConstants = False
            j = 0
            pprint("Out of Constants!")
        elif inConstants:
            constants[re.search('(?<=\s)[a-zA-Z]+', constCheck).group(0)] = re.search('((?<=\s)[0-9xA-F]+)', constCheck).group(1)
            pprint(constants)
            #ramTemp.append(hex(j).rjust(5, '0') + " : " + str(re.search('((?<=\s)[0-9xA-F]+)', constCheck).group(1)))
            j = j + 1
        elif constCheck.startswith('.code'):
            inCode = True
            pprint("in code!")
        elif constCheck.startswith('.endcode'):
            inCode = False
            j = 0
        elif inCode:
            printFlag = False
            if constCheck.startswith('@'):
                    pprint("I am inside the jmpcheck!!!!")
                    jmpTemp[re.search('[a-zA-Z]+', constCheck).group(0)] = j
                    pprint(jmpTemp) 
            else:
                try:
                    wordCheck = re.search('([a-zA-Z]+)', constCheck).group(0)
                except AttributeError:
                    continue
                if wordCheck == 'JMPC' or wordCheck == 'JMPV' or wordCheck == 'JMPZ' or wordCheck == 'JMPN' or wordCheck == 'JMPNC' or wordCheck == 'JMPNV' or wordCheck == 'JMPNZ' or wordCheck == 'JMPNN':
                     wordCheck = 'JMP'

                for i in OpDict:
                    if wordCheck == i and printFlag is False:
                        if OpDict[i] == 0 or OpDict[i] == 1:
                            j = j + 2 
                            rMatch = re.findall('R\d+|-\d+\(R\d+\)|\d+\(R\d+\)|[0-9]x[0-9]+', constCheck)
                            if len(rMatch) >= 4:
                                pprint('Too many operands on' + re.sub('\s', ' ', constCheck))
                                exit()
                        elif OpDict[i] == 2 or OpDict[i] == 3 or OpDict[i] == 5 or OpDict[i] == 6 or OpDict[i] == 10 or OpDict[i] == 11:
                            rMatch = re.findall('\d+', constCheck)
                            j = j + 1
                            if len(rMatch) >= 3:
                                pprint('Too many operands on' + re.sub('\s', ' ', constCheck))
                                exit()
                            elif int(rMatch[0]) >= 32 or int(rMatch[1]) >= 32:
                                pprint('One of the registers is too big on line ' + re.sub('\s', ' ', constCheck))
                                exit()
                        elif OpDict[i] == 7 or OpDict[i] == 8 or OpDict[i] == 14:
                            rMatch = re.findall('R\d+|[0-9a-fA-F]x[0-9a-fA-F]+', constCheck)
                            pprint(rMatch)
                            j = j + 1
                            if len(rMatch) >= 4:
                                pprint('Too many operands on' + re.sub('\s', ' ', constCheck))
                                exit()
                        elif OpDict[i] == 9:
                            rMatch = re.findall('\d+', constCheck)
                            pprint(rMatch)
                            j = j + 1
                        elif OpDict[i] == 4:
                            j = j + 2
                        elif  OpDict[i] == 12 or OpDict[i] == 13:
                            j = j + 1
                        printFlag = True
                        
except ValueError:
    pprint("Error with line"  + re.sub('\s', ' ', constCheck))
    exit()

    
try:    
    for locJump in AsmLine:
        if locJump.startswith('.code'):
            inCode = True
        elif locJump.startswith('.endcode'):
            inCode = False
            j = 0
        elif inCode:
            for i in jmpTemp:
                if i in locJump:
                    Ri = Ri
except ValueError:
    pprint("Error with line"  + locJump)
    exit()

try:
    for encode in AsmLine:

        if encode.startswith('.code'):
            inCode = True
        elif encode.startswith('.endcode'):
            inCode = False
            j = 0
        elif inCode:
            printFlag = False
            if encode.startswith('@'):
                Ri = Ri
            else:
                try:
                    wordCheck = re.search('([a-zA-Z]+)', encode).group(0)
                except AttributeError:
                    continue
                if wordCheck == 'JMPC' or wordCheck == 'JMPV' or wordCheck == 'JMPZ' or wordCheck == 'JMPN' or wordCheck == 'JMPNC' or wordCheck == 'JMPNV' or wordCheck == 'JMPNZ' or wordCheck == 'JMPNN':
                    wordCheck = 'JMP'
                for i in OpDict:
                    if wordCheck == i and printFlag is False:

                        if OpDict[i] == 0 or OpDict[i] == 1:
                            pprint(OpDict[i])
                            rMatch = re.findall('R\d+|\d+\([rR]\d+\)|-0x[0-9a-fA-F]+|0x[0-9a-fA-F]+', encode)
                            OpCode = '{:04b}'.format(OpDict[i])
                            Rj = '{:05b}'.format(int(re.sub('[rR]', '', rMatch[1])))
                            if re.match('-\d+\(R\d+\)|\d+\(R\d+\)', rMatch[0]):
                                rImatch = re.findall('-\d+|\d+', rMatch[0])
                                Ri = '{:05b}'.format(int(rImatch[1]))
                                pprint('Ri is ' + Ri)
                                if int(Ri, 2) >= 32:
                                    pprint ("Register is too big on line " + re.sub('\s', ' ', encode))
                                    exit()
                                if int(Rj, 2) >= 32:
                                    pprint("Constant is too large in line" + re.sub('\s', ' ', encode))
                                    exit()
                                codeOutIW1 = int(rImatch[0])
                                codeOutIW0 = bin(int(OpCode + Ri + Rj, 2))
                                codeOutIW0 = '{:04x}'.format(int(codeOutIW0, 2))
                                romTemp.append('{:03x}'.format(j) + " : " + codeOutIW0)
                                j = j + 1
                                if codeOutIW1 >= 0:
                                    codeOutIW1 = '{:04x}'.format(codeOutIW1)
                                elif codeOutIW1 < 0:
                                    codeOutIW1 = '{:04x}'.format(((abs(codeOutIW1) ^ 0x3fff) + 1) & 0x3fff )
                                romTemp.append('{:03x}'.format(j) + ' : ' + codeOutIW1)
                            elif re.match('-0x[0-9a-fA-F]+|0x[0-9a-fA-F]+', rMatch[0]):
                                Ri = '{:05b}'.format(0)
                                codeOutIW1 = int(re.sub('0x', '', rMatch[0]),16)
                                codeOutIW0 = bin(int(OpCode + Ri + Rj, 2))
                                codeOutIW0 = '{:04x}'.format(int(codeOutIW0, 2))
                                romTemp.append('{:03x}'.format(j) + " : " + codeOutIW0)
                                j = j + 1
                                if codeOutIW1 >= 0:
                                    codeOutIW1 = '{:04x}'.format(codeOutIW1)
                                romTemp.append('{:03x}'.format(j) + ' : ' + codeOutIW1)
                            j = j + 1
                        elif OpDict[i] == 4:
                            holdVar = re.findall('[a-zA-Z]+', encode)
                            jmpHold = holdVar[0]
                            pprint('I found ' + jmpHold)
                            if holdVar[0] == 'JMP':
                                OpCode = '{:04b}'.format(4)
                                Ri = '{:05b}'.format(0)
                                jmpType = '{:05b}'.format(0)
                                codeOutIW0 = bin(int(OpCode + Ri + jmpType, 2))
                                romTemp.append(hex(j).rjust(5, '0') + " : " + hex(int(codeOutIW0, 2)))
                                j = j + 1
                                if holdVar[1] in jmpTemp:
                                    codeOutIW1 = jmpTemp[holdVar[1]] - j
                                    pprint(codeOutIW1)
                                    if codeOutIW1 > 0:
                                        codeOutIW1 = '{:04x}'.format(codeOutIW1)
                                    elif codeOutIW1 < 0:
                                        codeOutIW1 = '{:04x}'.format(((abs(codeOutIW1-1) ^ 0x3fff) + 1) & 0x3fff )
                                    pprint(codeOutIW1)
                                    romTemp.append('{:03x}'.format(j) + ' : ' + codeOutIW1)
                                    j = j + 1
                                else:
                                    pprint("No such jump exists!")
                            elif holdVar[0] == 'JMPC':
                                OpCode = '{:04b}'.format(4)
                                Ri = '{:05b}'.format(0)
                                jmpType = '{:05b}'.format(16)
                                codeOutIW0 = bin(int(OpCode + Ri + jmpType, 2))
                                romTemp.append('{:03x}'.format(j) + " : " + hex(int(codeOutIW0, 2)))
                                j = j + 1
                                pprint(jmpTemp)
                                if holdVar[1] in jmpTemp:
                                    codeOutIW1 = jmpTemp[holdVar[1]] - j
                                    pprint(codeOutIW1)
                                    if codeOutIW1 > 0:
                                        codeOutIW1 = '{:04x}'.format(codeOutIW1)
                                    elif codeOutIW1 < 0:
                                        codeOutIW1 = '{:04x}'.format(((abs(codeOutIW1-1) ^ 0x3fff) + 1) & 0x3fff )
                                    pprint(codeOutIW1)
                                    romTemp.append('{:03x}'.format(j) + ' : ' + codeOutIW1)
                                    j = j + 1
                                else:
                                    pprint("No such jump exists!")
                            elif holdVar[0] == 'JMPN':
                                OpCode = '{:04b}'.format(4)
                                Ri = '{:05b}'.format(0)
                                jmpType = '{:05b}'.format(8)
                                codeOutIW0 = bin(int(OpCode + Ri + jmpType, 2))
                                romTemp.append('{:03x}'.format(j) + " : " + hex(int(codeOutIW0, 2)))
                                j = j + 1
                                pprint(jmpTemp)
                                if holdVar[1] in jmpTemp:
                                    codeOutIW1 = jmpTemp[holdVar[1]] - j
                                    pprint(codeOutIW1)
                                    if codeOutIW1 > 0:
                                        codeOutIW1 = '{:04x}'.format(codeOutIW1)
                                    elif codeOutIW1 < 0:
                                        codeOutIW1 = '{:04x}'.format(((abs(codeOutIW1-1) ^ 0x3fff) + 1) & 0x3fff )
                                    pprint(codeOutIW1)
                                    romTemp.append('{:03x}'.format(j) + ' : ' + codeOutIW1)
                                    j = j + 1
                                else:
                                    pprint("No such jump exists!")
                            elif holdVar[0] == 'JMPV':
                                OpCode = '{:04b}'.format(4)
                                Ri = '{:05b}'.format(0)
                                jmpType = '{:05b}'.format(4)
                                codeOutIW0 = bin(int(OpCode + Ri + jmpType, 2))
                                romTemp.append('{:03x}'.format(j) + " : " + hex(int(codeOutIW0, 2)))
                                j = j + 1
                                pprint(jmpTemp)
                                if holdVar[1] in jmpTemp:
                                    codeOutIW1 = jmpTemp[holdVar[1]] - j
                                    pprint(codeOutIW1)
                                    if codeOutIW1 > 0:
                                        codeOutIW1 = '{:04x}'.format(codeOutIW1)
                                    elif codeOutIW1 < 0:
                                        codeOutIW1 = '{:04x}'.format(((abs(codeOutIW1-1) ^ 0x3fff) + 1) & 0x3fff )
                                    pprint(codeOutIW1)
                                    romTemp.append('{:03x}'.format(j) + ' : ' + codeOutIW1)
                                    j = j + 1
                                else:
                                    pprint("No such jump exists!")
                            elif holdVar[0] == 'JMPZ':
                                OpCode = '{:04b}'.format(4)
                                Ri = '{:05b}'.format(0)
                                jmpType = '{:05b}'.format(2)
                                codeOutIW0 = bin(int(OpCode + Ri + jmpType, 2))
                                romTemp.append('{:03x}'.format(j) + " : " + hex(int(codeOutIW0, 2)))
                                j = j + 1
                                pprint(jmpTemp)
                                if holdVar[1] in jmpTemp:
                                    codeOutIW1 = jmpTemp[holdVar[1]] - j
                                    pprint(codeOutIW1)
                                    if codeOutIW1 > 0:
                                        codeOutIW1 = '{:04x}'.format(codeOutIW1)
                                    elif codeOutIW1 < 0:
                                        codeOutIW1 = '{:04x}'.format(((abs(codeOutIW1-1) ^ 0x3fff) + 1) & 0x3fff )
                                    pprint(codeOutIW1)
                                    romTemp.append('{:03x}'.format(j) + ' : ' + codeOutIW1)
                                    j = j + 1
                                else:
                                    pprint("No such jump exists!")
                            elif holdVar[0] == 'JMPNC':
                                OpCode = '{:04b}'.format(4)
                                Ri = '{:05b}'.format(0)
                                jmpType = '{:05b}'.format(14)
                                codeOutIW0 = bin(int(OpCode + Ri + jmpType, 2))
                                romTemp.append('{:03x}'.format(j) + " : " + hex(int(codeOutIW0, 2)))
                                j = j + 1
                                pprint(jmpTemp)
                                if holdVar[1] in jmpTemp:
                                    codeOutIW1 = jmpTemp[holdVar[1]] - j
                                    pprint(codeOutIW1)
                                    if codeOutIW1 > 0:
                                        codeOutIW1 = '{:04x}'.format(codeOutIW1)
                                    elif codeOutIW1 < 0:
                                        codeOutIW1 = '{:04x}'.format(((abs(codeOutIW1-1) ^ 0x3fff) + 1) & 0x3fff )
                                    pprint(codeOutIW1)
                                    romTemp.append('{:03x}'.format(j) + ' : ' + codeOutIW1)
                                    j = j + 1
                                else:
                                    pprint("No such jump exists!")
                            elif holdVar[0] == 'JMPNN':
                                OpCode = '{:04b}'.format(4)
                                Ri = '{:05b}'.format(0)
                                jmpType = '{:05b}'.format(22)
                                codeOutIW0 = bin(int(OpCode + Ri + jmpType, 2))
                                romTemp.append('{:03x}'.format(j) + " : " + hex(int(codeOutIW0, 2)))
                                j = j + 1
                                pprint(jmpTemp)
                                if holdVar[1] in jmpTemp:
                                    codeOutIW1 = jmpTemp[holdVar[1]] - j
                                    pprint(codeOutIW1)
                                    if codeOutIW1 > 0:
                                        codeOutIW1 = '{:04x}'.format(codeOutIW1)
                                    elif codeOutIW1 < 0:
                                        codeOutIW1 = '{:04x}'.format(((abs(codeOutIW1-1) ^ 0x3fff) + 1) & 0x3fff )
                                    pprint(codeOutIW1)
                                    romTemp.append('{:03x}'.format(j) + ' : ' + codeOutIW1)
                                    j = j + 1
                                else:
                                    pprint("No such jump exists!")
                            elif holdVar[0] == 'JMPNV':
                                OpCode = '{:04b}'.format(4)
                                Ri = '{:05b}'.format(0)
                                jmpType = '{:05b}'.format(26)
                                codeOutIW0 = bin(int(OpCode + Ri + jmpType, 2))
                                romTemp.append('{:03x}'.format(j) + " : " + hex(int(codeOutIW0, 2)))
                                j = j + 1
                                pprint(jmpTemp)
                                if holdVar[1] in jmpTemp:
                                    codeOutIW1 = jmpTemp[holdVar[1]] - j
                                    pprint(codeOutIW1)
                                    if codeOutIW1 > 0:
                                        codeOutIW1 = '{:04x}'.format(codeOutIW1)
                                    elif codeOutIW1 < 0:
                                        codeOutIW1 = '{:04x}'.format(((abs(codeOutIW1-1) ^ 0x3fff) + 1) & 0x3fff )
                                    pprint(codeOutIW1)
                                    romTemp.append('{:03x}'.format(j) + ' : ' + codeOutIW1)
                                    j = j + 1
                                else:
                                    pprint("No such jump exists!")
                            elif holdVar[0] == 'JMPNZ':
                                OpCode = '{:04b}'.format(4)
                                Ri = '{:05b}'.format(0)
                                jmpType = '{:05b}'.format(28)
                                codeOutIW0 = bin(int(OpCode + Ri + jmpType, 2))
                                romTemp.append('{:03x}'.format(j) + " : " + hex(int(codeOutIW0, 2)))
                                j = j + 1
                                pprint(jmpTemp)
                                if holdVar[1] in jmpTemp:
                                    codeOutIW1 = jmpTemp[holdVar[1]] - j
                                    pprint(codeOutIW1)
                                    if codeOutIW1 > 0:
                                        codeOutIW1 = '{:04x}'.format(codeOutIW1)
                                    elif codeOutIW1 < 0:
                                        codeOutIW1 = '{:04x}'.format(((abs(codeOutIW1-1) ^ 0x3fff) + 1) & 0x3fff )
                                    pprint(codeOutIW1)
                                    romTemp.append('{:03x}'.format(j) + ' : ' + codeOutIW1)
                                    j = j + 1
                                else:
                                    pprint("No such jump exists!")
                        elif OpDict[i] == 3 or OpDict[i] == 2 or OpDict[i] == 5 or OpDict[i] == 6 or OpDict[i] == 10 or OpDict[i] == 11 or OpDict[i] == 14:
                            OpCode = '{:04b}'.format(OpDict[i])
                            rMatch = re.findall('\d+', encode)
                            Ri = '{:05b}'.format(int(re.sub('[rR]', '', rMatch[0])))
                            Rj = '{:05b}'.format(int(rMatch[1], 10))
                            if int(Ri, 2) >= 32:
                                pprint ("Register is out of range on line " + re.sub('\s', ' ', encode))
                                exit()
                            if int(Rj, 2) >= 32:
                                pprint("Register is out of range on line" + re.sub('\s', ' ', encode))
                                exit()
                            codeOutIW0 = bin(int(OpCode + Ri + Rj, 2))
                            romTemp.append('{:03x}'.format(j) + " : " + '{:04x}'.format(int(codeOutIW0, 2)))
                            j = j + 1
                        elif OpDict[i] == 7 or OpDict[i] == 8 or OpDict[i] == 12 or OpDict[i] == 13:
                            rMatch = re.findall('R\d+|\d+\([rR]\d+\)|-0x[0-9a-fA-F]+|0x[0-9a-fA-F]+', encode)
                            OpCode = '{:04b}'.format(OpDict[i])
                            pprint(rMatch)
                            Ri = '{:05b}'.format(int(re.sub('[rR]', '' ,rMatch[0])))
                            Rj = '{:05b}'.format(int(rMatch[1], 16))
                            codeOutIW0 = bin(int(OpCode + Ri + Rj, 2))
                            romTemp.append('{:03x}'.format(j) + " : " + '{:04x}'.format(int(codeOutIW0, 2)))
                            j = j + 1
                        elif OpDict[i] == 9:
                            OpCode = '{:04b}'.format(OpDict[i])
                            Ri = '{:05b}'.format(int(re.search('\d+', encode).group(0)))
                            Rj = '{:05b}'.format(0)
                            codeOutIW0 = bin(int(OpCode + Ri + Rj, 2))
                            romTemp.append('{:03x}'.format(j) + " : " + '{:04x}'.format(int(codeOutIW0, 2)))
                            j = j + 1
                        printFlag = True
except ValueError:
    pprint("Error with line"  + encode)
    exit()
                
for k in range(0, (len(ramTemp)+1)):
    if k < len(ramTemp):
        #ramOut.append('[' + '{:03x}'.format(k) + '..3FF] : 0000')
        ramOut.append(re.sub('0x+', '', ramTemp[k])) 
    elif k == len(ramTemp):
        
        ramOut.append('END')
for k in range(0, (len(romTemp)+1)):
    if k < len(romTemp):
        romOut.append(re.sub('0x+', '', romTemp[k])) 
    elif k == len(romTemp):
        romOut.append('[' + '{:03x}'.format(k) + '..3FF] : 0000')
        romOut.append('END')
with open('ram1.mif', 'w') as ramWrite:
    for l in range(0, len(ramOut)):
        ramWrite.write(ramOut[l].upper() + ';\n')

with open('rom1.mif', 'w') as romWrite:
    for l in range(0, len(romOut)):
        romWrite.write(romOut[l].upper() + ';\n')

pprint(ramTemp)
pprint(romOut)