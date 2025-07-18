"""
生成AIを用いた文字起こしテキストの要約モジュール
"""
import os
import logging
import google.generativeai as genai

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def summarize_transcript_with_ai(file_path, ai_api_key, model_name="gemini-pro"):
    """
    ダウンロードした文字起こしファイルからテキストを読み込み、生成AIを用いて要約
    
    Args:
        file_path (str): .md形式で保存された文字起こしファイルのパス
        ai_api_key (str): 生成AIサービスのAPIキー
        model_name (str, optional): 使用する生成AIのモデル名
    
    Returns:
        str: 生成AIによって要約されたテキスト、失敗した場合はNone
    """
    try:
        # ファイルの存在確認
        if not os.path.exists(file_path):
            logger.error(f"ファイルが見つかりません: {file_path}")
            return None
        
        # ファイルからテキストを読み込み
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            logger.error("ファイルの内容が空です。")
            return None
        
        # Google Generative AI APIの設定
        genai.configure(api_key=ai_api_key)
        model = genai.GenerativeModel(model_name)
        
        # 要約プロンプトの作成
        prompt = _create_summary_prompt(content)
        
        logger.info("生成AIによる要約を開始します...")
        
        # 生成AIで要約を生成
        response = model.generate_content(prompt)
        
        if response.text:
            logger.info("要約が正常に生成されました。")
            return response.text.strip()
        else:
            logger.error("生成AIからの応答が空です。")
            return None
            
    except Exception as e:
        logger.error(f"要約処理でエラーが発生しました: {str(e)}")
        return None

def _create_summary_prompt(content):
    """
    要約用のプロンプトを作成
    
    Args:
        content (str): 要約対象のテキスト
    
    Returns:
        str: 要約用プロンプト
    """
    prompt = f"""
以下は会議の文字起こしです。この内容を以下の形式で要約してください：

【要約形式】
## 📋 会議要約

### 🎯 主要議題
- 重要なポイントを3-5点で簡潔にまとめてください

### 💡 決定事項
- 会議で決定された事項があれば箇条書きで記載してください
- 決定事項がない場合は「なし」と記載してください

### 📝 次回アクション・タスク
- 今後実行すべきアクションやタスクがあれば担当者と期限を含めて記載してください
- アクションがない場合は「なし」と記載してください

### 📅 次回会議
- 次回会議の予定があれば記載してください
- 予定がない場合は「未定」と記載してください

【文字起こし内容】
{content}

上記の内容を読みやすく、要点を整理して要約してください。専門用語がある場合は簡潔に説明を加えてください。
"""
    return prompt

def _create_summary_prompt_openai_style(content):
    """
    OpenAI API用の要約プロンプト（参考用）
    
    Args:
        content (str): 要約対象のテキスト
    
    Returns:
        str: 要約用プロンプト
    """
    prompt = f"""
Please summarize the following meeting transcript in Japanese. Format the summary as follows:

## 📋 会議要約

### 🎯 主要議題
[List 3-5 key points discussed]

### 💡 決定事項
[List decisions made, or state "なし" if none]

### 📝 次回アクション・タスク
[List action items with assignees and deadlines, or state "なし" if none]

### 📅 次回会議
[Next meeting details, or state "未定" if not scheduled]

Transcript:
{content}

Make the summary clear, concise, and well-organized in Japanese.
"""
    return prompt

# OpenAI APIを使用する場合の実装例（参考用）
def summarize_transcript_with_openai(file_path, openai_api_key, model_name="gpt-3.5-turbo"):
    """
    OpenAI APIを使用した要約（参考実装）
    
    Args:
        file_path (str): .md形式で保存された文字起こしファイルのパス
        openai_api_key (str): OpenAI APIキー
        model_name (str, optional): 使用するOpenAIのモデル名
    
    Returns:
        str: 生成AIによって要約されたテキスト、失敗した場合はNone
    """
    try:
        # この実装にはopenaiライブラリが必要です
        # pip install openai
        
        import openai
        
        # ファイルからテキストを読み込み
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            logger.error("ファイルの内容が空です。")
            return None
        
        # OpenAI APIの設定
        openai.api_key = openai_api_key
        
        # 要約プロンプトの作成
        prompt = _create_summary_prompt_openai_style(content)
        
        logger.info("OpenAI APIによる要約を開始します...")
        
        # OpenAI APIで要約を生成
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "あなたは会議の文字起こしを要約する専門家です。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        if response.choices[0].message.content:
            logger.info("要約が正常に生成されました。")
            return response.choices[0].message.content.strip()
        else:
            logger.error("OpenAI APIからの応答が空です。")
            return None
            
    except Exception as e:
        logger.error(f"OpenAI API要約処理でエラーが発生しました: {str(e)}")
        return None

if __name__ == "__main__":
    # テスト実行用
    from config import load_environment_variables
    
    try:
        env_vars = load_environment_variables()
        
        # テスト用のファイルパスを指定（実際にはdownload_latest_transcript_from_driveの結果を使用）
        test_file_path = os.path.join(env_vars['target_directory'], "test_transcript.md")
        
        # テスト用ファイルが存在しない場合は作成
        if not os.path.exists(test_file_path):
            print("テスト用ファイルが見つかりません。drive_downloader.pyを先に実行してください。")
        else:
            summary = summarize_transcript_with_ai(
                test_file_path,
                env_vars['google_ai_api_key'],
                env_vars['ai_model_name']
            )
            
            if summary:
                print("要約結果:")
                print(summary)
            else:
                print("要約に失敗しました。")
                
    except Exception as e:
        print(f"エラー: {e}")
