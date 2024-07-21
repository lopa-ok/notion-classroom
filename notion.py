import base64
import json
import re
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API setup
SERVICE_ACCOUNT_FILE = 'path/to/your/service_account.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gmail_service = build('gmail', 'v1', credentials=credentials)

# Notion API setup
NOTION_API_TOKEN = 'your_notion_api_token'
DATABASE_ID = 'your_notion_database_id'

def get_emails_with_tasks():
    try:
        results = gmail_service.users().messages().list(userId='me', q='subject:task OR subject:due').execute()
        messages = results.get('messages', [])

        tasks = []
        for message in messages:
            msg = gmail_service.users().messages().get(userId='me', id=message['id']).execute()
            payload = msg['payload']
            headers = payload['headers']
            for header in headers:
                if header['name'] == 'Subject':
                    subject = header['value']
                    task_title = re.search(r'Task: (.*)', subject)
                    due_date = re.search(r'Due: (.*)', subject)
                    if task_title and due_date:
                        tasks.append({
                            'title': task_title.group(1),
                            'dueDate': due_date.group(1)
                        })

        return tasks
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def add_task_to_notion(task):
    notion_url = f'https://api.notion.com/v1/pages'
    headers = {
        'Authorization': f'Bearer {NOTION_API_TOKEN}',
        'Content-Type': 'application/json',
        
    }

    task_data = {
        'parent': {'database_id': DATABASE_ID},
        'properties': {
            'Title': {'title': [{'text': {'content': task.get('title', 'No Title')}}]},
            'Due Date': {'date': {'start': task.get('dueDate', '')}}
        }
    }

    response = requests.post(notion_url, headers=headers, data=json.dumps(task_data))
    if response.status_code == 200:
        print(f"Task '{task.get('title', 'No Title')}' added to Notion.")
    else:
        print(f"Failed to add task: {response.text}")

def main():
    tasks = get_emails_with_tasks()
    for task in tasks:
        add_task_to_notion(task)

if __name__ == '__main__':
    main()
