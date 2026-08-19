import os, base64, sys
def save_file(path, b64_content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(base64.b64decode(b64_content))
    print(f'WROTE: {path}')
