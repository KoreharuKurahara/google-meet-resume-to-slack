# Google Meet文字起こし自動要約・Slack投稿アプリケーション

Google Meetの文字起こしを自動的に取得し、生成AIで要約した上で、元のGoogle DocのURLと共に指定されたSlackチャンネルに投稿するPythonアプリケーションです。

## 📋 機能

- 📁 Google Driveから最新の文字起こしファイルを自動取得
- 🤖 Google Generative AI（Gemini）による高品質な要約生成
- 📤 Slack Block Kitを使用したリッチフォーマットでの投稿
- 📊 詳細なログ出力とエラーハンドリング
- 🔧 環境変数による安全な設定管理

## 🚀 セットアップ

### 1. 依存関係のインストール

```bash
# プロジェクトディレクトリに移動
cd google-meet-resume-to-slack

# 仮想環境の作成（推奨）
python -m venv venv

# 仮想環境のアクティベート
source venv/bin/activate  # macOS/Linux
# または
venv\\Scripts\\activate  # Windows

# pipのアップグレード
pip install --upgrade pip

# 依存関係のインストール
pip install -r requirements.txt
```

### 2. 必要なAPIキーとサービスアカウントの設定

#### Google Cloud Platform（GCP）の設定

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. Google Drive APIを有効化
3. サービスアカウントを作成し、JSONキーファイルをダウンロード
4. Google Meetの文字起こしが保存されるGoogle Driveフォルダにサービスアカウントのアクセス権を付与

#### Slack アプリの設定

1. [Slack API](https://api.slack.com/apps)で新しいアプリを作成
2. 必要なスコープを設定：
   - `chat:write`
   - `chat:write.public`
3. ボットトークン（`xoxb-`で始まる）を取得
4. アプリを投稿先のワークスペースにインストール

#### Google Generative AI（Gemini）の設定

1. [Google AI Studio](https://makersuite.google.com/app/apikey)でAPIキーを取得

### 3. 環境変数の設定

`.env.example`をコピーして`.env`ファイルを作成し、必要な値を設定してください：

```bash
cp .env.example .env
```

`.env`ファイルを編集：

```bash
# Google Drive API設定
GOOGLE_CREDENTIALS_PATH=/path/to/your/service-account-key.json
GOOGLE_DRIVE_FOLDER_ID=your_google_drive_folder_id_here

# Slack設定
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token-here
SLACK_CHANNEL_ID=your_slack_channel_id_here

# 生成AI設定
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
AI_MODEL_NAME=gemini-pro

# ファイル保存先
TARGET_DIRECTORY=./downloads
```

### 4. Google DriveフォルダIDの取得方法

Google DriveのフォルダURLから取得できます：
```
https://drive.google.com/drive/folders/[ここがフォルダID]
```

### 5. SlackチャンネルIDの取得方法

Slackで以下の方法で取得できます：
1. チャンネルを右クリック → 「リンクをコピー」
2. URLの最後の部分がチャンネルIDです
```
https://app.slack.com/client/T1234567/[ここがチャンネルID]
```

## 🎯 使用方法

### 基本実行

```bash
python main.py
```

### テスト実行（各コンポーネントの動作確認）

```bash
python main.py --test
```

### 個別モジュールのテスト

```bash
# 環境変数のテスト
python config.py

# Google Drive接続のテスト
python drive_downloader.py

# 生成AI要約のテスト
python ai_summarizer.py

# Slack投稿のテスト
python slack_poster.py
```

## 📁 プロジェクト構造

```
google-meet-resume-to-slack/
├── main.py                 # メイン処理
├── config.py              # 環境変数管理
├── drive_downloader.py    # Google Drive操作
├── ai_summarizer.py       # 生成AI要約
├── slack_poster.py        # Slack投稿
├── requirements.txt       # 依存関係
├── .env.example          # 環境変数テンプレート
├── .env                  # 環境変数（要作成）
├── README.md             # このファイル
├── meeting_summary.log   # 実行ログ
└── downloads/            # ダウンロードファイル保存先
```

## 🔧 カスタマイズ

### 要約プロンプトの変更

`ai_summarizer.py`の`_create_summary_prompt`関数を編集して、要約の形式や内容をカスタマイズできます。

### Slackメッセージフォーマットの変更

`slack_poster.py`の`_create_slack_message`関数を編集して、投稿メッセージの見た目を変更できます。

### ファイル検索条件の変更

`drive_downloader.py`の検索クエリを編集して、対象ファイルの検索条件を変更できます。

## 📝 ログファイル

実行ログは`meeting_summary.log`に保存されます。エラーが発生した場合は、このファイルを確認してください。

## ⚠️ 注意事項

- **セキュリティ**: `.env`ファイルはGitにコミットしないでください
- **APIキー**: 本番環境では適切な権限管理を行ってください
- **レート制限**: 各APIのレート制限に注意してください
- **エラーハンドリング**: 本テンプレートは基本的なエラーハンドリングのみ実装されています

## 🐛 トラブルシューティング

### よくある問題

1. **Google Drive APIエラー**
   - サービスアカウントにフォルダのアクセス権があるか確認
   - Google Drive APIが有効になっているか確認

2. **Slack投稿エラー**
   - ボットトークンが正しいか確認
   - チャンネルIDが正しいか確認
   - 必要なスコープが設定されているか確認

3. **生成AIエラー**
   - APIキーが正しいか確認
   - APIクォータが残っているか確認

### ログレベルの変更

デバッグ時は、各ファイルのログレベルを`DEBUG`に変更してより詳細な情報を取得できます：

```python
logging.basicConfig(level=logging.DEBUG)
```

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🤝 コントリビューション

バグ報告や機能追加の提案は、GitHubのIssueまでお願いします。
