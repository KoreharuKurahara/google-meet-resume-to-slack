"""
Google Meet文字起こし自動要約・Slack投稿アプリケーション
メイン処理モジュール
"""
import sys
import logging
from datetime import datetime

from config import load_environment_variables
from drive_downloader import download_latest_transcript_from_drive
from ai_summarizer import summarize_transcript_with_ai
from slack_poster import post_summary_to_slack, test_slack_connection

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('meeting_summary.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """
    メイン処理：Google Driveから文字起こしを取得し、要約してSlackに投稿
    """
    try:
        logger.info("=== Google Meet文字起こし要約・Slack投稿処理を開始 ===")
        
        # 1. 環境変数の読み込み
        logger.info("環境変数を読み込み中...")
        env_vars = load_environment_variables()
        logger.info("環境変数の読み込みが完了しました。")
        
        # 2. Slack接続テスト
        logger.info("Slack接続をテスト中...")
        if not test_slack_connection(env_vars['slack_bot_token']):
            logger.error("Slack接続テストに失敗しました。処理を中止します。")
            return False
        logger.info("Slack接続テストに成功しました。")
        
        # 3. Google Driveから最新の文字起こしファイルをダウンロード
        logger.info("Google Driveから最新の文字起こしファイルをダウンロード中...")
        file_path, google_doc_url = download_latest_transcript_from_drive(
            env_vars['google_drive_folder_id'],
            env_vars['google_credentials_path'],
            env_vars['target_directory']
        )
        
        if not file_path or not google_doc_url:
            logger.error("Google Driveからのファイルダウンロードに失敗しました。処理を中止します。")
            return False
        
        logger.info(f"ファイルダウンロードが完了しました: {file_path}")
        
        # 4. 生成AIで要約を生成
        logger.info("生成AIを用いて要約を生成中...")
        summary_text = summarize_transcript_with_ai(
            file_path,
            env_vars['google_ai_api_key'],
            env_vars['ai_model_name']
        )
        
        if not summary_text:
            logger.error("要約の生成に失敗しました。処理を中止します。")
            return False
        
        logger.info("要約の生成が完了しました。")
        logger.debug(f"要約内容: {summary_text[:200]}...")  # 最初の200文字のみログ出力
        
        # 5. Slackに要約を投稿
        logger.info("Slackに要約を投稿中...")
        success = post_summary_to_slack(
            env_vars['slack_bot_token'],
            env_vars['slack_channel_id'],
            summary_text,
            google_doc_url
        )
        
        if not success:
            logger.error("Slackへの投稿に失敗しました。")
            return False
        
        logger.info("Slackへの投稿が完了しました。")
        logger.info("=== 処理が正常に完了しました ===")
        return True
        
    except Exception as e:
        logger.error(f"メイン処理でエラーが発生しました: {str(e)}")
        return False

def run_with_error_handling():
    """
    エラーハンドリングを含む実行ラッパー
    """
    try:
        success = main()
        if success:
            print("✅ 処理が正常に完了しました。")
            sys.exit(0)
        else:
            print("❌ 処理中にエラーが発生しました。ログを確認してください。")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("ユーザーによって処理が中断されました。")
        print("⚠️ 処理が中断されました。")
        sys.exit(2)
        
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {str(e)}")
        print(f"💥 予期しないエラーが発生しました: {e}")
        sys.exit(3)

def test_individual_components():
    """
    各コンポーネントの個別テスト（デバッグ用）
    """
    try:
        logger.info("=== 個別コンポーネントテストを開始 ===")
        
        # 環境変数テスト
        logger.info("1. 環境変数テスト...")
        env_vars = load_environment_variables()
        print("✅ 環境変数の読み込み: 成功")
        
        # Slack接続テスト
        logger.info("2. Slack接続テスト...")
        if test_slack_connection(env_vars['slack_bot_token']):
            print("✅ Slack接続: 成功")
        else:
            print("❌ Slack接続: 失敗")
            return
        
        # 残りのテストは実際のファイルが必要なため、コメントアウト
        logger.info("3. その他のテストは実際のファイルダウンロード後に実行してください。")
        
        logger.info("=== 個別コンポーネントテスト完了 ===")
        
    except Exception as e:
        logger.error(f"個別テストでエラーが発生しました: {str(e)}")
        print(f"❌ テストでエラーが発生しました: {e}")

if __name__ == "__main__":
    """
    スクリプトの直接実行
    
    使用例:
        python main.py                    # 通常実行
        python main.py --test            # 個別コンポーネントテスト
    """
    
    # コマンドライン引数の処理
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_individual_components()
    else:
        run_with_error_handling()
