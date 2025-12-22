import os

def check_files():
    files_to_fix = []
    for root, dirs, files in os.walk('.'):
        if '.venv' in dirs:
            dirs.remove('.venv')
        if '.git' in dirs:
            dirs.remove('.git')
            
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if '{% static' in content:
                            if '{% load static' not in content and '{% load static %}' not in content:
                                files_to_fix.append(path)
                            # else:
                                # print(f"Valid: {path}")
                        # else:
                            # print(f"No static: {path}")
                except Exception as e:
                    print(f"Error reading {path}: {e}")
                    
    print(f"Scanned {len(files_to_fix)} files missing load static:")
    for f in files_to_fix:
        print(f)

if __name__ == '__main__':
    check_files()
