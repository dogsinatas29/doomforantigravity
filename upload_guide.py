from gdrive_mcp import get_gdrive_service
from googleapiclient.http import MediaIoBaseUpload
import io

def upload_guide():
    service = get_gdrive_service()
    
    # 0. 'AI Studio' 폴더 삭제 (있다면)
    old_folder_name = 'AI Studio'
    query = f"name = '{old_folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    old_folders = results.get('files', [])
    
    for folder in old_folders:
        try:
            service.files().delete(fileId=folder['id']).execute()
            print(f"Deleted old folder '{old_folder_name}' with ID: {folder['id']}")
        except Exception as e:
            print(f"Failed to delete '{old_folder_name}': {e}")

    # 1. 'GOOGLE AI Studio' 폴더 찾기
    folder_name = 'GOOGLE AI Studio'
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get('files', [])
    
    if not folders:
        # 폴더가 없으면 생성
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        folder_id = folder.get('id')
        print(f"Created folder '{folder_name}' with ID: {folder_id}")
    else:
        folder_id = folders[0].get('id')
        print(f"Found folder '{folder_name}' with ID: {folder_id}")

    # 2. GUIDE.md 파일 준비
    file_name = 'GUIDE.md'
    content = """# 📝 AI Studio 프로젝트 문서화 기본 지침

본 문서는 `AI Studio` 폴더 내의 ECS 기반 로그라이크 엔진 소스 코드를 분석하고 관리하기 위한 공식 가이드라인입니다.

---

## 🚩 핵심 원칙 (Core Principles)
1. **ECS 구조 철저 분석**: 엔티티(Entity), 컴포넌트(Component), 시스템(System)의 관계를 명확히 정의한다.
2. **Data-Driven 설계**: `items.csv` 등 외부 데이터와 코드 간의 매핑 로직을 최우선으로 문서화한다. (하드코딩 배제 원칙)
3. **기획자 친화적 요약**: 모든 기술 문서 상단에는 기획자가 즉시 파악할 수 있는 3줄 요약을 포함한다.

---

## 📂 주요 분석 대상 파일
- **`items.csv`**: 아이템 속성 및 밸런스 데이터 규격.
- **`ecs.py` & `components.py`**: 데이터 구조 및 객체 정의.
- **`systems.py`**: 발사체 로직, 충돌 판정 등 핵심 게임 시스템.
- **`main.py`**: 엔진 초기화 및 전체 루프 구조.

---

## 📄 문서 작성 표준 템플릿
모든 세부 분석 문서는 다음 형식을 준수한다.
1. **[요약]**: 기획자용 3줄 핵심 요약.
2. **[핵심 로직]**: 주요 함수 및 작동 알고리즘 설명.
3. **[데이터 연결]**: 참조하는 CSV 컬럼 및 컴포넌트 변수명.
4. **[링크]**: 상위 `PROJECT_META.md`로의 상대 경로 링크.

---
**작성일**: 2024-05-24
**작성자**: 프로젝트 기획자
"""
    
    # 3. 파일 업로드 (기존 파일 있으면 업데이트, 없으면 생성)
    # 같은 이름의 파일이 있는지 확인
    query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype='text/markdown', resumable=True)

    if files:
        # 업데이트
        file_id = files[0].get('id')
        service.files().update(fileId=file_id, media_body=media).execute()
        print(f"Updated '{file_name}' (ID: {file_id}) in '{folder_name}'.")
    else:
        # 새로 생성
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"Created '{file_name}' in '{folder_name}'.")

if __name__ == "__main__":
    upload_guide()
