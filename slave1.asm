; 	ahf's assembly slave 1 test program.
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
        ADDC    R3, 0xf
@ArrOne:
        LD      0x3f80, R1;
        ST      0(R2), R1;
        ADDC    R2, 0x1;
        SUBC    R3, 0x1;
        JMPNN   ArrOne;
        SUB     R3, R3;
        SUB     R2, R2;
        ADDC    R3, 0xf;
@ArrTwo:
        LD      0x3f80, R1;
        ST      0(R2), R1;
        ADDC    R2, 0x1;
        SUBC    R3, 0x1;
        JMPNN   ArrTwo;
        SUB     R3, R3;
        SUB     R2, R2;
        ADDC    R3, 0x3;
@addArrays:
        LD      8(R2), R4;
        LD      24(R2), R5;
        ADD     R4, R5;
        ST      8(R2), R4;
        ADDC    R2, 0x1;
        SUBC    R3, 0x1;
        JMPNN   addArrays;
        SUB     R3, R3;
        SUB     R2, R2;
        ADDC    R3, 0x3;
@sendAdd:
        LD      8(R2), R1;
        ST      0x3f80, R1;
        ADDC    R2, 0x1;
        SUBC    R3, 0x1;
        JMPNN   sendAdd;
        SUB     R3, R3;
        SUB     R2, R2;
        ADDC    R3, 0xf;
@done:
        ADDC    R1, 0x1;
        JMP     done;
    .endcode;