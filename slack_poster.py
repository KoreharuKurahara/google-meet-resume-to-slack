"""
Slackに要約を投稿するモジュール
"""
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def post_summary_to_slack(slack_token, channel_id, summary_text, google_doc_url):
    """
    生成AIで要約されたテキストと、元のGoogle DocのURLをSlackの指定チャンネルに投稿
    
    Args:
        slack_token (str): Slackボットトークン
        channel_id (str): 投稿先のSlackチャンネルID
        summary_text (str): 生成AIによって要約されたテキスト
        google_doc_url (str): 元のGoogle DocのURL
    
    Returns:
        bool: 成功した場合はTrue、失敗した場合はFalse
    """
    try:
        # Slack WebClientの初期化
        client = WebClient(token=slack_token)
        
        # メッセージの作成
        message = _create_slack_message(summary_text, google_doc_url)
        
        logger.info(f"Slackチャンネル {channel_id} に投稿を開始します...")
        
        # Slackにメッセージを投稿
        response = client.chat_postMessage(
            channel=channel_id,
            text="📝 会議の要約が完了しました",  # 通知用のプレーンテキスト
            blocks=message["blocks"]  # リッチフォーマット用のブロック
        )
        
        if response["ok"]:
            logger.info(f"Slackへの投稿が成功しました。メッセージTS: {response['ts']}")
            return True
        else:
            logger.error(f"Slackへの投稿に失敗しました: {response}")
            return False
            
    except SlackApiError as e:
        logger.error(f"Slack API エラー: {e.response['error']}")
        return False
    except Exception as e:
        logger.error(f"Slack投稿でエラーが発生しました: {str(e)}")
        return False

def _create_slack_message(summary_text, google_doc_url):
    """
    Slack投稿用のメッセージを作成
    
    Args:
        summary_text (str): 要約テキスト
        google_doc_url (str): 元のGoogle DocのURL
    
    Returns:
        dict: Slack Block Kit形式のメッセージ
    """
    # メッセージブロックの作成
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📝 会議要約レポート",
                "emoji": True
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": summary_text
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"📄 *元の文書:* <{google_doc_url}|Google Docを開く>"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"🤖 自動生成された要約 | 生成日時: <!date^{int(__import__('time').time())}^{{date_short_pretty}} {{time}}|エラー>"
                }
            ]
        }
    ]
    
    return {"blocks": blocks}

def _create_simple_slack_message(summary_text, google_doc_url):
    """
    シンプルなSlackメッセージを作成（Block Kit未対応の場合の代替）
    
    Args:
        summary_text (str): 要約テキスト
        google_doc_url (str): 元のGoogle DocのURL
    
    Returns:
        str: プレーンテキスト形式のメッセージ
    """
    message = f"""📝 **会議要約レポート**

{summary_text}

---
📄 **元の文書:** {google_doc_url}

🤖 自動生成された要約"""
    
    return message

def post_simple_message_to_slack(slack_token, channel_id, summary_text, google_doc_url):
    """
    シンプルなテキストメッセージをSlackに投稿（Block Kit未対応の場合の代替）
    
    Args:
        slack_token (str): Slackボットトークン
        channel_id (str): 投稿先のSlackチャンネルID
        summary_text (str): 生成AIによって要約されたテキスト
        google_doc_url (str): 元のGoogle DocのURL
    
    Returns:
        bool: 成功した場合はTrue、失敗した場合はFalse
    """
    try:
        # Slack WebClientの初期化
        client = WebClient(token=slack_token)
        
        # シンプルなメッセージの作成
        message = _create_simple_slack_message(summary_text, google_doc_url)
        
        logger.info(f"Slackチャンネル {channel_id} にシンプルメッセージを投稿します...")
        
        # Slackにメッセージを投稿
        response = client.chat_postMessage(
            channel=channel_id,
            text=message
        )
        
        if response["ok"]:
            logger.info(f"Slackへの投稿が成功しました。メッセージTS: {response['ts']}")
            return True
        else:
            logger.error(f"Slackへの投稿に失敗しました: {response}")
            return False
            
    except SlackApiError as e:
        logger.error(f"Slack API エラー: {e.response['error']}")
        return False
    except Exception as e:
        logger.error(f"Slack投稿でエラーが発生しました: {str(e)}")
        return False

def test_slack_connection(slack_token):
    """
    Slack接続をテストする
    
    Args:
        slack_token (str): Slackボットトークン
    
    Returns:
        bool: 接続に成功した場合はTrue、失敗した場合はFalse
    """
    try:
        client = WebClient(token=slack_token)
        
        # API接続テスト
        response = client.auth_test()
        
        if response["ok"]:
            logger.info(f"Slack接続テスト成功: {response['user']}")
            return True
        else:
            logger.error(f"Slack接続テスト失敗: {response}")
            return False
            
    except SlackApiError as e:
        logger.error(f"Slack API エラー: {e.response['error']}")
        return False
    except Exception as e:
        logger.error(f"Slack接続テストでエラーが発生しました: {str(e)}")
        return False

if __name__ == "__main__":
    # テスト実行用
    from config import load_environment_variables
    
    try:
        env_vars = load_environment_variables()
        
        # Slack接続テスト
        if test_slack_connection(env_vars['slack_bot_token']):
            print("Slack接続テストに成功しました。")
            
            # テスト用要約とURL
            test_summary = """## 📋 会議要約

### 🎯 主要議題
- プロジェクトの進捗確認
- 次期リリースの計画
- バグ修正の優先度

### 💡 決定事項
- 次期リリースを来月末に設定
- バグ修正を優先して対応

### 📝 次回アクション・タスク
- 田中さん: 設計書の更新（来週金曜まで）
- 佐藤さん: テストケースの作成（今週中）

### 📅 次回会議
- 来週木曜日 14:00～"""
            
            test_url = "https://docs.google.com/document/d/test_document_id"
            
            # テスト投稿
            success = post_summary_to_slack(
                env_vars['slack_bot_token'],
                env_vars['slack_channel_id'],
                test_summary,
                test_url
            )
            
            if success:
                print("テスト投稿に成功しました。")
            else:
                print("テスト投稿に失敗しました。")
        else:
            print("Slack接続テストに失敗しました。")
            
    except Exception as e:
        print(f"エラー: {e}")
