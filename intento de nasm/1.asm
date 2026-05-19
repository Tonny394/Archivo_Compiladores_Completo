;compilar: nasm -f elf hola01.asm
;vincular: ld -m elf_i386 hola01.o -o holamundo01

;ARCHIVO hola01.asm
SECTION .data
	msg db "Hola mundo!", 0Ah ; cadena msg = "Hola Mundo!"

SECTION .text
global _start

_start:
	; Despliegue de cadena en pantalla
	mov edx, 12 	; cantidad de caracteres
	mov ecx, msg 	; ecx = msg dirección de cadena
	mov ebx, 1 	; Escribe al STDOUT_FILE
	mov eax, 4	; Invoca SYS_WRITE
	int 80h

	;Salida al sistema
	mov ebx, 0 	; return 0
	mov eax, 1	; invoca a SYS_EXIT
	int 80h