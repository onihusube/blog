# ［C++］構造化束縛とラムダキャプチャ

一部のコンパイラでは構造化束縛宣言で導入された変数をラムダ式によってキャプチャすることができません。ただ、規格を眺めてもできない理由を見出せません。  
どうしてこうなっているのでしょうか・・・？

### C++17における構造化束縛時の変数名の扱い

C++17においては

ただ、この2つの変更はC++17の規格書（N4659）には載っていません。  
Core issue 2313はC++17規格完成後に欠陥報告としてC++17に適用され、P0588R1はC++20で承認され明文化されたためです。

### C++20での構造化束縛宣言の拡張


### 参考文献
- [Lambda implicit capture fails with variable declared from structured binding - stackoverflow](https://stackoverflow.com/questions/46114214/lambda-implicit-capture-fails-with-variable-declared-from-structured-binding)
- [Core issue 2313 : Redeclaration of structured binding reference variables](https://wg21.cmeerw.net/cwg/issue2313)
- [P0588R1 : Simplifying implicit lambda capture](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0588r1.html)
- [P1091R3 : Extending structured bindings to be more like variable declarations](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1091r3.html)