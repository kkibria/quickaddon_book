import os
import argparse
import re
from jinja2 import Environment, FileSystemLoader, Template

def process_markdown_file(md_path: str, template: Template):
    # Read markdown file
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find first non-empty line (the heading)
    heading_line = None
    rest_lines_start = 0
    for idx, line in enumerate(lines):
        if line.strip():
            heading_line = line.strip()
            rest_lines_start = idx + 1
            break

    if heading_line is None:
        # No content in file
        return

    # Skip files where first non-empty line contains '---'
    if '---' in heading_line:
        return

    # Extract heading text, removing leading '#' and whitespace
    heading_text = heading_line.strip().lstrip('#').strip()

    # Render template with heading
    rendered = template.render({"title": heading_text})

    # Write back: template content + remaining lines
    print(f'adding frontmatter to {md_path}')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(rendered)
        # Ensure original spacing
        if rest_lines_start < len(lines):
            f.write(''.join(lines[rest_lines_start:]))




# 1. Your custom function that generates the new content
def my_transform_function(old_title):
    # Example: converting the title to uppercase or wrapping it in metadata
    return f"---\ntitle: {old_title.upper()}\n---"

def replace_first_header(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if not lines:
        return

    # 2. Check if the first line is a H1 header
    first_line = lines[0].strip()
    if first_line.startswith("# "):
        # Extract the title (remove '# ' and leading/trailing whitespace)
        extracted_title = first_line[2:].strip()
        
        # 3. Call your function and replace the first line
        new_header = my_transform_function(extracted_title)
        
        # Ensure there is a newline after your new header if it's missing
        lines[0] = new_header + ("\n" if not new_header.endswith("\n") else "")

        # 4. Write the results back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
        print(f"Successfully updated: {file_path}")
    else:
        print("First line is not a # H1 title. No changes made.")

# Usage:
# replace_first_header('example.md')





def main(folder: str, template_path: str):
    # Set up Jinja environment
    template_dir, template_file = os.path.split(template_path)
    env = Environment(
        loader=FileSystemLoader(searchpath=template_dir),
        autoescape=False
    )
    template = env.get_template(template_file)

    # Walk through directory recursively
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith('.md'):
                md_path = os.path.join(root, file)
                process_markdown_file(md_path, template)

if __name__ == '__main__':
    script_path = os.path.abspath(__file__)
    script_directory = os.path.dirname(script_path)

    def_template = os.path.join(script_directory, "fm.template")
    parser = argparse.ArgumentParser(
        description='Apply a Jinja template to all markdown files in a directory tree, replacing the first heading.')
    parser.add_argument('folder', nargs='?', default="./src/topics", help='Root folder to search for .md files')
    parser.add_argument('template', nargs='?', default=def_template, help='Path to the Jinja template file')
    args = parser.parse_args()
    print(f'folder={args.folder}, template={args.template}')
    main(args.folder, args.template)