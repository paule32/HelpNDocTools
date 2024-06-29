** This is a one line dBase comment
&& This is a one line dBase comment, too
// This is a one line C++ comment, that is valid in dBase, too

/* This is the begin of a common C block comment
 * it can contain
   multiple
 * lines in source codes
 */
 
    && xxxxxxx

/*
  the following command:  clean all
  will not execute, because it stands in a C comment block.

      */   /* dsfsdf */  clear /* comments can nearly 
      
      dfdfdf  stand overall places.
      The two commands "clear screen" between the comments will
      be execute, because they stand outside of a comment scope.
      
        */
        screen
        clear
    
    @ 1,  4 say date()
    @ 1, 54 say "My Company INTERNATIONAL, Inc." + "  \"\\mumu"
    @ 3,  1 say date()

   