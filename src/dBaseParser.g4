// ---------------------------------------------------------------------------
// File:   dBaseParser.g4
// Author: (c) 2024, 2025, 2026 Jens Kallup - paule32
// All rights reserved
// ---------------------------------------------------------------------------
parser grammar dBaseParser;
options { tokenVocab=dBaseLexer; }

input
    :   item* EOF
    ;

item
    :   classDecl
    |   methodDecl
    |   statement
    ;

statement
    :   ifStmt
    |   doStmt
    |   breakStmt
    |   parameterStmt
    |   writeStmt
    |   assignStmt
    |   createFileStmt
    |   exprStmt
    |   localAssignStmt
    |   localDeclStmt
    |   callStmt
    |   classDecl
    |   forStmt
    |   doWhileStatement
    |   deleteStmt
    |   returnStmt
    |   withStmt
    ;

createFileStmt
    : CREATE FILE (expr)?
    ;

handlerList
    :   LBRACE expr (SEMI expr)* RBRACE
    ;
    
breakStmt
    : BREAK
    ;

returnStmt
    : RETURN expr?
    ;

doStmt
    :   DO doTarget (WITH argList)?   // WITH ist optional
    ;

doTarget
    :   programRef
    |   IDENT                         // prozedurname
    ;

programRef
    :   IDENT ('.' IDENT)?            // z.B. PROGRAM.PRG (optional: Extension)
    |   PROGRAM IDENT                 // falls du "DO PROGRAM foo" willst
    ;

parameterStmt
    :   PARAMETER paramNames
    ;

paramNames
    :   IDENT (',' IDENT)*
    ;
    
callExpr
    : primary ('.' IDENT)* '(' argList? ')'
    ;

doWhileStatement
    :   DO WHILE condition block ENDDO
    ;

condition
    :   logicalOr
    ;

logicalOr
    :   logicalAnd (OR logicalAnd)*
    ;

logicalAnd
    :   logicalNot (AND logicalNot)*
    ;

logicalNot
    :   NOT logicalNot
    |   comparison
    ;

comparison
    :   additiveExpr (compareOp additiveExpr)?
    ;

compareOp
    :   LT | LE | GT | GE | EQ | NE
    ;

localDeclStmt
    :   LOCAL name=IDENT
    ;

localAssignStmt
    :   LOCAL name=IDENT ASSIGN expr
    ;

deleteStmt
    :   DELETE IDENT
    ;

forStmt
    :   FOR IDENT ASSIGN numberExpr TO numberExpr (STEP numberExpr)? block ENDFOR
    ;

numberExpr
    :   NUMBER
    ;

assignStmt
    :   lvalue ASSIGN expr
    ;

lvalue
    :   postfixExpr
    |   dottedRef
    ;

dottedRef
    :   THIS  (DOT IDENT)+
    |   IDENT (DOT IDENT)*
    ;

exprStmt
    :   postfixExpr
    ;

ifStmt
    :   IF expr block (ELSE block)? ENDIF
    ;

block
    :   statement*     // dadurch beliebig verschachtelbar
    ;
  
writeStmt
    :   WRITE writeArg (PLUS writeArg)*
    ;

writeArg
    :   STRING
    |   dottedRef
    |   expr
    ;
  
// ========= Klassenblock =========
classDecl
    :   CLASS name=IDENT (OF parent=IDENT)? classBody ENDCLASS
    ;

classBody
    :   (classMember | statement)*
    ;

classMember
    :   methodDecl
    |   propertyDecl
    |   assignStmt
    |   withStmt
    ;

withStmt
    :   WITH LPAREN withTarget RPAREN withBody ENDWITH
    ;


withTarget
    :   THIS
    |   dottedRef
    |   IDENT                 // optional: WITH (myObj)
    |   postfixExpr
    ;

withBody
    :   (withAssignStmt | withStmt | statement)*
    ;

withAssignStmt
    :   withLvalue ASSIGN expr
    ;

withLvalue
    :   IDENT (DOT IDENT)*    // relativ: top / caption / pushbutton1.width
    ;
    
propertyDecl
    :   PROPERTY IDENT (ASSIGN expr)?
    ;

methodDecl
    :   METHOD name=IDENT '(' paramList? ')' block ENDMETHOD
    ;

paramList
    :   IDENT (',' IDENT)*
    ;

callStmt
    :   CALL callTarget
    ;

callTarget
    :   (SUPER DCOLON)? IDENT LPAREN argList? RPAREN
    ;

qualifiedName
    :   identifier (DOT identifier)?
    ;

argList
    : expr (COMMA expr)*
    ;

identifier
    :   IDENT
    ;

// ========= Expressions =========
// Präzedenz von hoch nach niedrig:
// 1) Klammern/Atom
// 2) * /
// 3) + -
expr
    :   logicalOr
    ;

additiveExpr
    :   multiplicativeExpr ((PLUS | MINUS) multiplicativeExpr)*
    ;

multiplicativeExpr
    :   postfixExpr ((STAR | SLASH) postfixExpr)*
    ;

// postfixExpr erlaubt Memberzugriff und Calls:
//   THIS.PushButton1
//   Foo(1,2)
//   obj.Method(THIS)
//   (A+B).X
postfixExpr
    :   primary ( LPAREN argList? RPAREN | ( DOT | DCOLON ) IDENT )*
    ;

postfixSuffix
    :   DOT IDENT
    |   LPAREN argList? RPAREN
    ;

newExpr
    :   NEW IDENT '(' argList? ')'
    ;

memberExpr
    :   (THIS | IDENT) ((DOT | DCOLON) IDENT)*
    ;

literal
    :   NUMBER
    |   STRING
    |   TRUE
    |   FALSE
    ;
    
primary
    :   handlerList
    |   newExpr
    |   memberExpr
    |   literal
    |   THIS
    |   SUPER
    |   FLOAT
    |   NUMBER
    |   IDENT
    |   STRING
    |   BRACKET_STRING
    |   LPAREN expr RPAREN
    ;
