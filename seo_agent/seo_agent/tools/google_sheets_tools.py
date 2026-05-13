"""Google Sheets API Tools for Data Management and Tracking"""
from typing import Dict, Any, Optional, List
from googleapiclient.discovery import build
from ..auth import GoogleAuthManager
from ..config import ALL_SCOPES


def get_sheets_service():
    """Get authenticated Google Sheets service"""
    auth_manager = GoogleAuthManager(ALL_SCOPES)
    creds = auth_manager.get_credentials()
    return build('sheets', 'v4', credentials=creds)


def get_drive_service():
    """Get authenticated Google Drive service for listing sheets"""
    auth_manager = GoogleAuthManager(ALL_SCOPES)
    creds = auth_manager.get_credentials()
    return build('drive', 'v3', credentials=creds)


def read_sheet(
    spreadsheet_id: str,
    range_name: str = 'Sheet1'
) -> Dict[str, Any]:
    """Read data from Google Sheet

    Args:
        spreadsheet_id: Sheet ID from URL
        range_name: Range (Sheet1, Sheet1!A1:D10, Data!A:Z)

    Returns: Dict with values, row count, URL
    """
    try:
        service = get_sheets_service()

        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()

        values = result.get('values', [])

        return {
            'status': 'success',
            'spreadsheet_id': spreadsheet_id,
            'range': range_name,
            'values': values,
            'row_count': len(values),
            'url': f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'spreadsheet_id': spreadsheet_id,
            'range': range_name
        }


def write_to_sheet(
    spreadsheet_id: str,
    range_name: str,
    values: List[List[Any]]
) -> Dict[str, Any]:
    """Write data to Sheet (overwrites range)

    Args:
        spreadsheet_id: Sheet ID
        range_name: Range (Sheet1!A1, Data!A1:D10)
        values: 2D list [[row1], [row2], ...]

    Returns: Dict with updated cells/rows count, URL
    """
    try:
        service = get_sheets_service()

        body = {
            'values': values
        }

        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()

        return {
            'status': 'success',
            'spreadsheet_id': spreadsheet_id,
            'range': range_name,
            'updated_cells': result.get('updatedCells', 0),
            'updated_rows': result.get('updatedRows', 0),
            'url': f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'spreadsheet_id': spreadsheet_id
        }


def append_to_sheet(
    spreadsheet_id: str,
    range_name: str,
    values: List[List[Any]]
) -> Dict[str, Any]:
    """Append data to Sheet end

    Args:
        spreadsheet_id: Sheet ID
        range_name: Range (Sheet1, Data!A:D)
        values: 2D list to append

    Returns: Dict with updated cells/rows, URL
    """
    try:
        service = get_sheets_service()

        body = {
            'values': values
        }

        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()

        return {
            'status': 'success',
            'spreadsheet_id': spreadsheet_id,
            'range': range_name,
            'updated_cells': result.get('updates', {}).get('updatedCells', 0),
            'updated_rows': result.get('updates', {}).get('updatedRows', 0),
            'url': f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'spreadsheet_id': spreadsheet_id
        }


def create_spreadsheet(title: str, sheet_names: Optional[List[str]] = None) -> Dict[str, Any]:
    """Create new Spreadsheet

    Args:
        title: Spreadsheet title
        sheet_names: Optional sheet names (default [Sheet1])

    Returns: Dict with spreadsheet_id, sheets list, URL
    """
    try:
        service = get_sheets_service()

        sheets = []
        if sheet_names:
            for name in sheet_names:
                sheets.append({'properties': {'title': name}})
        else:
            sheets = [{'properties': {'title': 'Sheet1'}}]

        spreadsheet = {
            'properties': {'title': title},
            'sheets': sheets
        }

        result = service.spreadsheets().create(body=spreadsheet).execute()
        spreadsheet_id = result.get('spreadsheetId')

        return {
            'status': 'success',
            'spreadsheet_id': spreadsheet_id,
            'title': title,
            'url': f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit',
            'sheets': sheet_names or ['Sheet1']
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'title': title
        }


def clear_sheet(
    spreadsheet_id: str,
    range_name: str
) -> Dict[str, Any]:
    """Clear data from Sheet range

    Args:
        spreadsheet_id: Sheet ID
        range_name: Range (Sheet1, Data!A1:Z100)

    Returns: Dict with cleared range, URL
    """
    try:
        service = get_sheets_service()

        result = service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()

        return {
            'status': 'success',
            'spreadsheet_id': spreadsheet_id,
            'range': range_name,
            'cleared_range': result.get('clearedRange', ''),
            'url': f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'spreadsheet_id': spreadsheet_id
        }


def update_cell(
    spreadsheet_id: str,
    cell: str,
    value: Any
) -> Dict[str, Any]:
    """Update single cell

    Args:
        spreadsheet_id: Sheet ID
        cell: Cell reference (A1, Sheet1!B5)
        value: Value to write

    Returns: Dict with cell, value, URL
    """
    try:
        service = get_sheets_service()

        body = {
            'values': [[value]]
        }

        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=cell,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()

        return {
            'status': 'success',
            'spreadsheet_id': spreadsheet_id,
            'cell': cell,
            'value': value,
            'url': f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'spreadsheet_id': spreadsheet_id,
            'cell': cell
        }


def batch_update_cells(
    spreadsheet_id: str,
    updates: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Update multiple ranges in one request

    Args:
        spreadsheet_id: Sheet ID
        updates: List of dicts with range and values keys

    Returns: Dict with updated cells/ranges count, URL
    """
    try:
        service = get_sheets_service()

        data = []
        for update in updates:
            data.append({
                'range': update['range'],
                'values': update['values']
            })

        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': data
        }

        result = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()

        return {
            'status': 'success',
            'spreadsheet_id': spreadsheet_id,
            'updated_cells': result.get('totalUpdatedCells', 0),
            'updated_ranges': len(updates),
            'url': f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'spreadsheet_id': spreadsheet_id
        }


def list_spreadsheets(max_results: int = 10, query: Optional[str] = None) -> Dict[str, Any]:
    """List Spreadsheets in Drive

    Args:
        max_results: Max sheets (default 10)
        query: Optional search filter

    Returns: Dict with spreadsheets list (id, name, URL, dates)
    """
    try:
        service = get_drive_service()

        # Build query
        mime_type = 'application/vnd.google-apps.spreadsheet'
        q = f"mimeType='{mime_type}' and trashed=false"

        if query:
            q += f" and name contains '{query}'"

        # List spreadsheets
        results = service.files().list(
            q=q,
            pageSize=max_results,
            fields='files(id, name, createdTime, modifiedTime, webViewLink)',
            orderBy='modifiedTime desc'
        ).execute()

        spreadsheets = results.get('files', [])

        return {
            'status': 'success',
            'spreadsheet_count': len(spreadsheets),
            'spreadsheets': [
                {
                    'id': sheet['id'],
                    'name': sheet['name'],
                    'url': sheet.get('webViewLink', ''),
                    'created': sheet.get('createdTime', ''),
                    'modified': sheet.get('modifiedTime', '')
                }
                for sheet in spreadsheets
            ]
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


def get_spreadsheet_metadata(spreadsheet_id: str) -> Dict[str, Any]:
    """Get Spreadsheet metadata

    Args:
        spreadsheet_id: Sheet ID

    Returns: Dict with title, sheet count, sheets info (title/rows/cols), URL
    """
    try:
        service = get_sheets_service()

        spreadsheet = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()

        sheets_info = []
        for sheet in spreadsheet.get('sheets', []):
            props = sheet.get('properties', {})
            grid = props.get('gridProperties', {})
            sheets_info.append({
                'title': props.get('title', ''),
                'sheet_id': props.get('sheetId', ''),
                'index': props.get('index', 0),
                'row_count': grid.get('rowCount', 0),
                'column_count': grid.get('columnCount', 0)
            })

        return {
            'status': 'success',
            'spreadsheet_id': spreadsheet_id,
            'title': spreadsheet.get('properties', {}).get('title', ''),
            'sheet_count': len(sheets_info),
            'sheets': sheets_info,
            'url': f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'spreadsheet_id': spreadsheet_id
        }


def add_sheet_tab(
    spreadsheet_id: str,
    sheet_name: str,
    rows: int = 1000,
    columns: int = 26
) -> Dict[str, Any]:
    """Add new sheet tab to Spreadsheet

    Args:
        spreadsheet_id: Sheet ID
        sheet_name: New sheet name
        rows, columns: Grid size (default 1000x26)

    Returns: Dict with status, URL
    """
    try:
        service = get_sheets_service()

        requests = [{
            'addSheet': {
                'properties': {
                    'title': sheet_name,
                    'gridProperties': {
                        'rowCount': rows,
                        'columnCount': columns
                    }
                }
            }
        }]

        body = {'requests': requests}

        result = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()

        return {
            'status': 'success',
            'spreadsheet_id': spreadsheet_id,
            'sheet_name': sheet_name,
            'url': f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'spreadsheet_id': spreadsheet_id,
            'sheet_name': sheet_name
        }
