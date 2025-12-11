# リポジトリ管理

## 目的

本組織「Modeling-Coding-Automation-Project」にあるリポジトリ群をまとめてGit操作を行うための、便利なスクリプトをまとめています。

## 環境構築手順

本組織「Modeling-Coding-Automation-Project」にあるリポジトリ群を使うための環境構築手順を、以下で説明しています。

[環境構築手順](./documents/environment.md)

## Dockerイメージについて

Dockerによる開発環境も整備しています。以下リンク先のイメージを使えば、すぐに開発を始めることができます。

<https://github.com/modeling-coding-automation-project/MCAP_Playground/pkgs/container/mcap_env>

以下のコマンドを実行してイメージを取得できます。

```bash
docker pull ghcr.io/modeling-coding-automation-project/mcap_env:latest
```

イメージの詳細については、「docker/docker_image_creation/Dockerfile」、「docker/docker_image_creation/install_MCAP_environment_for_docker.sh」をご参照ください。

WSL UbuntuにDocker環境を整えるには、「docker/install_docker_environment.sh」を実行するだけですぐに整えることができます。

※以前はDockerHubにイメージを置いていましたが、GitHub Container Registry (ghcr) へ変更しました。以下リンク先のリポジトリは今後削除される可能性がありますのでご注意ください。

<https://hub.docker.com/r/claudeashford/mcap_env>

## サポート

新規にissueを作成して、詳細をお知らせください。

## 貢献

コミュニティからのプルリクエストを歓迎します。もし大幅な変更を考えているのであれば、提案する修正についての議論を始めるために、issueを開くことから始めてください。

また、プルリクエストを提出する際には、関連するテストが必要に応じて更新または追加されていることを確認してください。

## ライセンス

[MIT License](./LICENSE.txt)
