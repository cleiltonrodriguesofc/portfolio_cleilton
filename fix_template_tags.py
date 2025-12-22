
import os
import re

files_to_fix = [
    'prograos/templates/prograos/create_nota.html',
    'reforco/templates/reforco/mensagens.html',
    'reforco/templates/reforco/presenca_form.html',
    'reforco/templates/reforco/relatorio_pagamentos.html',
    'reforco/templates/reforco/relatorio_presenca.html',
]


def fix_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Regex to find tags spanning multiple lines
        # \{% captures start
        # .*? non-greedy match of content
        # %\} captures end
        # flags=re.DOTALL makes . match newlines

        # We want to find {% ... %} where ... contains a newline.

        def replacer(match):
            text = match.group(0)
            if '\n' in text:
                print(f"Fixing split tag in {path}: {text[:20]}...")
                return text.replace('\n', ' ').replace('\r', '')
            return text

        new_content = re.sub(r'\{%.*?%\}', replacer, content, flags=re.DOTALL)

        # Also fix missing spaces around == in if tags
        # Find {% if ... == ... %} where == has no spaces or one side
        # Easier: replace '==' with ' == ' generally inside tags?
        # But we need to be inside {%...%} block.
        # Let's just do a specific replacement for the known error '==aluno' or 'id=='

        new_content = new_content.replace('==aluno_selecionado.id', ' == aluno_selecionado.id')
        new_content = new_content.replace('aluno.id==', 'aluno.id == ')
        new_content = new_content.replace("status=='pago'", "status == 'pago'")
        new_content = new_content.replace("status=='pendente'", "status == 'pendente'")

        # Regex to find variable tags {{ ... }} spanning multiple lines
        def replacer_vars(match):
            text = match.group(0)
            if '\n' in text:
                print(f"Fixing split variable in {path}: {text[:20]}...")
                return text.replace('\n', ' ').replace('\r', '')
            return text

        new_content = re.sub(r'\{\{.*?\}\}', replacer_vars, new_content, flags=re.DOTALL)

        if new_content != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {path}")
        else:
            print(f"No changes needed for {path}")

    except Exception as e:
        print(f"Error processing {path}: {e}")


if __name__ == "__main__":
    for f in files_to_fix:
        if os.path.exists(f):
            fix_file(f)
        else:
            print(f"File not found: {f}")
