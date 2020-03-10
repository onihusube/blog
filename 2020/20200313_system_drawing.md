# ［C#/.Net Core］ .Net Core(3.1)でSystem.Drawingをクロスプラットフォームに利用する


### `System.Drawing.Common`パッケージ

`System.Drawing`名前空間には画像を扱う上で便利なものが含まれていますが、そのままだと[ドキュメント](https://docs.microsoft.com/ja-jp/dotnet/api/system.drawing?view=netframework-4.8)に見えるものの半分も利用できません。Windowsで開発していてもです・・・
これは.Net Frameworkから引き継いだもので、`System.Drawing`名前空間のものはWindowsのGDI+ APIに依存しているためWindows以外の環境で利用できません。.Net Coreはクロスプラットフォームがデフォルトなので、このような環境依存のものは利用できないのでしょう。でも[ドキュメント](https://docs.microsoft.com/ja-jp/dotnet/api/system.drawing?view=netframework-4.8)を眺めていると.Net Core 3.0から対応という記述が見られます。いや使えないじゃん・・・

これの正式な解決策かは知りませんが、Nugetから`System.Drawing.Common`パッケージを追加することで`System.Drawing`名前空間内のものを.Net Coreなプロジェクトにおいても利用可能になります。


これをインストールしておくことでWindowsではそのまま意図通りの動作を得られますし、シングルバイナリ出力しても問題ありません。しかし、Windows以外のプラットフォームへ持っていくと`DllNotFoundException`が投げられることでしょう。結局Windows依存なのか・・・

### libgdiplus

依存関係が無いなら依存関係を整えてやれば良いだけのこと。非Windowsにおける.Net実装であるMonoが`System.Drawing`の非Windows実装である*libgdiplus*というライブラリをリリースしています。これを入れればWindows以外でもそのままのコードで`System.Drawing`名前空間のものをほぼ利用できます（100%実装してないと書かれているので、利用できないものもあるでしょう・・・）。

#### MacOS

```bash
$ brew install mono-libgdiplus
```

[.NET COREでSYSTEM.DRAWINGを使う MAC編](https://minnano.app/support/2018/06/02/system-drawing_for_net_core/)より。

#### Linux

```bash
$ sudo apt-get update
$ sudo apt-get install libgdiplus
```

[.NET COREでSYSTEM.DRAWINGを使う UBUNTU編](https://minnano.app/support/2018/06/16/system-drawing_for_ubuntu/)より。

※私自身は、Linuxでの動作は未確認です。

### 参考文献

- [System.Drawing 名前空間 - Microsoft Docs](https://docs.microsoft.com/ja-jp/dotnet/api/system.drawing?view=netframework-4.8)
- [System.Drawing.Common 4.7.0 - Nuget Gallery](https://www.nuget.org/packages/System.Drawing.Common/)
- [libgdiplus - Mono](https://www.mono-project.com/docs/gui/libgdiplus/)
- [.NET COREでSYSTEM.DRAWINGを使う MAC編](https://minnano.app/support/2018/06/02/system-drawing_for_net_core/)
- [.NET COREでSYSTEM.DRAWINGを使う UBUNTU編](https://minnano.app/support/2018/06/16/system-drawing_for_ubuntu/)