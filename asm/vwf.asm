; Ruin Arm English: variable-width dialogue font, second font bank, relocated message pointers (docs/re/vwf.md).
;
; The printer ($81E195) draws each glyph code into its own 16x16 cell: 4 tiles (TL TR BL BR) in the WRAM buffer
; $7E:8000 + $0CB1, a 2x2 tilemap entry at $7EC844 + $0CB3, $0CB1 += $40, $0CB3 += 4, wrap after 14 cells; the
; frame's cells go to VRAM by DMA at $81E227. Here a glyph is rendered into SCRATCH (by the game's own cell drawer,
; so every code kind works) and ORed into the line at a pixel pen: $0CB1 keeps the cell base in bits 6+ and the pen
; px inside that cell in bits 0-3 (every writer of $0CB1 stores a line base, so px resets to 0 with it). A cell is
; cleared and given its tilemap entries when the pen first enters it. Advance = widths table (codes $0400-$0FFF),
; else 16 px.
lorom

incsrc "../build/vwf/defs.asm"     ; !FONT !MSGTAB (tools/asm.py)

!SCRATCH  = $9F00          ; $7E:9F00: one rendered cell (64 bytes); $7E:9F40 dummy cell for clipped columns
!SCROFS   = $1F00          ; SCRATCH - $8000: the drawer's buffer offset ($02)
!DUMMYOFS = $1F40
!CODE     = $9F80          ; vars, bank $7E ($7E:9000-$9FFF: no write in any tools/lua/wramuse.lua run)
!WIDTH    = $9F82
!PX       = $9F84          ; pen px in the cell at entry
!G        = $9F86
!HI       = $9F88
!LO       = $9F8A
!SH       = $9F8C
!COL0     = $9F8E          ; buffer offsets of the three columns the glyph can touch
!COL1     = $9F90
!COL2     = $9F92
!BASE     = $9F94
!MAP      = $9F96
!START    = $9F98

; ---------------------------------------------------------------- hooks
org $81E1CC                ; printer: glyph code in A (TAX / LDA $0CB1 / STA $02 / JSL $81E929 / tilemap / advance)
	jml vwf_char

org $81E227                ; frame end: PLA saved $0CB1 / PLA saved $0CB9 -> DMA source, VRAM, size
	jml vwf_dma

org $81E8B7                ; message id $0CA4 -> [$0CA7] through the block tables at $838642
	jml msg_ptr

org $81E4B9                ; number control (EE): digit + $00A1 (full-width digits) -> English digits
	adc #$0430

org $81E92E                ; cell drawer: TXA / CMP #$7F00
	jml font_a
org $85EC2D                ; its copy (name entry)
	jml font_b

org $8296F0                ; ruin password: name-entry buffer $140C vs the 8 words at $829711 (build.py: "RAIDROID")
	jml password

; ---------------------------------------------------------------- code
org $D18000

; code $0400-$0FFF (not $07FF) -> draw from the English font banks, else back to the original path. Code c is cell
; i & $3FF of bank FONT + (i >> 10), i = c - $400 (tools/font.py). Entry: A 16-bit, X = code, $02 = buffer offset.
macro font_hook(orig, wram, done)
	txa
	cmp #$7F00
	bcc ?low
	jml <wram>
?low:
	cmp #$0400
	bcc ?jp
	cmp #$07FF
	beq ?jp
	cmp #$1000
	bcc ?f2
?jp:
	jml <orig>
?f2:
	sec
	sbc #$0400
	sta $00
	and #$0007
	asl #4
	sta $04
	lda $00
	and #$03F8
	asl #5
	ora $04
	tay                        ; Y = cell offset in its bank
	lda $00
	lsr #10
	clc
	adc.w #!FONT>>16
	ldx $02                    ; X = buffer offset
	phb
	sep #$20
	pha
	plb                        ; DB = the code's font bank
	rep #$20
	lda #$0007
	sta $04
?row:
	lda $8000,y
	and #$00FF
	sta.l $7E8000,x
	lda $8008,y
	and #$00FF
	sta.l $7E8010,x
	lda $8080,y
	and #$00FF
	sta.l $7E8020,x
	lda $8088,y
	and #$00FF
	sta.l $7E8030,x
	inx
	inx
	iny
	dec $04
	bpl ?row
	jml <done>                 ; PLB, $02 += $40, PLY PLX PLP RTL
endmacro

font_a:
	%font_hook($81E937, $81E9A4, $81E997)
font_b:
	%font_hook($85EC36, $85ECA3, $85EC96)

msg_ptr:                       ; A 16-bit; returns to PLP / CLC / RTS (the PLP restores the flags)
	rep #$30
	lda $0CA4
	and #$1FFF
	sta $00
	asl
	clc
	adc $00
	tax
	lda.l !MSGTAB,x
	sta $0CA7
	lda.l !MSGTAB+1,x
	sta $0CA8
	jml $81E8E1

vwf_dma:                       ; stack: saved $0CB1, saved $0CB9
	pla
	and #$FFC0
	sta.l $7E0000+!START
	pla
	lda $0CB1
	and #$000F
	beq +
	lda #$0040
+	clc
	adc $0CB1
	and #$FFC0
	sec
	sbc.l $7E0000+!START
	beq +
	bpl ++
+	lda #$0040                 ; nothing new: re-send one cell (unchanged data)
++	sta $04
	lda.l $7E0000+!START
	clc
	adc #$8000
	sta $00
	lda.l $7E0000+!START
	lsr
	clc
	adc #$3800
	sta $02
	jml $81E24A

vwf_char:                      ; A = code
	rep #$30
	sta.l $7E0000+!CODE
	tax
	lda #!SCROFS
	sta $02
	jsl $81E929                ; render the cell into SCRATCH
	phb
	sep #$20
	lda #$7E
	pha
	plb
	rep #$20
	lda !CODE
	cmp #$0400
	bcc .w16
	cmp #$1000
	bcs .w16
	tax
	lda.l WIDTHS-$0400,x
	and #$00FF
	bra .wset
.w16:
	lda #$0010
.wset:
	sta !WIDTH
	lda $0CB1
	and #$000F
	sta !PX
	lda $0CB1
	and #$FFC0
	sta !BASE
	lda $0CB3
	sta !MAP
	lda !PX
	bne +
	jsr open_cell              ; pen at the cell's left edge: the cell is new
+	lda !BASE                  ; columns: c0 = px>>3 of this cell, then the next two (cell+1 when past 2)
	sta !COL0
	clc
	adc #$0010
	sta !COL1
	clc
	adc #$0030
	sta !COL2                  ; next cell's left column
	lda !PX
	cmp #$0008
	bcc +
	lda !COL1
	sta !COL0
	lda !COL2
	sta !COL1
	clc
	adc #$0010
	sta !COL2
+	lda !PX                    ; spill into the next cell?
	clc
	adc !WIDTH
	cmp #$0011
	bcc .draw
	lda !MAP
	and #$003F
	cmp #$0034
	bcc .open_next
	lda #!DUMMYOFS             ; last cell of the line: drop what falls past it
	ldx !PX
	cpx #$0008
	bcs +
	sta !COL2
	bra .draw
+	sta !COL1
	sta !COL2
	bra .draw
.open_next:
	lda !BASE
	pha
	lda !MAP
	pha
	clc
	adc #$0004
	sta !MAP
	lda !BASE
	clc
	adc #$0040
	sta !BASE
	jsr open_cell
	pla
	sta !MAP
	pla
	sta !BASE
.draw:
	lda !PX
	and #$0007
	sta !SH
	ldy #$0000
.row:
	lda !SCRATCH,y             ; left byte (TL/BL tile row, plane 0)
	and #$00FF
	xba
	sta !G
	lda !SCRATCH+$10,y         ; right byte (TR/BR)
	and #$00FF
	ora !G
	beq .next
	sta !G
	ldx !SH
-	beq +
	lsr
	dex
	bra -
+	sta !HI
	lda !G
	ldx !SH
-	cpx #$0008
	bcs +
	asl
	inx
	bra -
+	and #$00FF
	sta !LO
	tya
	clc
	adc !COL0
	tax
	sep #$20
	lda !HI+1
	ora $8000,x
	sta $8000,x
	rep #$20
	tya
	clc
	adc !COL1
	tax
	sep #$20
	lda !HI
	ora $8000,x
	sta $8000,x
	rep #$20
	tya
	clc
	adc !COL2
	tax
	sep #$20
	lda !LO
	ora $8000,x
	sta $8000,x
	rep #$20
.next:
	iny
	iny
	cpy #$0010
	bne +
	ldy #$0020                 ; rows 8-15: bottom tiles
+	cpy #$0030
	beq +
	jmp .row
+
	lda $0CB1                  ; advance the pen
	clc
	adc !WIDTH
	sta $0CB1
	and #$0030
	beq .done
	lda $0CB1                  ; past the cell: next cell, px - 16
	clc
	adc #$0030
	sta $0CB1
	lda $0CB3
	clc
	adc #$0004
	sta $0CB3
.done:
	plb
	lda $0CB3
	and #$003F
	cmp #$0038
	bcc +
	jml $81E217                ; line full: the game's own wrap
+	jml $81E21F

open_cell:                     ; clear the cell at BASE, tilemap entries at MAP (DB = $7E)
	ldx !BASE
	ldy #$0020
-	stz $8000,x
	inx
	inx
	dey
	bne -
	lda !BASE
	lsr #4
	clc
	adc #$2100
	ora $0CBD
	ldx !MAP
	sta $C844,x
	inc
	sta $C846,x
	inc
	sta $C884,x
	inc
	sta $C886,x
	rts

password:                      ; the original compare, case-blind: a-z singles ($0461-$047A) count as A-Z. A/X 16-bit.
	ldx #$0000
-	lda $140C,x
	cmp #$0461
	bcc +
	cmp #$047B
	bcs +
	sbc #$001F                 ; carry clear here: subtracts $20
+	cmp $829711,x
	bne ++
	inx
	inx
	cpx #$0010
	bcc -
	lda #$0018                 ; match
	bra +
++	lda #$0008
+	sta $1816
	rtl

WIDTHS:
	incbin "../build/vwf/widths.bin"
assert pc() <= $D1FFFF
