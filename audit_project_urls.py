import os
import re

# Configuration
PROJECT_ROOT = os.getcwd()
SKIP_DIRS = ['venv', '.git', '.gemini', '__pycache__', 'node_modules', 'staticfiles', 'media', 'updated', 'site-packages']
# Known global URLs that might not need namespaces (or are false positives)
# Adjust this list as we discover them.
# 'admin:index' has a colon, so it's fine.
# 'login', 'logout', 'password_change' are standard auth but now we use namespaced/custom ones often.
SAFE_GLOBAL_URLS = ['admin:index', 'admin:login', 'logout'] 

# Regex to find {% url 'name' ... %}
URL_PATTERN = re.compile(r'{%\s*url\s+[\'"]([^\'"]+)[\'"]\s*')

def scan_templates():
    print(f"Scanning for non-namespaced URLs in: {PROJECT_ROOT}\n")
    
    issues_found = []

    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, PROJECT_ROOT)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                    for i, line in enumerate(lines):
                        matches = URL_PATTERN.findall(line)
                        for url_name in matches:
                            # Check if it has a namespace (contains ':')
                            if ':' not in url_name and url_name not in SAFE_GLOBAL_URLS:
                                issues_found.append({
                                    'file': rel_path,
                                    'line': i + 1,
                                    'url': url_name,
                                    'content': line.strip()
                                })
                except Exception as e:
                    print(f"Could not read {rel_path}: {e}")

    output_path = os.path.join(PROJECT_ROOT, 'audit_results.txt')
    with open(output_path, 'w', encoding='utf-8') as out_f:
        if issues_found:
            out_f.write(f"Found {len(issues_found)} potential namespacing issues:\n")
            current_file = ""
            for issue in issues_found:
                if issue['file'] != current_file:
                    out_f.write(f"\n📄 {issue['file']}\n")
                    current_file = issue['file']
                out_f.write(f"  Line {issue['line']}: {issue['url']}  ->  {issue['content']}\n")
        else:
            out_f.write("✅ No obvious non-namespaced URLs found!\n")
    
    print(f"Audit complete. Results written to {output_path}")

if __name__ == "__main__":
    scan_templates()
