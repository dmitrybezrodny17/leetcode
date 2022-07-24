from config import *
import requests
import json
import os
import re
import sys


class HTMLEditor():
    def __init__(self, template):
        self.template = template

    def modify(self, pos: str, value: str):
        try:
            self.template = re.sub(pos, value, self.template)
        except TypeError:
            self.template = re.sub(pos, str(value), self.template)
        
    def get_html(self):
        return self.template

class FileExplorer():
    def __init__(self, path):
        self.path = path
        
    def is_exist(self):
        if os.path.exists(self.path):
            return True
        
    def create_dir(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
    
    def read(self):
        with open(self.path, 'r', encoding='utf8') as f:
            f_content = f.read()
        return f_content
        
    def write(self, content):
        with open(self.path, 'w+', encoding='utf8') as f:
            f_content = f.write(content)

def convert_related(related_topics):
    related_list = [related_exp.format(x) for x in related_topics]
    related = ''.join(related_list)
    return related
   
def get_related_topics(tags):
    related_topics = [x['name'] for x in tags]
    return related_topics
    
def modify_data(data):
    difficulty, tags = data['difficulty'], data['topicTags']
    related_topics = get_related_topics(tags)
    data['related'] = convert_related(related_topics)
    data['color'] = colors_dict[difficulty]
    return data

def change_template(template, data):
    editor = HTMLEditor(template)
    data = modify_data(data)
    for i in template_dict:
        editor.modify(i, data[template_dict[i]])
    html = editor.get_html()
    return html
    
def save_html(data, problem_path):
    template_file = FileExplorer(template_name)
    template = template_file.read()
    html = change_template(template, data)
    html_path = problem_path+index_name
    html_file = FileExplorer(html_path)
    html_file.write(html)
    return html_path

def get_snippet_status(snippet_file, code, snippet_path):
    if not snippet_file.is_exist():
        status = 'new'
    elif code != snippet_file.read():
        status = 'updated'
    else:
        status = 'not changed'
    message = f'{snippet_path} - {status}'
    print(message)
    return status
      
def get_snippet_filename(snippet_slug):
    if snippet_slug not in ext_dict:
        print(message_no_extension.format(snippet_slug), file=sys.stderr)
        file_ext = snippet_slug
    else:
        file_ext = ext_dict[snippet_slug]
    snippet_filename = f'{snippet_name}.{file_ext}'
    return snippet_filename

def save_snippet(snippet, problem_path):
    slug, code = snippet['langSlug'], snippet['code']
    snippet_filename = get_snippet_filename(slug)
    snippet_path = problem_path+snippet_filename
    snippet_file = FileExplorer(snippet_path)
    status = get_snippet_status(snippet_file, code, snippet_path)
    if status in ['new', 'updated']:
        snippet_file.write(code)

def get_problem_path(problem_id, problem_slug):
    rpath = f'/{problems_folder}/{problem_id}-{problem_slug}/'
    current_path = os.getcwd()
    problem_path = current_path.replace('\\','/')+rpath
    return problem_path
   
def no_errors(r_json):
    if 'errors' in r_json:
        return False
    elif 'data' in r_json:
        return True
   
def get_problem_response(question_slur):
    query['variables']['titleSlug'] = question_slur
    cookies = {'csrftoken': csrftoken, 'LEETCODE_SESSION': session} # CANT BE TESTED ATM
    response = requests.get(graphql_url, json=query)
    return response
    
def get_problem_url():
    try:
        problem_url = sys.argv[1]
    except IndexError:
        sys.exit(message_no_url)
    return problem_url

def get_problem_slur(problem_url):
    try:
        problem_slur = re.search(problem_exp, problem_url)[1]
    except TypeError:
        sys.exit(message_wrong_url)
    else:
        return problem_slur
        
def get_data(problem_slur):
    response = get_problem_response(problem_slur)
    r_json = response.json()
    if no_errors(r_json) == True:
        data = r_json['data']['question']
    else:
        error = r_json['errors'][0]['message']
        sys.exit(error)
    return data
    
def create_problem_dir(problem_path):
    problem_dir = FileExplorer(problem_path)
    problem_dir.create_dir()

def main(problem_url):
    problem_slur = get_problem_slur(problem_url)
    data = get_data(problem_slur)
    qid, snippets = data['questionId'], data['codeSnippets']
    problem_path = get_problem_path(qid, problem_slur)
    create_problem_dir(problem_path)
    for snippet in snippets:
        save_snippet(snippet, problem_path)
    save_html(data, problem_path)
    
if __name__=='__main__':
    problem_url = get_problem_url()
    main(problem_url)

