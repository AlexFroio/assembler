; 	ahf's assembly input test program.
;------------------------------------------------------------------------------
;	Assembler directives:
;------------------------------------------------------------------------------
;
;
;
    .directives;
    ;
    .equ   ConstA   0x12;
    .equ   ConstB   0x11;
    ;
    .enddirectives;
;------------------------------------------------------------------------------
;	Constant segment:
;------------------------------------------------------------------------------
    .constants;
    ;
    .word	firstConstWord	0xFFFF;
    .word   secondConstWord 0xEEEE;
	;
	.endconstants;
    
;------------------------------------------------------------------------------
;	Code segment:
;------------------------------------------------------------------------------
    .code;
    ADDC    R1, 0x0F;
    ST      0x3ff0, R1;
    ADDC    R12, 0xA;
@start:
    LD      0x3ff0, R1;
    CPY     R3, R1;
    ROTR    R3, 0x5;
    JMPC    start;
    LD      0x3ff0, R1;
    ST      0(R2), R1;
    ADDC    R2, 0x1;
    ST      0x3ff0, R1;
    CPY     R2, R3;
    SUBC    R3, 0xf;
    JMPN    start;
    .endcode