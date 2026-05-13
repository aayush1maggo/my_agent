"""Google Slides API Tools for Presentation Management"""
from typing import Dict, Any, Optional, List
from googleapiclient.discovery import build
from ..auth import GoogleAuthManager
from ..config import ALL_SCOPES


def get_slides_service():
    """Get authenticated Google Slides service"""
    auth_manager = GoogleAuthManager(ALL_SCOPES)
    creds = auth_manager.get_credentials()
    return build('slides', 'v1', credentials=creds)


def get_drive_service():
    """Get authenticated Google Drive service for listing presentations"""
    auth_manager = GoogleAuthManager(ALL_SCOPES)
    creds = auth_manager.get_credentials()
    return build('drive', 'v3', credentials=creds)


def create_presentation(title: str) -> Dict[str, Any]:
    """Create new Google Slides presentation

    Args:
        title: Presentation title

    Returns: Dict with presentation_id, URL, title
    """
    try:
        service = get_slides_service()

        presentation = service.presentations().create(
            body={'title': title}
        ).execute()

        presentation_id = presentation.get('presentationId')

        return {
            'status': 'success',
            'presentation_id': presentation_id,
            'title': title,
            'url': f'https://docs.google.com/presentation/d/{presentation_id}/edit',
            'message': f'Created presentation: {title}'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'title': title
        }


def get_presentation(presentation_id: str) -> Dict[str, Any]:
    """Get presentation details and structure

    Args:
        presentation_id: Presentation ID from URL (docs.google.com/presentation/d/{id})

    Returns: Dict with presentation metadata, slide count, slides info
    """
    try:
        service = get_slides_service()

        presentation = service.presentations().get(
            presentationId=presentation_id
        ).execute()

        title = presentation.get('title', 'Untitled')
        slides = presentation.get('slides', [])

        slides_info = []
        for idx, slide in enumerate(slides):
            slide_id = slide.get('objectId')
            slide_elements = slide.get('pageElements', [])

            # Extract all text from slide (not just a preview)
            text_content = []
            for element in slide_elements:
                if 'shape' in element:
                    shape = element['shape']
                    if 'text' in shape:
                        for text_element in shape['text'].get('textElements', []):
                            if 'textRun' in text_element:
                                text_content.append(text_element['textRun'].get('content', ''))

            full_text = ''.join(text_content)

            slides_info.append({
                'slide_number': idx + 1,
                'object_id': slide_id,
                'element_count': len(slide_elements),
                # Short snippet for quick scanning
                'text_preview': full_text[:200],
                # Complete concatenated text for detailed analysis
                'full_text': full_text,
            })

        return {
            'status': 'success',
            'presentation_id': presentation_id,
            'title': title,
            'slide_count': len(slides),
            'slides': slides_info,
            'url': f'https://docs.google.com/presentation/d/{presentation_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'presentation_id': presentation_id
        }


def add_slide(
    presentation_id: str,
    position: Optional[int] = None,
    layout: str = 'BLANK'
) -> Dict[str, Any]:
    """Add new slide to presentation

    Args:
        presentation_id: Presentation ID
        position: Optional position to insert slide (0-indexed). If None, adds to end
        layout: Slide layout - 'BLANK', 'TITLE', 'TITLE_AND_BODY', 'TITLE_ONLY', etc.

    Returns: Dict with new slide object_id, position
    """
    try:
        service = get_slides_service()

        # Get presentation to find layout and insertion index
        presentation = service.presentations().get(
            presentationId=presentation_id
        ).execute()

        # Generate unique object ID
        import uuid
        slide_id = f'slide_{uuid.uuid4().hex[:8]}'

        # Prepare request
        requests = [{
            'createSlide': {
                'objectId': slide_id,
                'slideLayoutReference': {
                    'predefinedLayout': layout
                }
            }
        }]

        # Add insertion index if position specified
        if position is not None:
            requests[0]['createSlide']['insertionIndex'] = position

        # Execute batch update
        response = service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()

        return {
            'status': 'success',
            'presentation_id': presentation_id,
            'slide_id': slide_id,
            'position': position if position is not None else len(presentation.get('slides', [])),
            'layout': layout,
            'url': f'https://docs.google.com/presentation/d/{presentation_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'presentation_id': presentation_id
        }


def delete_slide(presentation_id: str, slide_id: str) -> Dict[str, Any]:
    """Delete slide from presentation

    Args:
        presentation_id: Presentation ID
        slide_id: Slide object ID to delete

    Returns: Dict with status
    """
    try:
        service = get_slides_service()

        requests = [{
            'deleteObject': {
                'objectId': slide_id
            }
        }]

        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()

        return {
            'status': 'success',
            'presentation_id': presentation_id,
            'deleted_slide_id': slide_id,
            'message': 'Slide deleted successfully',
            'url': f'https://docs.google.com/presentation/d/{presentation_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'presentation_id': presentation_id
        }


def add_text_to_slide(
    presentation_id: str,
    slide_id: str,
    text: str,
    x: Optional[float] = None,
    y: Optional[float] = None,
    width: Optional[float] = None,
    height: Optional[float] = None
) -> Dict[str, Any]:
    """Add text box to slide

    Args:
        presentation_id: Presentation ID
        slide_id: Slide object ID
        text: Text content to add
        x: X coordinate in points (1 point = 1/72 inch), default 100
        y: Y coordinate in points, default 100
        width: Text box width in points, default 400
        height: Text box height in points, default 100

    Returns: Dict with text_box_id, status
    """
    try:
        service = get_slides_service()

        # Set defaults
        x = x if x is not None else 100
        y = y if y is not None else 100
        width = width if width is not None else 400
        height = height if height is not None else 100

        # Generate unique object ID for text box
        import uuid
        text_box_id = f'textbox_{uuid.uuid4().hex[:8]}'

        # Convert points to EMU (English Metric Units - Slides API uses EMU)
        # 1 point = 12700 EMU
        emu_x = int(x * 12700)
        emu_y = int(y * 12700)
        emu_width = int(width * 12700)
        emu_height = int(height * 12700)

        requests = [
            # Create text box
            {
                'createShape': {
                    'objectId': text_box_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'width': {'magnitude': emu_width, 'unit': 'EMU'},
                            'height': {'magnitude': emu_height, 'unit': 'EMU'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': emu_x,
                            'translateY': emu_y,
                            'unit': 'EMU'
                        }
                    }
                }
            },
            # Insert text
            {
                'insertText': {
                    'objectId': text_box_id,
                    'text': text,
                    'insertionIndex': 0
                }
            }
        ]

        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()

        return {
            'status': 'success',
            'presentation_id': presentation_id,
            'slide_id': slide_id,
            'text_box_id': text_box_id,
            'text_length': len(text),
            'url': f'https://docs.google.com/presentation/d/{presentation_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'presentation_id': presentation_id
        }


def add_title_to_slide(
    presentation_id: str,
    slide_id: str,
    title: str,
    subtitle: Optional[str] = None
) -> Dict[str, Any]:
    """Add title (and optional subtitle) to slide

    Args:
        presentation_id: Presentation ID
        slide_id: Slide object ID
        title: Title text
        subtitle: Optional subtitle text

    Returns: Dict with status
    """
    try:
        service = get_slides_service()

        # Get slide to find title and subtitle placeholders
        presentation = service.presentations().get(
            presentationId=presentation_id
        ).execute()

        # Find the specific slide
        slide = None
        for s in presentation.get('slides', []):
            if s.get('objectId') == slide_id:
                slide = s
                break

        if not slide:
            return {
                'status': 'error',
                'error': f'Slide {slide_id} not found',
                'presentation_id': presentation_id
            }

        requests = []

        # Find title and subtitle placeholders
        for element in slide.get('pageElements', []):
            if 'shape' in element:
                shape = element['shape']
                placeholder_type = shape.get('placeholder', {}).get('type')

                if placeholder_type == 'TITLE' or placeholder_type == 'CENTERED_TITLE':
                    # Insert title
                    requests.append({
                        'insertText': {
                            'objectId': element['objectId'],
                            'text': title,
                            'insertionIndex': 0
                        }
                    })

                if subtitle and placeholder_type == 'SUBTITLE':
                    # Insert subtitle
                    requests.append({
                        'insertText': {
                            'objectId': element['objectId'],
                            'text': subtitle,
                            'insertionIndex': 0
                        }
                    })

        if requests:
            service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={'requests': requests}
            ).execute()

            return {
                'status': 'success',
                'presentation_id': presentation_id,
                'slide_id': slide_id,
                'title': title,
                'subtitle': subtitle,
                'url': f'https://docs.google.com/presentation/d/{presentation_id}/edit'
            }
        else:
            return {
                'status': 'warning',
                'message': 'No title/subtitle placeholders found on slide',
                'presentation_id': presentation_id,
                'slide_id': slide_id
            }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'presentation_id': presentation_id
        }


def add_bullet_points_to_slide(
    presentation_id: str,
    slide_id: str,
    bullet_points: List[str],
    x: Optional[float] = None,
    y: Optional[float] = None,
    width: Optional[float] = None,
    height: Optional[float] = None
) -> Dict[str, Any]:
    """Add bullet point list to slide

    Args:
        presentation_id: Presentation ID
        slide_id: Slide object ID
        bullet_points: List of bullet point strings
        x: X coordinate in points, default 100
        y: Y coordinate in points, default 150
        width: Text box width in points, default 500
        height: Text box height in points, default 300

    Returns: Dict with status
    """
    try:
        service = get_slides_service()

        # Set defaults
        x = x if x is not None else 100
        y = y if y is not None else 150
        width = width if width is not None else 500
        height = height if height is not None else 300

        # Generate unique object ID
        import uuid
        text_box_id = f'textbox_{uuid.uuid4().hex[:8]}'

        # Convert points to EMU
        emu_x = int(x * 12700)
        emu_y = int(y * 12700)
        emu_width = int(width * 12700)
        emu_height = int(height * 12700)

        # Combine bullet points with newlines
        text_content = '\n'.join(bullet_points)

        requests = [
            # Create text box
            {
                'createShape': {
                    'objectId': text_box_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'width': {'magnitude': emu_width, 'unit': 'EMU'},
                            'height': {'magnitude': emu_height, 'unit': 'EMU'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': emu_x,
                            'translateY': emu_y,
                            'unit': 'EMU'
                        }
                    }
                }
            },
            # Insert text
            {
                'insertText': {
                    'objectId': text_box_id,
                    'text': text_content,
                    'insertionIndex': 0
                }
            }
        ]

        # Add bullet formatting for each line
        char_index = 0
        for i, point in enumerate(bullet_points):
            point_length = len(point)
            requests.append({
                'createParagraphBullets': {
                    'objectId': text_box_id,
                    'textRange': {
                        'type': 'FIXED_RANGE',
                        'startIndex': char_index,
                        'endIndex': char_index + point_length
                    },
                    'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
                }
            })
            char_index += point_length + 1  # +1 for newline

        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()

        return {
            'status': 'success',
            'presentation_id': presentation_id,
            'slide_id': slide_id,
            'text_box_id': text_box_id,
            'bullet_count': len(bullet_points),
            'url': f'https://docs.google.com/presentation/d/{presentation_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'presentation_id': presentation_id
        }


def add_image_to_slide(
    presentation_id: str,
    slide_id: str,
    image_url: str,
    x: Optional[float] = None,
    y: Optional[float] = None,
    width: Optional[float] = None,
    height: Optional[float] = None
) -> Dict[str, Any]:
    """Add image to slide from URL

    Args:
        presentation_id: Presentation ID
        slide_id: Slide object ID
        image_url: Public URL of image to insert
        x: X coordinate in points, default 100
        y: Y coordinate in points, default 100
        width: Image width in points, default 400
        height: Image height in points, default 300

    Returns: Dict with image_id, status
    """
    try:
        service = get_slides_service()

        # Set defaults
        x = x if x is not None else 100
        y = y if y is not None else 100
        width = width if width is not None else 400
        height = height if height is not None else 300

        # Generate unique object ID
        import uuid
        image_id = f'image_{uuid.uuid4().hex[:8]}'

        # Convert points to EMU
        emu_x = int(x * 12700)
        emu_y = int(y * 12700)
        emu_width = int(width * 12700)
        emu_height = int(height * 12700)

        requests = [{
            'createImage': {
                'objectId': image_id,
                'url': image_url,
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width': {'magnitude': emu_width, 'unit': 'EMU'},
                        'height': {'magnitude': emu_height, 'unit': 'EMU'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': emu_x,
                        'translateY': emu_y,
                        'unit': 'EMU'
                    }
                }
            }
        }]

        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()

        return {
            'status': 'success',
            'presentation_id': presentation_id,
            'slide_id': slide_id,
            'image_id': image_id,
            'image_url': image_url,
            'url': f'https://docs.google.com/presentation/d/{presentation_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'presentation_id': presentation_id
        }


def replace_text_in_presentation(
    presentation_id: str,
    find_text: str,
    replace_text: str,
    match_case: bool = True
) -> Dict[str, Any]:
    """Find and replace text across entire presentation

    Args:
        presentation_id: Presentation ID
        find_text: Text to find
        replace_text: Replacement text
        match_case: Whether to match case (default True)

    Returns: Dict with replacement count, status
    """
    try:
        service = get_slides_service()

        requests = [{
            'replaceAllText': {
                'containsText': {
                    'text': find_text,
                    'matchCase': match_case
                },
                'replaceText': replace_text
            }
        }]

        response = service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()

        # Count replacements
        replacements = 0
        for reply in response.get('replies', []):
            if 'replaceAllText' in reply:
                replacements = reply['replaceAllText'].get('occurrencesChanged', 0)

        return {
            'status': 'success',
            'presentation_id': presentation_id,
            'replacements_made': replacements,
            'find_text': find_text,
            'replace_text': replace_text,
            'url': f'https://docs.google.com/presentation/d/{presentation_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'presentation_id': presentation_id
        }


def list_presentations(max_results: int = 10, query: Optional[str] = None) -> Dict[str, Any]:
    """List Google Slides presentations in Drive

    Args:
        max_results: Max presentations to return (default 10)
        query: Optional search filter for presentation name

    Returns: Dict with presentations list (id, name, URL, dates)
    """
    try:
        service = get_drive_service()

        # Build query
        mime_type = 'application/vnd.google-apps.presentation'
        q = f"mimeType='{mime_type}' and trashed=false"

        if query:
            q += f" and name contains '{query}'"

        # List presentations
        results = service.files().list(
            q=q,
            pageSize=max_results,
            fields='files(id, name, createdTime, modifiedTime, webViewLink)',
            orderBy='modifiedTime desc'
        ).execute()

        presentations = results.get('files', [])

        return {
            'status': 'success',
            'presentation_count': len(presentations),
            'presentations': [
                {
                    'id': pres['id'],
                    'name': pres['name'],
                    'url': pres.get('webViewLink', ''),
                    'created': pres.get('createdTime', ''),
                    'modified': pres.get('modifiedTime', '')
                }
                for pres in presentations
            ]
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


def get_slide_thumbnail(
    presentation_id: str,
    slide_id: str,
    thumbnail_size: str = 'LARGE'
) -> Dict[str, Any]:
    """Get thumbnail image URL for a specific slide

    Args:
        presentation_id: Presentation ID
        slide_id: Slide object ID
        thumbnail_size: Size of thumbnail - 'SMALL', 'MEDIUM', 'LARGE' (default LARGE)

    Returns: Dict with thumbnail URL
    """
    try:
        service = get_slides_service()

        # Map size to actual thumbnail properties
        size_map = {
            'SMALL': 'SMALL',
            'MEDIUM': 'MEDIUM',
            'LARGE': 'LARGE'
        }

        thumbnail = service.presentations().pages().getThumbnail(
            presentationId=presentation_id,
            pageObjectId=slide_id,
            thumbnailProperties_thumbnailSize=size_map.get(thumbnail_size, 'LARGE')
        ).execute()

        return {
            'status': 'success',
            'presentation_id': presentation_id,
            'slide_id': slide_id,
            'thumbnail_url': thumbnail.get('contentUrl', ''),
            'size': thumbnail_size
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'presentation_id': presentation_id,
            'slide_id': slide_id
        }


def duplicate_slide(
    presentation_id: str,
    slide_id: str,
    insertion_index: Optional[int] = None
) -> Dict[str, Any]:
    """Duplicate an existing slide

    Args:
        presentation_id: Presentation ID
        slide_id: Slide object ID to duplicate
        insertion_index: Optional position to insert duplicated slide

    Returns: Dict with new slide ID and status
    """
    try:
        service = get_slides_service()

        requests = [{
            'duplicateObject': {
                'objectId': slide_id
            }
        }]

        # Add insertion index if specified
        if insertion_index is not None:
            requests[0]['duplicateObject']['objectIds'] = {
                slide_id: f'{slide_id}_copy'
            }

        response = service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()

        # Get duplicated object ID from response
        new_slide_id = None
        for reply in response.get('replies', []):
            if 'duplicateObject' in reply:
                new_slide_id = reply['duplicateObject'].get('objectId')

        return {
            'status': 'success',
            'presentation_id': presentation_id,
            'original_slide_id': slide_id,
            'new_slide_id': new_slide_id,
            'url': f'https://docs.google.com/presentation/d/{presentation_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'presentation_id': presentation_id
        }


def add_table_to_slide(
    presentation_id: str,
    slide_id: str,
    rows: int,
    columns: int,
    x: Optional[float] = None,
    y: Optional[float] = None,
    width: Optional[float] = None,
    height: Optional[float] = None
) -> Dict[str, Any]:
    """Add table to slide

    Args:
        presentation_id: Presentation ID
        slide_id: Slide object ID
        rows: Number of table rows
        columns: Number of table columns
        x: X coordinate in points, default 100
        y: Y coordinate in points, default 100
        width: Table width in points, default 500
        height: Table height in points, default 300

    Returns: Dict with table_id and status
    """
    try:
        service = get_slides_service()

        # Set defaults
        x = x if x is not None else 100
        y = y if y is not None else 100
        width = width if width is not None else 500
        height = height if height is not None else 300

        # Generate unique object ID
        import uuid
        table_id = f'table_{uuid.uuid4().hex[:8]}'

        # Convert points to EMU
        emu_x = int(x * 12700)
        emu_y = int(y * 12700)
        emu_width = int(width * 12700)
        emu_height = int(height * 12700)

        requests = [{
            'createTable': {
                'objectId': table_id,
                'rows': rows,
                'columns': columns,
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width': {'magnitude': emu_width, 'unit': 'EMU'},
                        'height': {'magnitude': emu_height, 'unit': 'EMU'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': emu_x,
                        'translateY': emu_y,
                        'unit': 'EMU'
                    }
                }
            }
        }]

        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()

        return {
            'status': 'success',
            'presentation_id': presentation_id,
            'slide_id': slide_id,
            'table_id': table_id,
            'rows': rows,
            'columns': columns,
            'url': f'https://docs.google.com/presentation/d/{presentation_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'presentation_id': presentation_id
        }


def update_table_cell(
    presentation_id: str,
    table_id: str,
    row: int,
    column: int,
    text: str
) -> Dict[str, Any]:
    """Update text in a table cell

    Args:
        presentation_id: Presentation ID
        table_id: Table object ID
        row: Row index (0-based)
        column: Column index (0-based)
        text: Text to insert in cell

    Returns: Dict with status
    """
    try:
        service = get_slides_service()

        # Get presentation to find cell object ID
        presentation = service.presentations().get(
            presentationId=presentation_id
        ).execute()

        # Find the table and get cell ID
        cell_id = None
        for slide in presentation.get('slides', []):
            for element in slide.get('pageElements', []):
                if element.get('objectId') == table_id and 'table' in element:
                    table = element['table']
                    if row < len(table.get('tableRows', [])):
                        cells = table['tableRows'][row].get('tableCells', [])
                        if column < len(cells):
                            cell_id = cells[column].get('tableCellProperties', {}).get('tableCellBackgroundFill', {}).get('solidFill', {}).get('color', {}).get('rgbColor')
                            # Actually get the text element objectId
                            for cell_element in cells[column].get('text', {}).get('textElements', []):
                                cell_id = cells[column].get('location', {}).get('rowIndex')
                    break

        # For simplicity, we'll use a different approach - delete and insert text
        requests = [
            {
                'deleteText': {
                    'objectId': table_id,
                    'cellLocation': {
                        'rowIndex': row,
                        'columnIndex': column
                    },
                    'textRange': {
                        'type': 'ALL'
                    }
                }
            },
            {
                'insertText': {
                    'objectId': table_id,
                    'cellLocation': {
                        'rowIndex': row,
                        'columnIndex': column
                    },
                    'text': text,
                    'insertionIndex': 0
                }
            }
        ]

        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()

        return {
            'status': 'success',
            'presentation_id': presentation_id,
            'table_id': table_id,
            'row': row,
            'column': column,
            'text': text,
            'url': f'https://docs.google.com/presentation/d/{presentation_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'presentation_id': presentation_id
        }
