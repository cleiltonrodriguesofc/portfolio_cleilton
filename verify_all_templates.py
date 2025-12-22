
import os
import django
from django.conf import settings
from django.template.loader import get_template
from django.template import TemplateSyntaxError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_cleilton.settings')
django.setup()

def check_templates():
    print("Checking all templates for syntax errors...")
    from django.template.utils import get_app_template_dirs
    
    # Get all template directories
    template_dirs = []
    # Add manual template dirs from settings if any (simplified)
    for engine in settings.TEMPLATES:
        template_dirs.extend(engine.get('DIRS', []))
    
    # Add app template dirs
    # This might be hard to enumerate perfectly without walking everything, 
    # but let's try walking the project root for .html files and trying to load them.
    
    errors = []
    
    for root, dirs, files in os.walk('.'):
        if '.venv' in dirs: dirs.remove('.venv')
        if '.git' in dirs: dirs.remove('.git')
        if '__pycache__' in dirs: dirs.remove('__pycache__')
        
        for file in files:
            if file.endswith('.html'):
                full_path = os.path.join(root, file)
                # Try to find relative path for loader
                # This is tricky because calculate the relative path expected by get_template
                # A heuristic: if 'templates' is in the path, take everything after it.
                
                rel_path = None
                parts = full_path.split(os.sep)
                if 'templates' in parts:
                    idx = parts.index('templates')
                    rel_path = "/".join(parts[idx+1:])
                
                if rel_path:
                    try:
                        get_template(rel_path)
                        # print(f"OK: {rel_path}")
                    except TemplateSyntaxError as e:
                        print(f"SYNTAX ERROR in {rel_path} ({full_path}): {e}")
                        errors.append((rel_path, e))
                    except Exception as e:
                        # TemplateDoesNotExist is expected if we guessed the path wrong, ignore it
                        # But other errors might be relevant
                        if "TemplateDoesNotExist" not in str(type(e)):
                             print(f"Error loading {rel_path}: {e}")

    if not errors:
        print("\nAll templates passed syntax check!")
    else:
        print(f"\nFound {len(errors)} templates with errors.")

if __name__ == "__main__":
    check_templates()
