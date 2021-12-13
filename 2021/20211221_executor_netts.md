# ［C++］`owning_view`によるパイプライン安全性の確保

この記事は[C++ Advent Calendar 2021](https://qiita.com/advent-calendar/2021/cxx)の21日目の記事です。

### ExecutorとNetworking TS

#### Executor

Executorライブラリは、C++に非同期処理サポートを組み込むためのライブラリです。

#### Networking TS

Networking TSはBoost.Asioをベースとして、標準ライブラリに基礎的なソケット通信の機能を追加しようとするものです。

Networking TS（Boost.Asio）は、非同期I/O操作のために非同期処理のサポート機構、すなわちExecutorに相当するものを提供しています。そのため、ExecutorライブラリはNetworking TSの一部であり、ベースとなるものとされます。

### Executorの道程


### P2300 vs Networking TS

### 参考文献

- [A Unified Executors Proposal for C++ | P0443R14](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p0443r14.html)
- [P2033R0 - History of Executor Properties](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2033r0.pdf)
- [P2300R2 `std::execution`](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2300r2.html)
- [P2444R0 The Asio asynchronous model](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2444r0.pdf)
- [P2470R0 Slides for presentation of P2300R2: `std::execution` (`sender/receiver`)](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2470r0.pdf)
- [P2463R0 Slides for P2444r0 The Asio asynchronous model](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2463r0.pdf)
- [P2464R0 Ruminations on networking and executors](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2464r0.html)
- [P2469R0 Response to P2464: The Networking TS is baked, P2300 Sender/Receiver is not.](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2469r0.pdf)
- [P2479R0 Slides for P2464](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2479r0.pdf)
- [P2471R1 NetTS, ASIO and Sender Library Design Comparison](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2471r1.pdf)
- [P2480R0 Response to P2471: "NetTS, Asio, and Sender library design comparison" - corrected and expanded](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2480r0.pdf)