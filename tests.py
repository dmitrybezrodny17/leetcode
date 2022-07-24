from config import *
from main import *
import pytest


current_path = os.getcwd().replace('\\','/') # windows pathing

class JSONLoader(FileExplorer):
    def load(self):
        with open(self.path, 'r', encoding='utf8') as f:
            data = json.load(f)
        return data

def test_convert_related():
    related_topics = ['1', '2']
    result_html = convert_related(related_topics)
    correct_html = '<div class="rl">1</div><div class="rl">2</div>'
    assert result_html == correct_html
    
def test_get_problem_slur():
    test_slur = 'https://leetcode.com/problems/median-of-two-sorted-arrays/'
    result_slur = get_problem_slur(test_slur)
    correct_slur = 'median-of-two-sorted-arrays'
    assert result_slur == correct_slur
    
def test_get_problem_slur_bad_domain():
    with pytest.raises(SystemExit) as e:
        get_problem_slur('https://leetcod.com/problems/123/')
    assert str(e.value) == message_wrong_url 
    
def test_get_problem_slur_bad_url():
    with pytest.raises(SystemExit) as e:
        get_problem_slur('https://leetcode.com/problems/123')
    assert str(e.value) == message_wrong_url
    
def test_get_problem_response_code():
    test_slur = 'any-slur'
    result_response = get_problem_response(test_slur)
    assert result_response.status_code == 200 

def get_test_response(case):   
    path = current_path+f'/test_data/response_with_{case}.json'
    response_file = JSONLoader(path)
    response = response_file.load() 
    return response

def test_no_errors_response_with_data():
    response = get_test_response('data')
    result_status = no_errors(response)
    assert result_status == True
    
def test_no_errors_response_with_errors():
    response = get_test_response('errors')
    result_status = no_errors(response)
    assert result_status == False

def test_get_problem_path():
    problem_id, problem_slug = '1', 'test'
    result_path = get_problem_path(problem_id, problem_slug)
    correct_path = current_path+'/problems/1-test/'
    assert result_path == correct_path
    
def get_snippet_code(case):
    path = current_path+'/test_data/snippets.json'
    snippets_file = JSONLoader(path)
    snippets = snippets_file.load()
    code = snippets['codeSnippets'][case]['code']
    return code
    
def test_get_snippet_status_new():
    code = get_snippet_code(0)
    path = current_path+'/test_data/0-test-problem/main.cpp'
    snippet_file = FileExplorer(path)
    result_status = get_snippet_status(snippet_file, code, path)
    assert result_status == 'new'

def test_get_snippet_status_updated():
    code = get_snippet_code(1)
    path = current_path+'/test_data/0-test-problem/main.java'
    snippet_file = FileExplorer(path)
    result_status = get_snippet_status(snippet_file, code, path)
    assert result_status == 'updated'

def test_get_snippet_status_not_changed():
    code = get_snippet_code(2)
    path = current_path+'/test_data/0-test-problem/main.py'
    snippet_file = FileExplorer(path)
    result_status = get_snippet_status(snippet_file, code, path)
    assert result_status == 'not changed'
    
def test_get_problem_url_correct():
    sys.argv[1] = 'https://leetcode.com/problem/any-slur/'
    correct_problem_url = 'https://leetcode.com/problem/any-slur/'
    result_problem_url = get_problem_url()
    assert result_problem_url == correct_problem_url
    
def test_get_problem_url_exit():
    sys.argv = [sys.argv[0]]
    with pytest.raises(SystemExit) as e:
        get_problem_url()
    assert str(e.value) == message_no_url
    
def test_get_snippet_filename_correct_slug():
    snippet_slug = 'python3'
    result_filename = get_snippet_filename(snippet_slug)
    correct_filename = 'main.py3'
    assert result_filename == correct_filename
    
def test_get_snippet_filename_incorrect_slug():
    snippet_slug = 'python2'
    result_filename = get_snippet_filename(snippet_slug)
    correct_filename = 'main.python2'
    assert result_filename == correct_filename
    
def test_get_snippet_filename_incorrect_slug_stdout(capsys):
    snippet_slug = 'python2'
    get_snippet_filename(snippet_slug)
    captured = capsys.readouterr()
    assert captured.err == message_no_extension.format(snippet_slug)+'\n'

def get_test_template():
    template_path = current_path+'/template.html'
    template_file = FileExplorer(template_path)
    template = template_file.read()
    return template
    
def get_test_data():
    data_path = current_path+'/test_data/response_with_data.json'
    data_file = JSONLoader(data_path)
    data = data_file.load()['data']['question']
    return data
    
def get_test_html():
    html_path = current_path+'/test_data/index_correct.html'
    html_file = FileExplorer(html_path)
    html = html_file.read()
    return html

def test_change_html():
    template = get_test_template()
    data = get_test_data()
    result_html = change_template(template, data).rstrip('\n')
    correct_html = get_test_html()
    assert result_html == correct_html
    
def test_save_html():
    data = get_test_data()
    problem_path = current_path+'/test_data/0-test-problem/'
    result_path = save_html(data, problem_path)
    is_exists = os.path.exists(result_path)
    assert is_exists == True

def test_save_snippet():
    data = get_test_data()
    snippet = data['codeSnippets'][4]
    problem_path = current_path+'/test_data/0-test-problem/'
    save_snippet(snippet, problem_path)
    slug, code = snippet['langSlug'], snippet['code']
    snippet_path = problem_path+'/main.c'
    assert os.path.exists(snippet_path) == True

def test_get_data_correct_slur():
    data = get_test_data()
    problem_slur = 'median-of-two-sorted-arrays'
    result_data = get_data(problem_slur)
    assert result_data['questionId'] == data['questionId']
    
def test_get_data_incorrect_slur():
    data = get_test_data()
    problem_slur = 'wrong-slur'
    with pytest.raises(SystemExit) as e:
        get_data(problem_slur)
    assert str(e.value) == 'Question matching query does not exist.'
        
def test_create_problem_dir():
    problem_path = 'problems/228'
    create_problem_dir(problem_path)
    assert os.path.exists(problem_path) == True
  
def test_main():
    problem_url = 'https://leetcode.com/problems/string-to-integer-atoi/'
    main(problem_url)
    problem_path = current_path+'/problems/8-string-to-integer-atoi'
    assert os.path.exists(problem_path) == True
    index_path = problem_path+'/index.html'
    assert os.path.exists(index_path) == True
    for ext in ext_dict.values():
        snippet_path = problem_path+f'/main.{ext}'
        assert os.path.exists(snippet_path) == True

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    