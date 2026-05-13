"""Google Docs API Tools for Content Management"""
from typing import Dict, Any, Optional, List
from googleapiclient.discovery import build
from ..auth import GoogleAuthManager
from ..config import ALL_SCOPES


def get_docs_service():
    """Get authenticated Google Docs service"""
    auth_manager = GoogleAuthManager(ALL_SCOPES)
    creds = auth_manager.get_credentials()
    return build('docs', 'v1', credentials=creds)


def get_drive_service():
    """Get authenticated Google Drive service for listing docs"""
    auth_manager = GoogleAuthManager(ALL_SCOPES)
    creds = auth_manager.get_credentials()
    return build('drive', 'v3', credentials=creds)


def read_document(document_id: str) -> Dict[str, Any]:
    """Read Google Doc content

    Args:
        document_id: Doc ID from URL (docs.google.com/document/d/{id})

    Returns: Dict with title, content, length, URL
    """
    try:
        service = get_docs_service()

        # Get the document
        document = service.documents().get(documentId=document_id).execute()

        # Extract title
        title = document.get('title', 'Untitled')

        # Extract text content
        content = []
        for element in document.get('body', {}).get('content', []):
            if 'paragraph' in element:
                for para_element in element['paragraph'].get('elements', []):
                    if 'textRun' in para_element:
                        text = para_element['textRun'].get('content', '')
                        content.append(text)

        full_content = ''.join(content)

        return {
            'status': 'success',
            'document_id': document_id,
            'title': title,
            'content': full_content,
            'content_length': len(full_content),
            'url': f'https://docs.google.com/document/d/{document_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'document_id': document_id
        }


def create_document(title: str, content: Optional[str] = None) -> Dict[str, Any]:
    """Create new Google Doc

    Args:
        title: Document title
        content: Optional initial content

    Returns: Dict with document_id, URL
    """
    try:
        service = get_docs_service()

        # Create the document
        document = service.documents().create(body={'title': title}).execute()
        document_id = document.get('documentId')

        # Add content if provided
        if content:
            requests = [{
                'insertText': {
                    'location': {
                        'index': 1,
                    },
                    'text': content
                }
            }]

            service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()

        return {
            'status': 'success',
            'document_id': document_id,
            'title': title,
            'url': f'https://docs.google.com/document/d/{document_id}/edit',
            'message': f'Created document: {title}'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'title': title
        }


def append_to_document(document_id: str, content: str) -> Dict[str, Any]:
    """Append content to Doc end

    Args:
        document_id: Doc ID
        content: Text to append

    Returns: Dict with status, URL
    """
    try:
        service = get_docs_service()

        # Get current document to find end index
        document = service.documents().get(documentId=document_id).execute()
        end_index = document.get('body', {}).get('content', [])[-1].get('endIndex', 1)

        # Append text
        requests = [{
            'insertText': {
                'location': {
                    'index': end_index - 1,
                },
                'text': content
            }
        }]

        service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

        return {
            'status': 'success',
            'document_id': document_id,
            'message': 'Content appended successfully',
            'url': f'https://docs.google.com/document/d/{document_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'document_id': document_id
        }


def replace_text_in_document(
    document_id: str,
    find_text: str,
    replace_text: str
) -> Dict[str, Any]:
    """Find and replace text in Doc

    Args:
        document_id: Doc ID
        find_text: Text to find
        replace_text: Replacement text

    Returns: Dict with replacements count, URL
    """
    try:
        service = get_docs_service()

        requests = [{
            'replaceAllText': {
                'containsText': {
                    'text': find_text,
                    'matchCase': True
                },
                'replaceText': replace_text
            }
        }]

        response = service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

        # Count replacements
        replacements = 0
        for reply in response.get('replies', []):
            if 'replaceAllText' in reply:
                replacements = reply['replaceAllText'].get('occurrencesChanged', 0)

        return {
            'status': 'success',
            'document_id': document_id,
            'replacements_made': replacements,
            'find_text': find_text,
            'replace_text': replace_text,
            'url': f'https://docs.google.com/document/d/{document_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'document_id': document_id
        }


def insert_text_at_position(
    document_id: str,
    text: str,
    index: int = 1
) -> Dict[str, Any]:
    """Insert text at specific position

    Args:
        document_id: Doc ID
        text: Text to insert
        index: Position (default 1 = beginning)

    Returns: Dict with status, URL
    """
    try:
        service = get_docs_service()

        requests = [{
            'insertText': {
                'location': {
                    'index': index,
                },
                'text': text
            }
        }]

        service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

        return {
            'status': 'success',
            'document_id': document_id,
            'message': f'Inserted text at position {index}',
            'url': f'https://docs.google.com/document/d/{document_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'document_id': document_id
        }


def list_google_docs(max_results: int = 10, query: Optional[str] = None) -> Dict[str, Any]:
    """List Google Docs in Drive

    Args:
        max_results: Max documents (default 10)
        query: Optional search filter

    Returns: Dict with documents list (id, name, URL, dates)
    """
    try:
        service = get_drive_service()

        # Build query
        mime_type = 'application/vnd.google-apps.document'
        q = f"mimeType='{mime_type}' and trashed=false"

        if query:
            q += f" and name contains '{query}'"

        # List documents
        results = service.files().list(
            q=q,
            pageSize=max_results,
            fields='files(id, name, createdTime, modifiedTime, webViewLink)',
            orderBy='modifiedTime desc'
        ).execute()

        documents = results.get('files', [])

        return {
            'status': 'success',
            'document_count': len(documents),
            'documents': [
                {
                    'id': doc['id'],
                    'name': doc['name'],
                    'url': doc.get('webViewLink', ''),
                    'created': doc.get('createdTime', ''),
                    'modified': doc.get('modifiedTime', '')
                }
                for doc in documents
            ]
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


def get_document_metadata(document_id: str) -> Dict[str, Any]:
    """Get Doc metadata

    Args:
        document_id: Doc ID

    Returns: Dict with title, word count, character count, URL
    """
    try:
        service = get_docs_service()
        document = service.documents().get(documentId=document_id).execute()

        # Count words
        content = []
        for element in document.get('body', {}).get('content', []):
            if 'paragraph' in element:
                for para_element in element['paragraph'].get('elements', []):
                    if 'textRun' in para_element:
                        text = para_element['textRun'].get('content', '')
                        content.append(text)

        full_content = ''.join(content)
        word_count = len(full_content.split())

        return {
            'status': 'success',
            'document_id': document_id,
            'title': document.get('title', 'Untitled'),
            'revision_id': document.get('revisionId', ''),
            'word_count': word_count,
            'character_count': len(full_content),
            'url': f'https://docs.google.com/document/d/{document_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'document_id': document_id
        }


def clear_document_content(document_id: str) -> Dict[str, Any]:
    """Clear all Doc content (keeps title)

    Args:
        document_id: Doc ID

    Returns: Dict with status, URL
    """
    try:
        service = get_docs_service()

        # Get current document
        document = service.documents().get(documentId=document_id).execute()
        content = document.get('body', {}).get('content', [])

        if len(content) > 1:
            # Delete all content except first element (which is structural)
            end_index = content[-1].get('endIndex', 1)

            requests = [{
                'deleteContentRange': {
                    'range': {
                        'startIndex': 1,
                        'endIndex': end_index - 1
                    }
                }
            }]

            service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()

        return {
            'status': 'success',
            'document_id': document_id,
            'message': 'Document content cleared',
            'url': f'https://docs.google.com/document/d/{document_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'document_id': document_id
        }
