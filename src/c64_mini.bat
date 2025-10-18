:: 1) leeres D64 mit Name/ID erzeugen
c1541 -format "HELLODISK,01" d64 program.d64 ^
  -attach program.d64 ^
  -write program.prg "HELLO"
