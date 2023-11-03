# REX - simple Ruby lexer

**Содержание:**
<!-- TOC -->
* [REX - simple Ruby lexer](#rex---simple-ruby-lexer)
* [Оптимизация транслируемого кода](#оптимизация-транслируемого-кода)
* [Тесты](#тесты)
  * [Лексер](#лексер)
    * [1. numberOperators](#1-numberoperators)
    * [2. numberTokens](#2-numbertokens)
    * [3. keywordTokens](#3-keywordtokens)
    * [4. bracketsTokens](#4-bracketstokens)
    * [5. logicalOperators](#5-logicaloperators)
    * [6. specialTokens](#6-specialtokens)
    * [7. ignoreWhitespace](#7-ignorewhitespace)
    * [8. emptyInput](#8-emptyinput)
    * [9. complexCode](#9-complexcode)
    * [10. tokensPositioning](#10-tokenspositioning)
    * [11. Тесты на выявление ошибок](#11-тесты-на-выявление-ошибок)
<!-- TOC -->

# Оптимизация транслируемого кода
В процессе трансляции, Rex выполняет следующие оптимизации кода:
1. Примитивы в математических выражениях вычисляются на этапе трансляции. Например, `3 * 2 - 4` заменяется на `2`
2. Повторяющиеся унарные операции упрощаются. Например, `--1` заменяется на `1`, а `---1` на `-1`
3. 
4. Все операции, расположенные после `return` - игнорируются и не выводятся в транслируемый код. Если на верхнем уровне встречен оператор `return`, то процесс парсинга завершается, т.к. нижеследующие операторы уже не имеют смысла.
5. Содержимое `return` верхнего уровня - игнорируется, т.к. не имеет смысла.

# Тесты
## Лексер

### 1. numberOperators

Задача теста, проверить, что лексер правильно распознает токены числовых операторов.

В качестве входных данных рассматривается следующий код на языке Ruby:

```
x = 10 + 5 - 5 * 2 / 2 % 10
x += 1
x -= 1
x *= 1
x /= 1
x %= 1
```

|     **Входные данные**      |                                                                                                                               **Выходные данные**                                                                                                                               |                                                                                                                              **Ожидаемые данные**                                                                                                                               |
|:---------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| x = 10 + 5 - 5 * 2 / 2 % 10 | Special.ID<br> Operators.EQUALS<br> Special.INTEGER<br> Operators.PLUS<br> Special.INTEGER<br> Operators.MINUS<br> Special.INTEGER<br> Operators.ASTERISK<br> Special.INTEGER<br> Operators.SLASH<br> Special.INTEGER<br> Operators.MOD<br> Special.INTEGER<br> Special.NEWLINE | Special.ID<br> Operators.EQUALS<br> Special.INTEGER<br> Operators.PLUS<br> Special.INTEGER<br> Operators.MINUS<br> Special.INTEGER<br> Operators.ASTERISK<br> Special.INTEGER<br> Operators.SLASH<br> Special.INTEGER<br> Operators.MOD<br> Special.INTEGER<br> Special.NEWLINE |
|           x += 1            |                                                                                                  Special.ID<br> Operators.PLUS_EQUALS<br> Special.INTEGER<br> Special.NEWLINE                                                                                                   |                                                                                                  Special.ID<br> Operators.PLUS_EQUALS<br> Special.INTEGER<br> Special.NEWLINE                                                                                                   |
|           x -= 1            |                                                                                                  Special.ID<br> Operators.MINUS_EQUALS<br> Special.INTEGER<br> Special.NEWLINE                                                                                                  |                                                                                                  Special.ID<br> Operators.MINUS_EQUALS<br> Special.INTEGER<br> Special.NEWLINE                                                                                                  |
|           x *= 1            |                                                                                                 Special.ID<br> Special.ASTERISK_EQUALS<br> Special.INTEGER<br> Special.NEWLINE                                                                                                  |                                                                                                 Special.ID<br> Special.ASTERISK_EQUALS<br> Special.INTEGER<br> Special.NEWLINE                                                                                                  |
|           x /= 1            |                                                                                                  Special.ID<br> Operators.SLASH_EQUALS<br> Special.INTEGER<br> Special.NEWLINE                                                                                                  |                                                                                                  Special.ID<br> Operators.SLASH_EQUALS<br> Special.INTEGER<br> Special.NEWLINE                                                                                                  |
|           x %= 1            |                                                                                                             Special.ID<br> Operators.MOD_EQUALS<br> Special.INTEGER                                                                                                             |                                                                                                             Special.ID<br> Operators.MOD_EQUALS<br> Special.INTEGER                                                                                                             |
|         End Of File         |                                                                                                                                   Special.EOF                                                                                                                                   |                                                                                                                                   Special.EOF                                                                                                                                   |

### 2. numberTokens

Задача теста, проверить, что лексер правильно распознает токены и значения чисел.

В качестве входных данных рассматривается следующий код на языке Ruby:

```
0
1
10
100
0.1
0.01e4
-100
```

| Входные данные |               Выходные данные                |               Ожидаемые данные               |
|:--------------:|:--------------------------------------------:|:--------------------------------------------:|
|       0        |  (Special.INTEGER, '0')<br>Special.NEWLINE   |  (Special.INTEGER, '0')<br>Special.NEWLINE   |
|       1        |  (Special.INTEGER, '1')<br>Special.NEWLINE   |  (Special.INTEGER, '1')<br>Special.NEWLINE   |
|       10       |  (Special.INTEGER, '10')<br>Special.NEWLINE  |  (Special.INTEGER, '10')<br>Special.NEWLINE  |
|      100       | (Special.INTEGER, '100')<br>Special.NEWLINE  | (Special.INTEGER, '100')<br>Special.NEWLINE  |
|      0.1       |  (Special.FLOAT, '0.1')<br>Special.NEWLINE   |  (Special.FLOAT, '0.1')<br>Special.NEWLINE   |
|     0.01e4     | (Special.FLOAT, '0.01e4')<br>Special.NEWLINE | (Special.FLOAT, '0.01e4')<br>Special.NEWLINE |
|      -100      | Operators.MINUS<br>(Special.INTEGER, '100')  | Operators.MINUS<br>(Special.INTEGER, '100')  |
|  End Of File   |                 Special.EOF                  |                 Special.EOF                  |

### 3. keywordTokens

Задача теста, проверить, что лексер правильно распознает токены ключевых слов языка Ruby.

В качестве входных данных рассматривается следующий код на языке Ruby:

```
def return end while do for until next break if elsif else in case when or and not true false nil
```

| Входные данные |  Выходные данные  | Ожидаемые данные  |
|:--------------:|:-----------------:|:-----------------:|
|      def       | KeyWords.FUNCTION | KeyWords.FUNCTION |
|     return     |  KeyWords.RETURN  |  KeyWords.RETURN  |
|      end       |   KeyWords.END    |   KeyWords.END    |
|     while      |  KeyWords.WHILE   |  KeyWords.WHILE   |
|       do       |    KeyWords.DO    |    KeyWords.DO    |
|      for       |   KeyWords.FOR    |   KeyWords.FOR    |
|     until      |  KeyWords.UNTIL   |  KeyWords.UNTIL   |
|      next      |   KeyWords.NEXT   |   KeyWords.NEXT   |
|     break      |  KeyWords.BREAK   |  KeyWords.BREAK   |
|       if       |    KeyWords.IF    |    KeyWords.IF    |
|     elsif      |  KeyWords.ELSIF   |  KeyWords.ELSIF   |
|      else      |   KeyWords.ELSE   |   KeyWords.ELSE   |
|       in       |    KeyWords.IN    |    KeyWords.IN    |
|      case      |   KeyWords.CASE   |   KeyWords.CASE   |
|      when      |   KeyWords.WHEN   |   KeyWords.WHEN   |
|       or       |    KeyWords.OR    |    KeyWords.OR    |
|      and       |   KeyWords.AND    |   KeyWords.AND    |
|      not       |   KeyWords.NOT    |   KeyWords.NOT    |
|      true      |   Reserved.TRUE   |   Reserved.TRUE   |
|     false      |  Reserved.FALSE   |  Reserved.FALSE   |
|      nil       |   Reserved.NIL    |   Reserved.NIL    |
|  End Of File   |    Special.EOF    |    Special.EOF    |

### 4. bracketsTokens
Задача теста, проверить, что лексер правильно распознает токены скобок языка Ruby.

В качестве входных данных рассматривается следующий код на языке Ruby:

```
( ) [ ] { }\
```

| Входные данные |                                                     Выходные данные                                                      |                                                     Ожидаемые данные                                                     |
|:--------------:|:------------------------------------------------------------------------------------------------------------------------:|:------------------------------------------------------------------------------------------------------------------------:|
|  ( ) [ ] { }   | Special.LPAR<br>Special.RPAR<br>Special.LBR<br>Special.RBR<br>Special.LFBR<br>Special.RFBR<br>Special.VBR<br>Special.EOF | Special.LPAR<br>Special.RPAR<br>Special.LBR<br>Special.RBR<br>Special.LFBR<br>Special.RFBR<br>Special.VBR<br>Special.EOF |
### 5. logicalOperators
Задача теста, проверить, что лексер правильно распознает токены логических операторов и операторов сравнения языка Ruby.

В качестве входных данных рассматривается следующий код на языке Ruby:

```
< > <= >= == != and or not\
```

|       Входные данные       |                                                                                             Выходные данные                                                                                             |                                                                                            Ожидаемые данные                                                                                             |
|:--------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| < > <= >= == != and or not | Operators.LESS<br>Operators.GREATER<br>Operators.LESS_EQUAL<br>Operators.GREATER_EQUAL<br>Operators.DOUBLE_EQUALS<br>Operators.NOT_EQUALS<br>KeyWords.AND<br>KeyWords.OR<br>KeyWords.NOT<br>Special.EOF | Operators.LESS<br>Operators.GREATER<br>Operators.LESS_EQUAL<br>Operators.GREATER_EQUAL<br>Operators.DOUBLE_EQUALS<br>Operators.NOT_EQUALS<br>KeyWords.AND<br>KeyWords.OR<br>KeyWords.NOT<br>Special.EOF |
### 6. specialTokens
Задача теста, проверить, что лексер правильно распознает токены специальных символов языка Ruby (запятые, точки и т.п).

В качестве входных данных рассматривается следующий код на языке Ruby:

```
, .. ; .\
```

| Входные данные |                                    Выходные данные                                     |                                    Ожидаемые данные                                    |
|:--------------:|:--------------------------------------------------------------------------------------:|:--------------------------------------------------------------------------------------:|
|    , .. ; .    | Special.COMMA<br>Special.DOUBLE_DOT<br>Special.SEMICOLON<br>Special.DOT<br>Special.EOF | Special.COMMA<br>Special.DOUBLE_DOT<br>Special.SEMICOLON<br>Special.DOT<br>Special.EOF |

### 7. ignoreWhitespace
Задача теста, проверить, что лексер правильно распознает токены скобок языка Ruby.

В качестве входных данных рассматривается следующий код на языке Ruby:

```
\t           \t        
         \t  
```

| Входные данные |                  Выходные данные                  |                 Ожидаемые данные                  |
|:--------------:|:-------------------------------------------------:|:-------------------------------------------------:|
|    Код выше    | Special.NEWLINE<br>Special.NEWLINE<br>Special.EOF | Special.NEWLINE<br>Special.NEWLINE<br>Special.EOF |
### 8. emptyInput
Задача теста, проверить, что лексер правильно распознает токены скобок языка Ruby.

В качестве входных данных рассматривается следующий код на языке Ruby:

```
-
```

| Входные данные | Выходные данные | Ожидаемые данные |
|:--------------:|:---------------:|:----------------:|
|       -        |   Special.EOF   |   Special.EOF    |


### 9. complexCode
Задача теста, проверить, что лексер правильно распознает токены сложных конструкций языка Ruby.

В качестве входных данных рассматривается следующий код на языке Ruby:

```
hello = "Hello, world!"
# Define a method
def self.say_hello
    puts hello
end

x = 5
if x > 10
  puts "x is greater than 10"
elsif x > 5
  puts "x is greater than 5 but less than or equal to 10"
else
  puts "x is less than or equal to 5"
end

my_array = [1, 2, 3, 4, 5]
puts my_array.sum
```
Рассмотрим результаты работы лексера построчно.

|                     Входные данные                      |                                                                                                            Выходные данные                                                                                                             |                                                                                                            Ожидаемые данные                                                                                                            |
|:-------------------------------------------------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|                 hello = "Hello, world!"                 |                                                                                  ID:hello:1:1<br>EQUALS:1:7<br>STR:Hello, world!:1:9<br>NEWLINE:1:24                                                                                   |                                                                                  ID:hello:1:1<br>EQUALS:1:7<br>STR:Hello, world!:1:9<br>NEWLINE:1:24                                                                                   |
|                    # Define a method                    |                                                                                                            <br>NEWLINE:2:18                                                                                                            |                                                                                                            <br>NEWLINE:2:18                                                                                                            |
|                   def self.say_hello                    |                                                                              FUNCTION:3:1<br>ID:self:3:5<br>DOT:3:9<br>ID:say_hello:3:10<br>NEWLINE:3:19                                                                               |                                                                              FUNCTION:3:1<br>ID:self:3:5<br>DOT:3:9<br>ID:say_hello:3:10<br>NEWLINE:3:19                                                                               |
|                       puts hello                        |                                                                                              ID:puts:4:5<br>ID:hello:4:10<br>NEWLINE:4:15                                                                                              |                                                                                              ID:puts:4:5<br>ID:hello:4:10<br>NEWLINE:4:15                                                                                              |
|                           end                           |                                                                                                         END:5:1<br>NEWLINE:5:4                                                                                                         |                                                                                                         END:5:1<br>NEWLINE:5:4                                                                                                         |
|                           \n                            |                                                                                                              NEWLINE:6:1                                                                                                               |                                                                                                              NEWLINE:6:1                                                                                                               |
|                          x = 5                          |                                                                                        ID:\x:7:1<br>EQUALS:7:3<br>INTEGER:5:7:5<br>NEWLINE:7:6                                                                                         |                                                                                        ID:\x:7:1<br>EQUALS:7:3<br>INTEGER:5:7:5<br>NEWLINE:7:6                                                                                         |
|                        if x > 10                        |                                                                                  IF:8:1<br>ID:\x:8:4<br>GREATER:8:6<br>INTEGER:10:8:8<br>NEWLINE:8:10                                                                                  |                                                                                  IF:8:1<br>ID:\x:8:4<br>GREATER:8:6<br>INTEGER:10:8:8<br>NEWLINE:8:10                                                                                  |
|               puts "x is greater than 10"               |                                                                                      ID:puts:9:3<br>STR:x is greater than 10:9:8<br>NEWLINE:9:30                                                                                       |                                                                                      ID:puts:9:3<br>STR:x is greater than 10:9:8<br>NEWLINE:9:30                                                                                       |
|                       elsif x > 5                       |                                                                              ELSIF:10:1<br>ID:\x:10:7<br>GREATER:10:9<br>INTEGER:5:10:11<br>NEWLINE:10:12                                                                              |                                                                              ELSIF:10:1<br>ID:\x:10:7<br>GREATER:10:9<br>INTEGER:5:10:11<br>NEWLINE:10:12                                                                              |
| puts "x is greater than 5 but less than or equal to 10" |                                                                       ID:puts:11:3<br>STR:x is greater than 5 but less than or equal to 10:11:8<br>NEWLINE:11:58                                                                       |                                                                       ID:puts:11:3<br>STR:x is greater than 5 but less than or equal to 10:11:8<br>NEWLINE:11:58                                                                       |
|                          else                           |                                                                                                       ELSE:12:1<br>NEWLINE:12:5                                                                                                        |                                                                                                       ELSE:12:1<br>NEWLINE:12:5                                                                                                        |
|           puts "x is less than or equal to 5"           |                                                                                 ID:puts:13:3<br>STR:x is less than or equal to 5:13:8<br>NEWLINE:13:38                                                                                 |                                                                                 ID:puts:13:3<br>STR:x is less than or equal to 5:13:8<br>NEWLINE:13:38                                                                                 |
|                           end                           |                                                                                                        END:14:1<br>NEWLINE:14:4                                                                                                        |                                                                                                        END:14:1<br>NEWLINE:14:4                                                                                                        |
|                           \n                            |                                                                                                              NEWLINE:15:1                                                                                                              |                                                                                                              NEWLINE:15:1                                                                                                              |
|               my_array = [1, 2, 3, 4, 5]                | ID:my_array:16:1<br>EQUALS:16:10<br>LBR:16:12<br>INTEGER:1:16:13<br>COMMA:16:14<br>INTEGER:2:16:16<br>COMMA:16:17<br>INTEGER:3:16:19<br>COMMA:16:20<br>INTEGER:4:16:22<br>COMMA:16:23<br>INTEGER:5:16:25<br>RBR:16:26<br>NEWLINE:16:27 | ID:my_array:16:1<br>EQUALS:16:10<br>LBR:16:12<br>INTEGER:1:16:13<br>COMMA:16:14<br>INTEGER:2:16:16<br>COMMA:16:17<br>INTEGER:3:16:19<br>COMMA:16:20<br>INTEGER:4:16:22<br>COMMA:16:23<br>INTEGER:5:16:25<br>RBR:16:26<br>NEWLINE:16:27 |
|                    puts my_array.sum                    |                                                                             ID:puts:17:1<br>ID:my_array:17:6<br>DOT:17:14<br>ID:sum:17:15<br>NEWLINE:17:18                                                                             |                                                                             ID:puts:17:1<br>ID:my_array:17:6<br>DOT:17:14<br>ID:sum:17:15<br>NEWLINE:17:18                                                                             |
|                       End Of File                       |                                                                                                                EOF:18:1                                                                                                                |                                                                                                                EOF:18:1                                                                                                                |

### 10. tokensPositioning
Задача теста, проверить, что лексер правильно распознает позиции токенов в коде языка Ruby.

В качестве входных данных рассматривается следующий код на языке Ruby:

```
my_array = [1, 2, 3, 4, 5]
puts my_array.sum\
```

|       Входные данные       |                                                                    Выходные данные                                                                    |                                                                   Ожидаемые данные                                                                    |
|:--------------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------:|
| my_array = [1, 2, 3, 4, 5] | (1, 1)<br>(1, 10)<br>(1, 12)<br>(1, 13)<br>(1, 14)<br>(1, 16)<br>(1, 17)<br>(1, 19)<br>(1, 20)<br>(1, 22)<br>(1, 23)<br>(1, 25)<br>(1, 26)<br>(1, 27) | (1, 1)<br>(1, 10)<br>(1, 12)<br>(1, 13)<br>(1, 14)<br>(1, 16)<br>(1, 17)<br>(1, 19)<br>(1, 20)<br>(1, 22)<br>(1, 23)<br>(1, 25)<br>(1, 26)<br>(1, 27) |
|     puts my_array.sum      |                                                   (2, 1)<br>(2, 6)<br>(2, 14)<br>(2, 15)<br>(2, 18)                                                   |                                                   (2, 1)<br>(2, 6)<br>(2, 14)<br>(2, 15)<br>(2, 18)                                                   |
|        End Of File         |                                                                        (3, 1)                                                                         |                                                                        (3, 1)                                                                         |

### 11. Тесты на выявление ошибок
Задача теста, выявить потенциальные ошибки лексера, так как входные данные в этом тесте являются некорректными и лексер должен обрабатывать их выдавая соответствующие ошибки.  

В качестве входных данных рассматривается следующий код на языке Ruby:

```
1.1.1
1abvgd
000111
000000000
```
До правок в программу результаты её работы были следующие:

| Входные данные |         Выходные данные         |         Ожидаемые данные         |
|:--------------:|:-------------------------------:|:--------------------------------:|
|     1.1.1      | FLOAT:1.1<br>DOT:1<br>INTEGER:1 |   Incorrect number token: 1.1.   |
|     1abvgd     |   Incorrect number token: 1a    |    Incorrect number token: 1a    |
|     000111     |       INTEGER:000111:3:1        |  Incorrect number token:000111   |
|   000000000    |      INTEGER:000000000:4:1      | Incorrect number token:000000000 |

Как можно видеть, часть неправильных конструкций кода лексер обработал правильно, а другая часть не была учтена при реализации.
После выявление ошибок и внесения соответствующих правок, результат работы стал следующим:

| Входные данные |         Выходные данные          |         Ожидаемые данные         |
|:--------------:|:--------------------------------:|:--------------------------------:|
|     1.1.1      |   Incorrect number token: 1.1.   |   Incorrect number token: 1.1.   |
|     1abvgd     |    Incorrect number token: 1a    |    Incorrect number token: 1a    |
|     000111     |  Incorrect number token:000111   |  Incorrect number token:000111   |
|   000000000    | Incorrect number token:000000000 | Incorrect number token:000000000 |


