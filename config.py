"""
環境変数の設定と読み込み
"""
import os
from dotenv import load_dotenv

def load_environment_variables():
    """
    .envファイルから環境変数を読み込む
    
    Returns:
        dict: 環境変数の辞書
    """
    load_dotenv()
    
    env_vars = {
        'google_credentials_path': os.getenv('GOOGLE_CREDENTIALS_PATH'),
        'google_drive_folder_id': os.getenv('GOOGLE_DRIVE_FOLDER_ID'),
        'slack_bot_token': os.getenv('SLACK_BOT_TOKEN'),
        'slack_channel_id': os.getenv('SLACK_CHANNEL_ID'),
        'google_ai_api_key': os.getenv('GOOGLE_AI_API_KEY'),
        'ai_model_name': os.getenv('AI_MODEL_NAME', 'gemini-pro'),
        'target_directory': os.getenv('TARGET_DIRECTORY', './downloads')
    }
    
    # 必須の環境変数をチェック
    required_vars = [
        'google_credentials_path',
        'google_drive_folder_id', 
        'slack_bot_token',
        'slack_channel_id',
        'google_ai_api_key'
    ]
    
    missing_vars = [var for var in required_vars if not env_vars[var]]
    if missing_vars:
        raise ValueError(f"以下の環境変数が設定されていません: {', '.join(missing_vars)}")
    
    return env_vars

if __name__ == "__main__":
    try:
        env_vars = load_environment_variables()
        print("環境変数の読み込みが完了しました。")
        for key, value in env_vars.items():
            if 'token' in key or 'key' in key:
                print(f"{key}: {'*' * 10}")
            else:
                print(f"{key}: {value}")
    except ValueError as e:
        print(f"エラー: {e}")
