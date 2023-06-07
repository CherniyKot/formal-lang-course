grammar Gram;

prog:   (sentence SEMICOLON)* EOF;

sentence:
                                            #empty
    |   id EQ expr                          #bind
    |   'print' '(' expr ')'                #print
    ;

expr:
        expr '.' operator '(' expr? ')'     #op
    |   expr '.' 'map' '(' lambda ')'       #map
    |   expr '.' 'filter' '(' lambda ')'    #filter
    |   'load' '(' v ')'                    #load
    |   expr '&' expr                       #intersect
    |   expr ':' expr                       #concat
    |   expr '|' expr                       #union
    |   expr '*'                            #star
    |   '<' STRING '>'                      #symb
    |   id                                  #var
    |   v                                   #val
    |   '(' expr ')'                        #par
    |   'set' '(' expr ')'                  #setExpr
    |   'list' '(' expr ')'                  #listExpr
    ;

id      : STRING (INT)*;

v:
        '\'' value=.*? '\''                 #string
    |   INT                                 #int
    |   '[' (v?| v ( ','v)*) ']'            #list
    |   '{' (v?| v ( ','v)*) '}'            #set
    ;


operator:
        'set_final'
    |   'set_start'
    |   'add_start'
    |   'add_final'
    |   'get_start'
    |   'get_final'
    |   'get_reachable'
    |   'get_vertices'
    |   'get_edges'
    |   'get_labels'
    ;

lambda: id '=>' CODE;

CODE: '{{' .*? '}}';

STRING  : [A-Za-z_]+;
WS : [ \t\n\r]+ -> skip;
INT     : [0-9]+ ;

SEMICOLON: ';';
EQ: '=';
