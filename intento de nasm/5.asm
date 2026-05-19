 ;compilar: nasm -f elf hola04.asm
;vincular: ld -m elf_i386 hola04.o -o holamundo04

%include	'stdio32.asm'

SECTION .data
	msg1 db "Hola mundo con archivo de cabecera!", 0Ah ; cadena msg = "Hola Mundo!"
	msg2 db "¿Quien encuentra el error?", 0 ; cadena msg = "Hola Mundo!"
	msg3 db "Esta cadena en la nueva linea", 0 
SECTION .text
global _start

_start:
	;----------------------printStr(msg)-----------
	mov eax, msg1
	call printStr

	mov eax, msg2
	call printStr

	mov eax, msg3
	call pirntStrLn

	call quit