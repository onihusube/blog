# ［C++］ std::atomicの待機・通知APIと条件変数

[:contents]

### `std::atomic`の待機・通知API

C++20では`std::atomic`（`std::atomic_flag`/`std::atomic_ref`）に待機と通知を行うメンバ関数が追加され、`std::atomic`オブジェクトによってスレッド間の同期がより簡単かつ効率的に行えるようになります。

```cpp
std::atomic<int> shared_val{};  // C++20から0で初期化される

void wait_thread() {
  while (...) {
    // 通知スレッドからの通知を待機する
    shared_val.wait();
    int val = shared_val.load();

    ...
  }
}

void notify_thread() {
  while (...) {
    int new_num = 0;
    ...

    // 値を更新
    shared_val.store(new_num);
    // wait()中のスレッドへ通知
    shared_val.notify_one();

    // 待機しているのが複数のスレッドの場合
    // wait()中の全てのスレッドへ通知
    shared_val.notify_all();
  }
}
```

複数スレッド間で共有したいリソースを`std::atomic`オブジェクトとしておき、そのオブジェクトに対して待機側では`.wait()`の呼び出しで待機を行い、通知側（起床させる場合）では同じオブジェクトに対して`.notify_one()`を呼び出すことでそのオブジェクトで待機しているスレッドを1つだけ起床させ再開させます。1つの`std::atomic`オブジェクトに対して複数のスレッドが待機を行うこともでき、もし待機中のスレッドをすべて一斉に起床させたい場合は`.notify_all()`を使用できます。

従来`std::atomic`でこのような同期を行おうとすると待機側ではCASループのようなビジーループを使用せざるを得ず、それはあまり効率的な待機方法ではありませんでした。これらのAPIはそれを改善するために追加されたもので、`.wait()`による待機はOSのAPIを用いるなどして効率的に処理されることが期待されます。

C++20ではいくつかの同期プリミティブクラスが追加されましたが、`std::atomic`とこの待機・通知APIを用いるとそれらのクラスを簡単かつ効率的に構成することができます。

### `std::condition_variable`

先程のサンプルコードはC++17までなら`std::condition_variable`を使用して書くことになるでしょう。対応させるように書くと例えば次のようになります

```cpp
int shared_val{};
std::mutex mtx;
std::condition_variable cv;

void wait_thread() {
  while (...) {
    // 通知スレッドからの通知を待機する
    shared_val.wait();
    {
      // まずロックを取得
      std::unique_lock lock{mtx};

      // 通知スレッドからの通知を待機
      cv.wait(lock);

      // 共有変数の使用
      int val = shared_val;
    }

    ...
  }
}

void notify_thread() {
  while (...) {
    int new_num = 0;

    // 更新する値の取得など
    ...

    {
      // ロックを取得
      std::lock_guard _{mtx};
      
      // 値を更新
      int val = new_num;

      // wait()中のスレッドへ通知
      cv.notify_one();

      
      // 待機しているのが複数のスレッドの場合
      // wait()中の全てのスレッドへ通知
      shared_val.notify_all();
    }
  }
}
```

メンバ関数名が共通しているという以上に、この2つのAPIはよく似通っていることが分かります。

### 比較

C++20`std::atomic`の待機・通知APIは`std::condition_variable`の基本的な使用法を改善したものと見ることもできます。比較してみると次のような差があります

||`atomic`による通知と待機|`condition_variable`|
|---|---|---|
|必要なもの|`atomic`オブジェクト |保護するリソース+`mutex`+`condition_variable`オブジェクト|
|効率的な待機を行う|Yes|Yes|
|複数リソースの保護|`atomic<T>`の`T`にまとめることができれば可能|可能|
|時間を指定して待機|不可|`wait_until()/wait_for()`|

特に、同じ同期を行うために`std::atomic`オブジェクト1つで共有リソースの表現から同期オブジェクトとしての利用までこなせるという点は、`std::condition_variable`が利用のために3点セットが必要になるのと比較するとかなり簡易化しています。また、同期に当たって`std::mutex`のロックを必要としないことも利点となるかもしれません。

一方で、共有リソースが複数になったり（あるいは`std::atomic`で包めなかったり）、時間を指定して`.wait()`を解除したいなどの場合は`std::atomic`のAPIでは達成できなくなるので、従来通り`std::condition_variable`の利用が必要になります。

### シグナルセーフ？

`std::atomic<T>`オブジェクトは`std::atomic<T>::is_always_lock_free`が`true`であればシグナルセーフであると指定されており、このAPI追加以降のC++23現在でもそれは変化していません。では、C++20の待機・通知APIはシグナルセーフなのでしょうか？

まず、`.wait()`はその性質上明らかに現在のスレッドをブロックするため、シグナルセーフではありません。

では通知関数はというと、ロックフリーな実装を取ることができるものの、オブジェクトサイズや環境によってはロックフリーとならない場合があるようです。

詳しいことはP3255R1で報告されていますが、待機・通知API以外は`is_always_lock_free == true`ならばシグナルセーフとなりますが待機・通知APIはそうならないため、規定を修正して待機・通知APIがシグナルセーフかどうかは別のプロパティで指定するように修正しようとしています（R1によれば待機関数もシグナルセーフとなる場合があるようです、どういうことでしょう・・・）。

### 参考文献

- [条件変数の利用方法 - cpprefjp](https://cpprefjp.github.io/article/lib/how_to_use_cv.html)
- [P3255R1 Expose whether atomic notifying operations are lock-free](https://wg21.link/p3255r1)
