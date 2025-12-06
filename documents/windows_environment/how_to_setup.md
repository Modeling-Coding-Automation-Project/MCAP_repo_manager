# Windows 環境構築手順

## 目次

- [Windows 環境構築手順](#windows-環境構築手順)
  - [目次](#目次)
  - [要件](#要件)
  - [1. WSLの有効化](#1-wslの有効化)
  - [2. Ubuntu 24.04をインストール](#2-ubuntu-2404をインストール)
  - [3. Visual Studio Codeをインストール](#3-visual-studio-codeをインストール)
  - [4. Visual Studio CodeからWSL Ubuntuを開く](#4-visual-studio-codeからwsl-ubuntuを開く)
  - [5. リポジトリクローンとDockerのインストール](#5-リポジトリクローンとdockerのインストール)
  - [6. Dockerを開く](#6-dockerを開く)
  - [7. 動作確認](#7-動作確認)

## 要件

Windows11 25H2、またはそれに近いOSバージョンであること。

## 1. WSLの有効化

スタート画面を開き、「Windowsの機能の有効化または無効化」を入力する。

以下のように項目が表示されるので、「Windowsの機能の有効化または無効化」をクリックして開く。

![image](./images/open_windows_function_activate.png)

「Linux 用 Windows サブシステム」をチェックして有効化する。
「Hype-V」をチェックして有効化する。

![image](./images/windows_function_activate.png)

OKをクリックしてウィンドウを閉じ、PCを再起動する。

次に、WSLを最新に更新する。

スタート画面を開き、「PowerShell」と入力し、「Windows PowerShell」をクリックして開く。

![image](./images/power_shell.png)

開いたターミナル画面で、以下のコマンドを実行する。

```powershell
wsl --update
```

![image](./images/wsl_update.png)

## 2. Ubuntu 24.04をインストール

スタート画面を開き、「Store」と入力し、「Microsoft Store」を開く。

![image](./images/open_store.png)

検索欄にUbuntuと入力し、Ubuntu 24.04 を選択してインストールする。

![image](./images/store_ubuntu.png)

この時、「Ubuntu 24.04.01 LTS」のように表示されているが、ここは時期によっては「Ubuntu 24.04.02 LTS」となっているかもしれない。

どちらでも問題ないので、「Ubuntu 24.04.~~」をインストールすること。

インストールが終わると、「開く」というボタンが表示されるので、クリックする。

![image](./images/open_ubuntu_from_store.png)

初回起動時は、インストール処理が入るので、待つ。

![image](./images/ubuntu_installing.png)

しばらく待つと、ユーザー名とパスワードの入力を求められる。

![image](./images/ubuntu_user_setup.png)

自由に決めてよいので、ユーザー名とパスワードを入力する。パスワードは入力しても、画面上には表示されていないので注意。

![image](./images/ubuntu_installed.png)

## 3. Visual Studio Codeをインストール

以下のリンク先から、Visual Studio Codeのインストーラをダウンロードしてインストールする。

<https://code.visualstudio.com/download>

Visual Studio Codeを開き、「Extensions」をクリックし、以下の拡張機能をインストールする。

![image](./images/extensions_remote_development.png)

![image](./images/extensions_docker.png)

画像のように、検索欄で「Remote Development」、「Docker」を入力すると、項目が現れる。

## 4. Visual Studio CodeからWSL Ubuntuを開く

「Remote Explorer」を開き、

![image](./images/click_remote_explorer.png)

「WSL Targets」を開く。

![image](./images/select_wsl_targets.png)

「Ubuntu-24.04」がリストされているので、マウスカーソルを合わせて右矢印をクリックする。

![image](./images/select_ubuntu.png)

これにより、のWSL Ubuntu環境がVisual Studio Codeで開かれる。左下に「WSL: Ubuntu24.04」と表示されていることを確認する。

## 5. リポジトリクローンとDockerのインストール

Visual Studio Codeのターミナルで、以下のコマンドを実行する。

```bash
git clone https://github.com/Modeling-Coding-Automation-Project/MCAP_repo_manager.git
```

![image](./images/git_clone_mcap.png)

「MCAP_repo_manager」一式がダウンロードされるので、「Open Folder」をクリックしてそのディレクトリを開く。

![image](./images/click_open_folder.png)

![image](./images/click_MCAP_repo_manager.png)

「Do you trust the authors of the files in this folder?」と表示されたら、「Yes, I trust the authors」を選択する。

次に、「docker」フォルダの「install_docker_environment.sh」を実行する。

![image](./images/show_install_docker_environment.png)

ターミナルを表示し、以下のコマンドを実行する。

```bash
cd ./docker
chmod +x ./*.sh
./install_docker_environment.sh
```

Dockerのインストールが始まる。途中、エンターキーの入力を求められる場合があるので、エンターを押す。

![image](./images/require_enter_key.png)

インストール完了後、以下のコマンドを実行し、Dockerを再起動する。

```bash
sudo sytemctl restart docker
```

それでも以降の作業がエラーで進まない場合は、WSLを閉じ、WSL Ubuntuを再起動する。またはPCを再起動する。

## 6. Dockerを開く

左下の「>< WSL: Ubuntu-24.04」をクリックし、

![image](./images/WSL_Ubuntu-24.04.png)

「Reopen in Container」をクリックする。

![image](./images/reopen_in_container.png)

Docker Hubからイメージのダウンロードが始まる。サイズが大きいので、少し時間がかかる。

イメージのダウンロード、コンテナの起動、Visual Studio Codeの拡張機能のセットアップが自動で行われ、以下のように表示される。

![image](./images/docker_container_setup_finished.png)

## 7. 動作確認

ここまでの作業で、環境構築は完了している。

しかし、初回はPythonの仮想環境のパス指定が必要であるので、動作確認も兼ねて行う。

メニューバーの「File」、「Open Folder」で、「/opt/ModelingCodingAutomationProject/python_mpc_to_cpp」を開く。

![image](./images/open_demo.png)

次に、「sample」フォルダから任意のPythonコードを開く。

![image](./images/open_sample.png)

右下のPythonバージョン「3.12.3」と書かれているところをクリックする。

![image](./images/click_python_version.png)

「Enter interpreter path...」をクリックする。

![image](./images/click_enter_interpreter_path.png)

「Find」をクリックする。

![image](./images/click_find.png)

「/opt/venv_py_MCAP/bin/python3」をクリックする。

![image](./images/click_python3.png)

左側の「Run and Debug」をクリックし、設定を「Python Debugger: Python File」に切り替える。

![image](./images/change_debugger.png)

上記画像の再生ボタンををクリック、またはF5を入力することで、コードを実行する。

エラー無くC++コードが生成されたり、グラフウィンドウが表示されればOK。
