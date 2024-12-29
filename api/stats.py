import threading
import time
import json
import os
from hashlib import md5
import re

# 当前程序状态,暂时用字典存储
stats = {}
documents = []
lock = threading.Lock()

# Guard to ensure the thread is only started once
if not hasattr(threading, 'save_documents_thread'):
    def save_documents():
        while True:
            with lock:
                temp_documents = documents.copy()
            for item in temp_documents:
                resp = item['resp']
                del item['resp']
                del item['stats']['q_info']
                stats_hash = md5(json.dumps(item, sort_keys=True).encode()).hexdigest()
                course_title = item["stats"]["course"]["title"]
                chapter_title = item["stats"]["chapter_point"]["title"]
                directory = f'docs/{course_title}'
                os.makedirs(directory, exist_ok=True)
                json_path = os.path.join(directory, f'{chapter_title}_{stats_hash}.json')
                docs_path = os.path.join(directory, f'{chapter_title}_{stats_hash}.docs')
                
                # Save as JSON
                with open(json_path, 'w') as json_file:
                    json.dump(item, json_file)
                
                # Save as PPTX (assuming you have the content to save as PPTX)
                with open(docs_path, 'wb') as pptx_file:
                    pptx_file.write(resp)
            # delete all documents
            with lock:
                for item in temp_documents:
                    documents.remove(item)
            time.sleep(5)

    # Start the thread
    threading.save_documents_thread = threading.Thread(target=save_documents, daemon=True)
    threading.save_documents_thread.start()