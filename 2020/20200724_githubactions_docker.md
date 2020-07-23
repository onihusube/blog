# Github Actions上のDockerコンテナ上のGCCの最新版でテストを走らせたかった

Github Actionsで用意されている[ubuntu 20.04環境に用意されているソフトウェア](https://github.com/actions/virtual-environments/blob/master/images/linux/Ubuntu2004-README.md)を見るとGCCは9.3が用意されています（2020年7月24日現在）。しかしGCC9.3はC++20対応がほぼなされていないので使い物になりません（個人の感想です）。いつかは追加されるでしょうが、GCC10.2（もう出た）、GCC 11.1とか言いだすと永遠に待ち続けることになりそうです・・・

一方、[Docker公式のGCCコンテナ](https://hub.docker.com/_/gcc)は既にGCC10.1が利用可能です（2020年7月24日現在）。

つまり、この2つを組み合わせれば最新のGCCを使いながらGithub Actionsできるはず！

### Dcokerコンテナを起動しその上でビルドとテストを走らせるActionを作成する

- [Docker コンテナのアクションを作成する - GitHub Docs](https://docs.github.com/ja/actions/creating-actions/creating-a-docker-container-action)

この資料にはDockerコンテナを使ってCIを走らせるための初歩初歩の事が書いてあります。ちゃんと読むと、Dockerコンテナを起動し何かするためのオリジナルのActionを作成し、それをテストしたいリポジトリのymlファイルから呼び出す形になる事が分かります。

（なお、私はちゃんと読まなかったのでわかりませんでした）

というわけで、まずはGCCのDockerコンテナを起動してビルドとテストを行うActionを作成します。

#### Dockerファイルの作成

まずは所望の動作を達成するためのDockerファイルを作ります。

```docker
From gcc:latest
RUN apt-get update
RUN apt-get install -y python3-pip
RUN pip3 install meson ninja
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

私はビルドシステムに専らmesonを使っているので、mesonもインストールしておきます。上記Dcokerfileの2-4行目はお好きなビルドシステムのインストールに置き換えてください。

ここの`RUN`で全部やっても良いのですがあまり汎用性が無くなるので、ここでは最低限の環境構築に留めて、メインの処理は別に書いたシェルスクリプト（ここでは`entrypoint.sh`）に記述します。

5行目で用意したシェルスクリプトをDockerインスタンス上にコピーして、6行目で開始時に実行するように指示します。

#### シェルスクリプトの作成

- [Docker コンテナのアクションを作成する - GitHub Docs](https://docs.github.com/ja/actions/creating-actions/creating-a-docker-container-action#writing-the-action-code)

このページにあるものを参考にして書きます。ただこのページだけ見ても、テストしたいリポジトリのクローンをどうするのかが分かりません。試してみると別にクローンされてはいないので自分でクローンしてくる必要があります。なので、それを引数として受け取るようにします。

公式のActionにはcheckoutというのがありますが、今回はDocker上で実行するため利用できなさそうです。

```bash
#!/bin/sh -l

git clone $2
cd $1
meson build
meson test -C build -v
```

第一引数にリポジトリ名（=ディレクトリ名）、第二引数にリポジトリのURLを受けるようにしています。5-6行目はmeson特有のものなので、お使いのビルドシステムのビルドコマンドと成果物の実行コマンドに置き換えてください。

ファイル名は先程Dockerfileに書いた`entrypoint.sh`と合わせます。`chmod +x entrypoint.sh`で実行可能にすることを忘れないようにしてください。  
Windowsの場合は次のページが参考になります。

- [Gitでファイルの実行権限を変更する - Qita](https://qiita.com/satotka/items/29f1483f8921d2ecfeab)

#### Actionファイルの作成

次にActionとして呼ばれたときに何をするかを`action.yml`というファイルに記述します。試してないですがファイル名は多分固定だと思われます。

```yml
name: 'build & test'

inputs:
  name:
    description: 'Name of target repository'
    required: true
  uri:
    description: 'URI of target repository'
    required: true

runs:
    using: 'docker'
    image: 'Dockerfile'
    args:
    - ${{ inputs.name }}
    - ${{ inputs.uri }}
```

`inputs`で先程のシェルスクリプトに渡す引数を定義しています。上から順番に第一引数（`name`）、第二引数（`uri`）で内容は先ほどの通り。`description`は説明で無くても良いです。`required`は引数が省略可能かを表しており、今回は省略してほしくないので`true`に設定しておきます。

他にも出力を定義できたりします。出来ることは次のページを参照。

- [GitHub Actionsのメタデータ構文 - GitHub Docs](https://docs.github.com/ja/actions/creating-actions/metadata-syntax-for-github-actions)

`runs`にActionとして呼ばれたときにやることを書いておきます。`using`は何のアプリケーションを使用するのかを指示するもので、ここではDockerを指定します。`image`には使いたいDockerイメージ名を指定します。Docker Hubにあるイメージ名を指定しても良いようですが、今回は先ほど用意したDockerfile（のファイル名）を指定します。

#### Actionリポジトリの作成

ここまで用意したDockerfile、やることを記述したシェルスクリプト`entrypoint.sh`、Actionを記述した`action.yml`の3つをGithub上の公開リポジトリに保存しておき、リリースタグを打っておくことで、他のリポジトリからActionとして参照できるようになります。  
リポジトリのトップに全てをぶちまけるのが正しそうです。

私の場合は次のようになりました。

- [onihusube/gcc-meson-docker-action - Github](https://github.com/onihusube/gcc-meson-docker-action)

`Publish this Action to Marketplace`なるメッセージが表示されていたら、きちんとActionとして認識されています。もし自作のActionをMarketplaceに公開したい場合はreadmeを適切に整えておく必要がありそうです。

### テストしたいリポジトリのワークフロー中でActionを呼ぶ

こうして用意した自作Docker ActionをテストしたいリポジトリのGithub Actions ワークフローから呼び出します。

```yml
name: Test by GCC latest  # ワークフローの名前
on: [push, pull_request]  # 何をトリガーにして実行するか

jobs:
  test:
    runs-on: ubuntu-latest  # Dockerを実行することになるベース環境
    name: run test
    steps:
    - name: run test in docker
      uses: onihusube/gcc-meson-docker-action@v6
      with:
        name: 'harmony'
        uri: 'https://github.com/onihusube/harmony.git'
```

実物が[こちら](https://github.com/onihusube/harmony/blob/master/.github/workflows/main.yml)です。今回対象のリポジトリは私が[衝動で書いていたC++のライブラリ](https://github.com/onihusube/harmony)です。

ベースは普通のGithub Actionsのワークフローを書くのと変わらないはず。今回重要なのは先程作成したDocker Actionを適切に呼び出すことです。

`steps`中の`uses`で任意のActionを呼び出すことができます。先程作成したActionのリポジトリ参照する形で`作ったユーザー名/リポジトリ名@タグ`というように指定します（上記タグがv6とかなってるのは試行錯誤の名残です・・・）。  
その次の`with`で順番に引数を指定します。指定出来るのはActionの`yml`に書いたものだけで、ここに書いた引数がDockerインスタンス上で実行されるシェルスクリプトに渡されることになります。

でこれをプッシュするとDocker上のGCCでビルドされテストが実行されたので、どうやら目的を果たせたようです（[参考の結果](https://github.com/onihusube/harmony/runs/885189423?check_suite_focus=true)）。

### 参考文献

- [gcc - Docker Hub](https://hub.docker.com/_/gcc)
- [Docker コンテナのアクションを作成する - GitHub Docs](https://docs.github.com/ja/actions/creating-actions/creating-a-docker-container-action)
- [GitHub Actionsのメタデータ構文 - GitHub Docs](https://docs.github.com/ja/actions/creating-actions/metadata-syntax-for-github-actions)
- [Gitでファイルの実行権限を変更する - Qita](https://qiita.com/satotka/items/29f1483f8921d2ecfeab)