## Структура языка описана ниже в формате ANTLR

    grammar Gram;

    prog:   (expr SEMICOLON)* EOF;

    expr:
                                                #empty
        |   id EQ (expr)                        #bind
        |   id '.' operator '(' expr? ')'       #op
        |   'print' '(' expr ')'                #print
        |   expr '.' 'map' '(' lambda ')'       #map
        |   'load' '(' PATH ')'                 #load
        |   expr '&' expr                       #intersect
        |   expr ':' expr                       #concat
        |   expr '|' expr                       #union
        |   '*' expr                            #star
        |   expr '++'                           #move
        |   id                                  #var
        |   v                                   #val
        ;

    id      : STRING (INT)*;

    v:
            '\'' value=.*? '\''                 #string
        |   INT                                 #int
        |   '[' id* ']'                         #set
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
    PATH: [-a-zA-Z0-9@:%._+~#=]{1,256}'.'[a-zA-Z0-9()]{1,6} '\b' ([-a-zA-Z0-9()@:%_+.~#?&/=]*) ;

### Примеры кода:
1. Загружает граф и выводит его ноды и ребра

        g=load('vk.ru/graph');
        print(g.get_labels());
        print(g.get_edges());
2. Загружает два графа и печатает их пересечение по ребрам и вершинам

        g1=load('vk.ru/graph');
        g2=load('vk.com/graph');
        g = g1 & g2;
        print(g);
