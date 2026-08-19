import os

def save(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as out:
        out.write(content.strip() + '\n')
    print('SAVED:', path)

print('make_all initialized')
