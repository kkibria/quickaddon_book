import re

# Example mapping of file paths to titles
title_mapping = {
    'docs/intro.md': 'Introduction',
    'docs/setup.md': 'Setup Guide',
    'images/logo.png': 'Project Logo',
    'https://openai.com': 'OpenAI',
}

pattern = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def replace_titles(text, mapping):
    def repl(match):
        old_title, path = match.groups()
        new_title = mapping.get(path, old_title)
        return f"[{new_title}]({path})"

    return pattern.sub(repl, text)


if __name__ == '__main__':
    # Read the markdown file
    with open('test.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace link titles
    updated = replace_titles(content, title_mapping)

    # Write back to file or to a new file
    with open('test_updated.md', 'w', encoding='utf-8') as f:
        f.write(updated)

    print('Link titles replaced and written to README_updated.md')



# def update_links(file_content, update_dict):
#     # Regex breakdown:
#     # \[([^\]]+)\] -> Matches link text inside square brackets [group 1]
#     # \(([^)]+)\)  -> Matches link path inside parentheses [group 2]
#     pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    
#     def replacement(match):
#         old_title = match.group(1)
#         path = match.group(2)
        
#         # If the path exists in our dict, update the title; otherwise, keep it
#         new_title = update_dict.get(path, old_title)
#         return f"[{new_title}]({path})"

#     return re.sub(pattern, replacement, file_content)