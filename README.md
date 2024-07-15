# REX - транслятор с языка Ruby на язык R.

**Содержание:**
<!-- TOC -->

* [REX - Ruby to R translator](#rex---simple-ruby-lexer)
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
3. Неиспользованные переменные и функции - игнорируются и не выводятся в транслируемый код.

   Например, следующий код на языке Ruby:
    ``` Ruby
   a = 10
   b = 20
   def foo()
      return a
   end
   c = a + b
   puts(a)
   ```
   В результате трансляции на язык R примет следующий вид:
    ``` R
    a <- 10
    print(a)
      ```
   Так как функция `foo` и переменная `c` хоть и были объявлены, но нигде в дальнейшем не были использованы. А
   переменная `b` была использована один раз в расчете переменной `c`, однако т.к. последняя была убрана в ходе
   оптимизации, то и переменная `b` теперь больше не используется, поэтому тоже не подлежит трансляции.


4. Все операции, расположенные после `return` - игнорируются и не выводятся в транслируемый код. Если на верхнем уровне
   встречен оператор `return`, то процесс парсинга завершается, т.к. нижеследующие операторы уже не имеют смысла.
5. Содержимое `return` верхнего уровня - игнорируется, т.к. не имеет смысла.
6. Ненужные скобки игнорируются на этапе трансляции.

   Например, следующий код на языке Ruby:
    ``` Ruby
    a = (((((((((((10 + 20)))))))))))
    b = (((((a)) + (10))) * 20)
    puts(a + b)
   ```
   В результате трансляции на язык R примет следующий вид:
    ``` R
    a <- 10 + 20
    b = (a + 10) * 20
    print(a + b)
    ```

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

Задача теста, выявить потенциальные ошибки лексера, так как входные данные в этом тесте являются некорректными и лексер
должен обрабатывать их выдавая соответствующие ошибки.

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

Как можно видеть, часть неправильных конструкций кода лексер обработал правильно, а другая часть не была учтена при
реализации.
После выявление ошибок и внесения соответствующих правок, результат работы стал следующим:

| Входные данные |         Выходные данные          |         Ожидаемые данные         |
|:--------------:|:--------------------------------:|:--------------------------------:|
|     1.1.1      |   Incorrect number token: 1.1.   |   Incorrect number token: 1.1.   |
|     1abvgd     |    Incorrect number token: 1a    |    Incorrect number token: 1a    |
|     000111     |  Incorrect number token:000111   |  Incorrect number token:000111   |
|   000000000    | Incorrect number token:000000000 | Incorrect number token:000000000 |


