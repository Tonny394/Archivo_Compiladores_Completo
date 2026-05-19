;
;compilar: nasm -f elf hola02.asm
;vincular: ld -m elf_i386 hola02.o -o holamundo01

SECTION .data
	msg db "Hola mundo version 2!", 0Ah ; cadena msg = "Hola Mundo!"

SECTION .text
global _start

_start:
	;Calculo de tamaño de cadena
	mov ebx, msg	; ebx = direccion de msg
	mov eax, ebx	; eax = ebx

sigChar:
	cmp byte [eax], 0	; si [eax] == NULL
	jz	finConteo
	inc	eax
	jmp	sigChar
finConteo:
	sub eax, ebx

	; Despliegue de cadena en pantalla
	mov edx, eax 	; cantidad de caracteres
	mov ecx, msg 	; ecx = msg dirección de cadena
	mov ebx, 1 	; Escribe al STDOUT_FILE
	mov eax, 4	; Invoca SYS_WRITE
	int 80h

	;Salida al sistema
	mov ebx, 0 	; return 0
	mov eax, 1	; invoca a SYS_EXIT
	int 80h