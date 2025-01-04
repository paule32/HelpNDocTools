%% ---------------------------------------------------------------------------
%% \file    test1.pl
%% \copy    (c) 2024 by paule32 - Jens Kallup
%% \rights  all rights reserved
%%
%% \note    only for education !!!
%% ---------------------------------------------------------------------------

:- dynamic zahl/1.
:- dynamic ist/1.
:- dynamic ein/1.
:- dynamic was/1.

%% ---------------------------------------------------------------------------
%% w-Frage(n) ...
%% ---------------------------------------------------------------------------
warum   :- format('warum   Frage:'), nl.
was     :- format('was     Frage:'), nl.
welche  :- format('welche  Frage:'), nl.
welchem :- format('welchem Frage:'), nl.
welchen :- format('welchen Frage:'), nl.
welcher :- format('welcher Frage:'), nl.
welches :- format('welches Frage:'), nl.
wer     :- format('wer     Frage:'), nl.
weshalb :- format('weshalb Frage:'), nl.
wie     :- format('wie     Frage:'), nl.
wieso   :- format('wieso   Frage:'), nl.
wieviel :- format('wieviel Frage:'), nl.
wo      :- format('wo      Frage:'), nl.
wofür   :- format('wofür   Frage:'), nl.
woher   :- format('woher   Frage:'), nl.
wohin   :- format('wohin   Frage:'), nl.
wollte  :- format('wollte  Frage:'), nl.
womit   :- format('womit   Frage:'), nl.
woran   :- format('woran   Frage:'), nl.
woraus  :- format('woraus  Frage:'), nl.
worin   :- format('worin   Frage:'), nl.
worüber :- format('worüber Frage:'), nl.
wovon   :- format('wovon   Frage:'), nl.
wozu    :- format('wozu    Frage:'), nl.
%% ---------------------------------------------------------------------------
woraus(macht(man(apfelschorle))) :- format('Apfelsaft und Minneralwasser.').
woraus(macht(man(bier)))         :- format('Hopfen und Malz.').
woraus(macht(man(kaffee)))       :- format('Kaffeebohnen und Wasser.').
woraus(macht(man(lakritze)))     :- format('Lakritze wird aus einer Süßholzwurzel.').

womit(macht(man(Kaffee)))        :- format('Kaffeemaschiene, Wasser und Kaffee.').
%% ---------------------------------------------------------------------------
%% mathematische Ziffern ...
%% ---------------------------------------------------------------------------
mathe_text_1(Text1) :- Text1 = 'ist eine mathematische Ziffer.'.
mathe_text_2(Text2) :- Text2 = 'ist eine mathematisches Objekt.'.
mathe_text_3(Text3) :- Text3 = 'ist eine natürliche Zahl.'.

null   :- mathe_text_1(Text1), format('null   ~w', [Text1]), nl,
          mathe_text_2(Text2), format('null   ~w', [Text2]), nl,
          mathe_text_3(Text3), format('null   ~w', [Text3]), nl.

eins   :- mathe_text_1(Text1), format('eins   ~w', [Text1]), nl,
          mathe_text_2(Text2), format('eins   ~w', [Text2]), nl,
          mathe_text_3(Text3), format('eins   ~w', [Text3]), nl.
          
zwei   :- mathe_text_1(Text1), format('zwei   ~w', [Text1]), nl,
          mathe_text_2(Text2), format('zwei   ~w', [Text2]), nl,
          mathe_text_3(Text3), format('zwei   ~w', [Text3]), nl.
          
drei   :- mathe_text_1(Text1), format('drei   ~w', [Text1]), nl,
          mathe_text_2(Text2), format('drei   ~w', [Text2]), nl,
          mathe_text_3(Text3), format('drei   ~w', [Text3]), nl.
          
vier   :- mathe_text_1(Text1), format('vier   ~w', [Text1]), nl,
          mathe_text_2(Text2), format('view   ~w', [Text2]), nl,
          mathe_text_3(Text3), format('vier   ~w', [Text3]), nl.
          
fünf   :- mathe_text_1(Text1), format('fünf   ~w', [Text1]), nl,
          mathe_text_2(Text2), format('fünf   ~w', [Text2]), nl,
          mathe_text_3(Text3), format('fünf   ~w', [Text3]), nl.
          
sechs  :- mathe_text_1(Text1), format('sechs  ~w', [Text1]), nl,
          mathe_text_2(Text2), format('sechs  ~w', [Text2]), nl,
          mathe_text_3(Text3), format('sechs  ~w', [Text3]), nl.
          
sieben :- mathe_text_1(Text1), format('sieben ~w', [Text1]), nl,
          mathe_text_2(Text2), format('sieben ~w', [Text2]), nl,
          mathe_text_3(Text3), format('sieben ~w', [Text3]), nl.
          
acht   :- mathe_text_1(Text1), format('acht   ~w', [Text1]), nl,
          mathe_text_2(Text2), format('acht   ~w', [Text2]), nl,
          mathe_text_3(Text3), format('acht   ~w', [Text3]), nl.
          
neun   :- mathe_text_1(Text1), format('neun   ~w', [Text1]), nl,
          mathe_text_2(Text2), format('neun   ~w', [Text2]), nl,
          mathe_text_3(Text3), format('neun   ~w', [Text3]), nl.

zahl(X) :- X.

was(ist(die(X)))  :- write(X), nl, was, zahl(X).
was(ist(zahl(X))) :- was, zahl(X).
was(ist(X))       :- was(ist(zahl(X))).

?- was(ist(die(neun))), nl.

%% ---------------------------------------------------------------------------
%% Beispiel für eine Anfrage
%% ---------------------------------------------------------------------------
ein(hund) :-
    write('ein Hund ist ein Hund.'), nl ;
    write('ein Hund ist ein Säugetier.'), nl.

?- ein(hund).

ist(ein(hund(ein(säugetier)))) :-
    write('ja, ein Hund ist ein säugetier.'), nl.

?- ist(ein(hund(ein(säugetier)))).

%% ---------------------------------------------------------------------------
%% Skript beenden
%% ---------------------------------------------------------------------------
:- nl, write('Endeü.ü'), nl.
:- halt.
