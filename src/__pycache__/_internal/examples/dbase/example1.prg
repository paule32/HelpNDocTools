
/* \file   example1.prg
 * \author Jens Kallup - paule32
 * \copy   (c) 2024 all rights reserved.
 *
 * \brief  This file demonstrate some possibilities of the compiler.
 *         It cover not all, and bugs can be included.
 *
 *         YOU USE ALL OF THEM AT YOUR OWN RISK WITHOUT GURANTEES FROM
 *         THE AUTHORS !
 *
 * \note   This are multiline comment block(s).
 */

** \brief  two asterisk's  marks a one-line comment (dBase extra).
&& \brief  two ampersign's marks a one-line comment, too (dBase extra)
// \brief  two slash's     marks a one-line C++ like comment

//set color to w+/b+
//variable = "zuzu" ? "123 " + "ssss"+" BNM"

@ 3 , 2 say "hello"  +/* comment between */ "xxx" + "ssss"
  + // ****
 /* command */ "111"+
"aaaa"
set color to w/b+
@5,5 say"gugu"+"jaja"
kopo = 12

set color to g+/w
@ 34, 12 say "gug"

set color to n/w
@ 38, 12 say "Looop" + " : : "

//fufu = (21+(45))+22

//y = 10

//@ y+12 , y say "GUGU"

/*for y = 1 to 4
  @ 1, y say "GAGA"
  @ (10+5-(3))-(1+3), (y+1-(+2)) say "zuzu"
  for x = 1 to 2
    @ 10, x say "lolo"
  next
  @ 20, 10 say "harry"
next*/
