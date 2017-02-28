; 	ahf's assembly test program.
;------------------------------------------------------------------------------
;	Assembler directives:
;------------------------------------------------------------------------------
;
;
;
	.directives;
	;
	.narray M1 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0;
    .narray M2 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0;
    .narray M3 1000, 1000;
    ;
	.enddirectives;
;------------------------------------------------------------------------------
;	Constant segment:
;------------------------------------------------------------------------------
; These values are initialized in the locations at the end of the code segment.
; For now, .word is the only constant initialization assembly directive.
; After assembling the code, during the final run, the constant name is 
;   replaced with its location address in the program memory.
	.constants;
;
	.word	firstConstWord	0xFFFF;
    .word   secondConstWord 0xEEEE;
	;
	.endconstants;
;------------------------------------------------------------------------------
;	Code segment:
;------------------------------------------------------------------------------
;   first ST/LD var as info, 2nd as storing/loading to register
	.code;
        ADDC    R12, 0xf;
@fillArrOne:
        LD      0x3f00, R1;
        ROTR    R1, 0x5;
        JMPC    fillArrOne;
@debOne:
        LD      0x3f00, R1;
        ST      0(R12), R1;
        ST      0x3f00, R1;
        ROTR    R1, 0x5;
        JMPNC   debOne
        SUBC    R12, 0x1;
        JMPNN   fillArrOne;
        SUB     R12, R12;
        ADDC    R12, 0xf;
@fillArrTwo:
        LD      0x3f00, R1;
        ROTR    R1, 0x5;
        JMPC    fillArrTwo;
@debTwo:
        LD      0x3f00, R1;
        ST      16(R12), R1;
        ST      0x3f00, R1;
        ROTR    R1, 0x5;
        JMPNC   debTwo
        SUBC    R12, 0x1;
        JMPNN   fillArrTwo;
        SUB     R12, R12;
        ADDC    R3, 0xf;
@sendArrOne:
        LD      0(R2), R1;
        ST      0x3f80, R1;
        ADDC    R2, 0x1;
        SUBC    R3, 0x1;
        JMPNN   sendArrOne;
        SUB     R3, R3;
        SUB     R2, R2;
        ADDC    R3, 0xf;
@sendArrTwo:
        LD      16(R2), R1;
        ST      0x3f80, R1;
        ADDC    R2, 0x1;
        SUBC    R3, 0x1;
        JMPNN   sendArrTwo;
        SUB     R3, R3;
        SUB     R2, R2;
        ADDC    R3, 0x3;
@addArrays:
        LD      0(R2), R4;
        LD      16(R2), R5;
        ADD     R4, R5;
        ST      16(R6), R4;
        ADDC    R2, 0x1;
        ADDC    R6, 0x4;
        SUBC    R3, 0x1;
        JMPNN   addArrays;
        SUB     R2, R2;
        SUB     R3, R3;
        ADDC    R3, 0x3;
@receiveResultsSZero:
        LD      0x3f80, R1;
        ST      17(R2), R1;
        ADDC    R2, 0x4;
        SUBC    R3, 0x1;
        JMPNN   receiveResultsSZero;
        SUB     R2, R2;
        SUB     R3, R3
        ADDC    R3, 0x3;
@receiveResultsSOne:
        LD      0x3fa0, R1;
        ST      18(R2), R1;
        ADDC    R2, 0x4;
        SUBC    R3, 0x1;
        JMPNN   receiveResultsSOne;
        SUB     R2, R2;
        SUB     R3, R3;
        ADDC    R3, 0x3;
@receiveResultsSTwo:
        LD      0x3fc0, R1;
        ST      19(R2), R1;
        ADDC    R2, 0x1;
        SUBC    R3, 0x1;
        JMPNN   receiveResultsSTwo;
        SUB     R2, R2;
        SUB     R3, R3;
        ADDC    R3, 0xf;
@display:
        LD      16(R2), R1;
        ST      0x3f00, R1;
        LD      0x20, R10;
@loopTwo:
        LD      0x20, R11;
@loopOne:
        SUBC    R11, 0x1;
        JMPNZ   loopOne
        SUBC    R10, 0x1;
        JMPNZ   loopTwo;
        ADDC    R2, 0x1;
        SUBC    R3, 0x1;
        JMPNN   display;
	.endcode;
