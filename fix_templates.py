import os
import glob

def fix_templates():
    template_dir = 'app/templates/pages'
    for template_file in glob.glob(os.path.join(template_dir, '*.html')):
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '{% extends \'layout.html\' %}' in content:
            content = content.replace('{% extends \'layout.html\' %}', '{% extends \'layouts/layout.html\' %}')
            
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Fixed {template_file}')

if __name__ == '__main__':
    fix_templates() 