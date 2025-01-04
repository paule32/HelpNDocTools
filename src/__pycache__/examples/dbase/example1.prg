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

@ 321 , 2 say "hello"  +/* comment between */ "xxx" + "ssss"
  + // ****
 /* command */ "111"+
"aaaa"
