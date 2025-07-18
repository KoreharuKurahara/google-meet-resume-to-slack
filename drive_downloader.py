"""
Google Driveから最新の文字起こしファイルを取得するモジュール
"""
import os
import io
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from docx import Document
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_latest_transcript_from_drive(folder_id, credentials_path, target_directory):
    """
    Google Driveから最新の文字起こしファイルをダウンロードし、.md形式で保存
    
    Args:
        folder_id (str): 文字起こしファイルが保存されているGoogle DriveのフォルダID
        credentials_path (str): GoogleサービスアカウントキーのJSONファイルパス
        target_directory (str): ダウンロードしたファイルを保存するローカルのディレクトリパス
    
    Returns:
        tuple: (ダウンロードして保存した.mdファイルのパス, 元のGoogle DocのURL)
               失敗した場合は (None, None)
    """
    try:
        # 認証情報の設定
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=SCOPES
        )
        
        # Google Drive APIサービスの構築
        service = build('drive', 'v3', credentials=credentials)
        
        # 指定フォルダ内のファイルを取得（文字起こし関連のファイル名でフィルタ）
        query = f"'{folder_id}' in parents and (name contains '会議の録音' or name contains 'meeting' or name contains 'transcript')"
        
        results = service.files().list(
            q=query,
            orderBy='modifiedTime desc',  # 最新の更新日時でソート
            fields="files(id, name, mimeType, modifiedTime, webViewLink)"
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            logger.warning("指定されたフォルダに文字起こしファイルが見つかりません。")
            return None, None
        
        # 最新のファイルを選択
        latest_file = files[0]
        file_id = latest_file['id']
        file_name = latest_file['name']
        mime_type = latest_file['mimeType']
        web_view_link = latest_file['webViewLink']
        
        logger.info(f"最新のファイルを発見: {file_name}")
        
        # ターゲットディレクトリを作成
        os.makedirs(target_directory, exist_ok=True)
        
        # ファイル内容を取得
        content = _download_file_content(service, file_id, mime_type)
        
        if content is None:
            logger.error("ファイル内容の取得に失敗しました。")
            return None, None
        
        # .md形式で保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        md_filename = f"transcript_{timestamp}.md"
        md_filepath = os.path.join(target_directory, md_filename)
        
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(f"# 会議文字起こし\n\n")
            f.write(f"**元ファイル名:** {file_name}\n")
            f.write(f"**更新日時:** {latest_file['modifiedTime']}\n")
            f.write(f"**元のURL:** {web_view_link}\n\n")
            f.write("## 内容\n\n")
            f.write(content)
        
        logger.info(f"ファイルを保存しました: {md_filepath}")
        return md_filepath, web_view_link
        
    except Exception as e:
        logger.error(f"Google Driveからのダウンロードでエラーが発生しました: {str(e)}")
        return None, None

def _download_file_content(service, file_id, mime_type):
    """
    ファイルの内容をダウンロードしてテキストとして返す
    
    Args:
        service: Google Drive APIサービス
        file_id (str): ファイルID
        mime_type (str): ファイルのMIMEタイプ
    
    Returns:
        str: ファイルの内容（テキスト）
    """
    try:
        if mime_type == 'application/vnd.google-apps.document':
            # Google Docの場合はプレーンテキストとしてエクスポート
            request = service.files().export_media(fileId=file_id, mimeType='text/plain')
        elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            # .docxファイルの場合
            request = service.files().get_media(fileId=file_id)
        elif mime_type == 'text/plain':
            # .txtファイルの場合
            request = service.files().get_media(fileId=file_id)
        else:
            logger.warning(f"サポートされていないファイル形式: {mime_type}")
            return None
        
        file_io = io.BytesIO()
        downloader = MediaIoBaseDownload(file_io, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        file_io.seek(0)
        
        # ファイル形式に応じてテキストを抽出
        if mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            # .docxファイルからテキストを抽出
            document = Document(file_io)
            content = '\n'.join([paragraph.text for paragraph in document.paragraphs])
        else:
            # プレーンテキストファイル
            content = file_io.getvalue().decode('utf-8')
        
        return content
        
    except Exception as e:
        logger.error(f"ファイル内容の取得でエラーが発生しました: {str(e)}")
        return None

if __name__ == "__main__":
    # テスト実行用
    from config import load_environment_variables
    
    try:
        env_vars = load_environment_variables()
        
        file_path, doc_url = download_latest_transcript_from_drive(
            env_vars['google_drive_folder_id'],
            env_vars['google_credentials_path'],
            env_vars['target_directory']
        )
        
        if file_path:
            print(f"ダウンロード成功: {file_path}")
            print(f"元のURL: {doc_url}")
        else:
            print("ダウンロードに失敗しました。")
            
    except Exception as e:
        print(f"エラー: {e}")
