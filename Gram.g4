grammar Gram;

prog:   (expr SEMICOLON)* EOF;

expr:
                                            #empty
    |   id EQ (expr)                        #bind
    |   id '.' operator '(' expr? ')'       #op
    |   'print' '(' expr ')'                #print
    |   expr '.' 'map' '(' lambda ')'       #map
    |   'load' '(' v ')'                    #load
    |   expr '&' expr                       #intersect
    |   expr ':' expr                       #concat
    |   expr '|' expr                       #union
    |   expr '*'                            #star
    |   '<' STRING '>'                      #symb
    |   id                                  #var
    |   v                                   #val
    ;

id      : STRING (INT)*;

v:
        '\'' value=.*? '\''                 #string
    |   INT                                 #int
    |   '[' (v?| v ( ','v)*) ']'            #set
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

lambda: var=id '=>' code;

code: '{{' .*? '}}';

STRING  : [A-Za-z_]+;
WS : [ \t\n\r]+ -> skip;
INT     : [0-9]+ ;

SEMICOLON: ';';
EQ: '=';
