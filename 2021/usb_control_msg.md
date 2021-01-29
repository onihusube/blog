# ［Linux］usb_control_msgの引数について

LinuxでのUSBデバイスドライバを書く事になった折に、`usb_control_msg`関数の引数が意味不明だったので調べたことのメモです（2021年1月29日時点の情報です）。

`usb_control_msg`は`usb.h`内で次のように宣言されています（実装がどこにあるのかは知りません・・・）。

```c
extern int usb_control_msg(struct usb_device *dev, unsigned int pipe,
	__u8 request, __u8 requesttype, __u16 value, __u16 index,
	void *data, __u16 size, int timeout);
```

この中で分からないのは`pipe`から`index`の引数の意味です。他の引数はなんとなく察せられると思うので割愛します。

この謎のパラメータたちはUSB仕様で指定されるUSB Device Requestsにおける送信側が用意しておくべきデータフィールドに対応しています。これらがなぜわからないのかと言うと、USB仕様書をちゃんと読まないと分からないからです。たったの650ページしかないのでC++規格書に比べると圧倒的な薄さです、読みましょう。

### `pipe`



### `requesttype`

[ch9.h](https://github.com/torvalds/linux/blob/master/include/uapi/linux/usb/ch9.h)

### `request`
### `value`
### `index`

### 余談 : Unknown symbol usb_control_msg

なんかなにもか考えずにビルドしてinsmodするとdmesgにこんなエラーがずらーっと出てます。これはそのモジュールが宣言？しているライセンスが合っていないのでそれらのものを使えない？と言われているようです。

`MODULE_LICENSE("GPL");`を追記（変更）すると消えます。

Linuxの提供するUSBのライブラリを使っているのでライセンスはそれに従う事になるようです。

### 参考文献

- [usb.h torvalds/linux - Github](https://github.com/torvalds/linux/blob/master/include/linux/usb.h)
- [ch9.h torvalds/linux - Github](https://github.com/torvalds/linux/blob/master/include/uapi/linux/usb/ch9.h)
- [USB 2.0 Specification - USB-IF](https://www.usb.org/document-library/usb-20-specification)
- [Linuxデバイスドライバ 第3版 - O'Reilly Japan](https://www.oreilly.co.jp/books/4873112532/)
- [unknown symbol __class_create (err 0) - stackoverflow](https://stackoverflow.com/questions/29578931/unknown-symbol-class-create-err-0)