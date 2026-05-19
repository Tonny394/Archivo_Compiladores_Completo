;
;compilar: nasm -f elf hola02.asm
;vincular: ld -m elf_i386 hola02.o -o holamundo01

SECTION .data
	msg db "Hola mundo con llamada a procedimiento!", 0Ah ; cadena msg = "Hola Mundo!"
global _start

_start:
	mov eax, msg	; ebx = direccion de msg
	call strLen

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


;Calculo de tamaño de cadena
strLen:
	push ebx	; guardar en pila el contenido de ebx
	mov ebx, eax	; ebx = direccion de msg
sigChar:
	cmp byte [eax], 0	; si [eax] == NULL
	jz	finConteo
	inc	eax
	jmp	sigChar
finConteo:
	sub eax, ebx
	pop ebx		;elimina de la pila ebx
	ret