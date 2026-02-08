// ---------------------------------------------------------------------------
// File:   dBaseLexer.g4
// Author: (c) 2024, 2025, 2026 Jens Kallup - paule32
// All rights reserved
// ---------------------------------------------------------------------------
lexer grammar dBaseLexer;

PARAMETER   : [pP][aA][rR][aA][mM][eE][tT][eE][rR];
WITH        : [wW][iI][tT][hH];
ENDWITH     : [eE][nN][dD][wW][iI][tT][hH];
PROGRAM     : [pP][rR][oO][gG][rR][aA][mM];

RETURN      : [rR][eE][tT][uU][rR][nN];

FOR         : [fF][oO][rR];
TO          : [tT][oO];
ENDFOR      : [eE][nN][dD][fF][oO][rR];
STEP        : [sS][tT][eE][pP];

BREAK       : [bB][rR][eE][aA][kK];

DO          : [dD][oO];
WHILE       : [wW][hH][iI][lL][eE];
ENDDO       : [eE][nN][dD][dD][oO];

LOCAL       : [lL][oO][cC][aA][lL];
NEW         : [nN][eE][wW];
DELETE      : [dD][eE][lL][eE][tT][eE];

SUPER       : [sS][uU][pP][eE][rR];
CLASS       : [cC][lL][aA][sS][sS];
ENDCLASS    : [eE][nN][dD][cC][lL][aA][sS][sS];
OF          : [oO][fF];

THIS        : [tT][hH][iI][sS];

METHOD      : [mM][eE][tT][hH][oO][dD];
ENDMETHOD   : [eE][nN][dD][mM][eE][tT][hH][oO][dD];
PROPERTY    : [pP][rR][oO][pP][eE][rR][tT][yY];

CREATE      : [cC][rR][eE][aA][tT][eE];
FILE        : [fF][iI][lL][eE];

IF          : [iI][fF];
ELSE        : [eE][lL][sS][eE];
ENDIF       : [eE][nN][dD][iI][fF];

WRITE       : [wW][rR][iI][tT][eE];

CALL        : [cC][aA][lL][lL];

COMMA       : ',';
DOT         : '.';

FLOAT       : [0-9]+'.'[0-9]+;
NUMBER      : [0-9]+;

STRING
            : DQ_STRING
            | SQ_STRING
            ;

fragment DQ_STRING
    : '"' ( ESC | ~["\\\r\n] )* '"'
    ;

fragment SQ_STRING
    : '\'' ( ESC | ~['\\\r\n] )* '\''
    ;

fragment ESC
    : '\\' .
    ;

LE          : '<=';
GE          : '>=';
NE          : '!=';
EQ          : '==';

LT          : '<';
GT          : '>';

DCOLON      : '::';
COLON       : ':' ;

ASSIGN      : '=';

LPAREN      : '(';
RPAREN      : ')';
PLUS        : '+';
MINUS       : '-';
STAR        : '*';
SLASH       : '/';

LBRACE      : '{' ;
RBRACE      : '}' ;
SEMI        : ';' ;

BRACKET_STRING
            : '[' ( ']]' | ~']' )* ']'   // ']]' bedeutet ein echtes ']' im Text
            ;

TRUE        : '.T.' | '.t.';
FALSE       : '.F.' | '.f.';

AND         : '.' [aA][nN][dD] '.';
OR          : '.' [oO][rR] '.';
NOT         : '.' [nN][oO][tT] '.';

IDENT       : [a-zA-Z_][a-zA-Z0-9_]*;

// Whitespace / Comments
WS              : [ \t\r\n]+ -> skip;

LINECOMMENT_DBA : '**' ~[\r\n]* -> skip;
LINECOMMENT_DBB : '&&' ~[\r\n]* -> skip;
LINECOMMENT_CPP : '//' ~[\r\n]* -> skip;

BLOCKCOMMENT_START
    : '/*' { self._cmtDepth = getattr(self, "_cmtDepth", 0) + 1 } -> pushMode(COMMENT), skip
    ;

// ---------- COMMENT mode (verschachtelbar) ----------
mode COMMENT;

COMMENT_NEST_START  : '/*' { self._cmtDepth += 1 } -> pushMode(COMMENT), skip;
COMMENT_END         : '*/' { self._cmtDepth -= 1 } -> popMode, skip;
COMMENT_ANY         : . -> skip ;
