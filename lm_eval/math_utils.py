import re


def convert_word_number(text: str) -> str:
    try:
        text = str(w2n.word_to_num(text))
    except Exception:
        pass
    return text


def _fix_fracs(string):
    substrs = string.split('\\frac')
    new_str = substrs[0]
    if len(substrs) > 1:
        substrs = substrs[1:]
        for substr in substrs:
            new_str += '\\frac'
            if len(substr) > 0 and substr[0] == '{':
                new_str += substr
            else:
                try:
                    assert len(substr) >= 2
                except Exception:
                    return string
                a = substr[0]
                b = substr[1]
                if b != '{':
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += '{' + a + '}{' + b + '}' + post_substr
                    else:
                        new_str += '{' + a + '}{' + b + '}'
                else:
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += '{' + a + '}' + b + post_substr
                    else:
                        new_str += '{' + a + '}' + b
    string = new_str
    return string


def _fix_a_slash_b(string):
    if len(string.split('/')) != 2:
        return string
    a = string.split('/')[0]
    b = string.split('/')[1]
    try:
        if 'sqrt' not in a:
            a = int(a)
        if 'sqrt' not in b:
            b = int(b)
        assert string == '{}/{}'.format(a, b)
        new_string = '\\frac{' + str(a) + '}{' + str(b) + '}'
        return new_string
    except Exception:
        return string


def _fix_sqrt(string):
    _string = re.sub(r'\\sqrt(\w+)', r'\\sqrt{\1}', string)
    return _string


def strip_answer_string(string):
    string = str(string).strip()
    # linebreaks
    string = string.replace('\n', '')

    # right "."
    string = string.rstrip('.')

    # remove inverse spaces
    # replace \\ with \
    string = string.replace('\\!', '')
    # string = string.replace("\\ ", "")
    # string = string.replace("\\\\", "\\")

    # matrix
    string = re.sub(r'\\begin\{array\}\{.*?\}', r'\\begin{pmatrix}', string)
    string = re.sub(r'\\end\{array\}', r'\\end{pmatrix}', string)
    string = string.replace('bmatrix', 'pmatrix')

    # replace tfrac and dfrac with frac
    string = string.replace('tfrac', 'frac')
    string = string.replace('dfrac', 'frac')
    string = (string.replace('\\neq', '\\ne').replace('\\leq', '\\le').replace('\\geq', '\\ge'))

    # remove \left and \right
    string = string.replace('\\left', '')
    string = string.replace('\\right', '')
    string = string.replace('\\{', '{')
    string = string.replace('\\}', '}')

    # Function to replace number words with corresponding digits
    def replace_match(match):
        word = match.group(1).lower()
        if convert_word_number(word) == word:
            return match.group(0)
        else:
            return convert_word_number(word)

    string = re.sub(r'\\text\{([a-zA-Z]+)\}', replace_match, string)

    # Before removing unit, check if the unit is squared (for surface area)
    string = re.sub(r'(cm|inches)\}\^2', r'\1}', string)

    # Remove unit: miles, dollars if after is not none
    _string = re.sub(r'\\text{.*?}$', '', string).strip()
    if _string != '' and _string != string:
        # print("Warning: unit not removed: '{}' -> '{}'".format(string, _string))
        string = _string

    # Remove circ (degrees)
    string = string.replace('^{\\circ}', '')
    string = string.replace('^\\circ', '')

    # remove dollar signs
    string = string.replace('\\$', '')
    string = string.replace('$', '')
    string = string.replace('\\(', '').replace('\\)', '')

    # convert word number to digit
    string = convert_word_number(string)

    # replace "\\text{...}" to "..."
    string = re.sub(r'\\text\{(.*?)\}', r'\1', string)
    for key in ['x=', 'y=', 'z=', 'x\\in', 'y\\in', 'z\\in', 'x\\to', 'y\\to', 'z\\to']:
        string = string.replace(key, '')
    string = string.replace('\\emptyset', r'{}')
    string = string.replace('(-\\infty,\\infty)', '\\mathbb{R}')

    # remove percentage
    string = string.replace('\\%', '')
    string = string.replace('\%', '')
    string = string.replace('%', '')

    # " 0." equivalent to " ." and "{0." equivalent to "{." Alternatively, add "0" if "." is the start of the string
    string = string.replace(' .', ' 0.')
    string = string.replace('{.', '{0.')

    # cdot
    # string = string.replace("\\cdot", "")
    if (
        string.startswith('{') and string.endswith('}') and string.isalnum()
        or string.startswith('(') and string.endswith(')') and string.isalnum()
        or string.startswith('[') and string.endswith(']') and string.isalnum()
    ):
        string = string[1:-1]

    # inf
    string = string.replace('infinity', '\\infty')
    if '\\infty' not in string:
        string = string.replace('inf', '\\infty')
    string = string.replace('+\\inity', '\\infty')

    # and
    string = string.replace('and', '')
    string = string.replace('\\mathbf', '')

    # use regex to remove \mbox{...}
    string = re.sub(r'\\mbox{.*?}', '', string)

    # quote
    string.replace("'", '')
    string.replace('"', '')

    # i, j
    if 'j' in string and 'i' not in string:
        string = string.replace('j', 'i')

    # replace a.000b where b is not number or b is end, with ab, use regex
    string = re.sub(r'(\d+)\.0*([^\d])', r'\1\2', string)
    string = re.sub(r'(\d+)\.0*$', r'\1', string)

    # if empty, return empty string
    if len(string) == 0:
        return string
    if string[0] == '.':
        string = '0' + string

    # to consider: get rid of e.g. "k = " or "q = " at beginning
    if len(string.split('=')) == 2:
        if len(string.split('=')[0]) <= 2:
            string = string.split('=')[1]

    string = _fix_sqrt(string)
    string = string.replace(' ', '')

    # \frac1b or \frac12 --> \frac{1}{b} and \frac{1}{2}, etc. Even works with \frac1{72} (but not \frac{72}1). Also does a/b --> \\frac{a}{b}
    string = _fix_fracs(string)

    # NOTE: X/Y changed to \frac{X}{Y} in dataset, but in simple cases fix in case the model output is X/Y
    string = _fix_a_slash_b(string)

    # Remove unnecessary '\' before integers
    string = re.sub(r'\\(?=\-?\d+(\\|\)|,|\]|$))', '', string)

    # Remove grade level (e.g., 12th grade) and just maintain the integer
    string = re.sub(r'thgrade$', '', string)

    # Normalize thousands-formatted numbers (e.g., 70,000 or -1,234,567.89) by removing commas
    # This must run before the "list of integers" sorting to avoid misclassifying numbers with thousand separators.
    if re.fullmatch(r'\s*-?\d{1,3}(?:,\d{3})+(?:\.\d+)?\s*', string):
        string = string.replace(',', '')

    # If the answer is a list of integers (without parenthesis), sort them
    if re.fullmatch(r'(\s*-?\d+\s*,)*\s*-?\d+\s*', string):
        # Split the string into a list of integers
        try:
            integer_list = list(map(int, string.split(',')))
        except Exception:
            integer_list = list(map(int, '-1,-1'.split(',')))

        # Sort the list in ascending order
        sorted_list = sorted(integer_list)

        # Join the sorted list back into a comma-separated string
        string = ','.join(map(str, sorted_list))

    return string


def extract_answer(pred_str, use_last_number=True):
    pred_str = pred_str.replace('\u043a\u0438', '')
    if 'final answer is $' in pred_str and '$. I hope' in pred_str:
        # minerva_math
        tmp = pred_str.split('final answer is $', 1)[1]
        pred = tmp.split('$. I hope', 1)[0].strip()
    elif 'boxed' in pred_str:
        ans = pred_str.split('boxed')[-1]
        if len(ans) == 0:
            return ''
        elif ans[0] == '{':
            stack = 1
            a = ''
            for c in ans[1:]:
                if c == '{':
                    stack += 1
                    a += c
                elif c == '}':
                    stack -= 1
                    if stack == 0:
                        break
                    a += c
                else:
                    a += c
        else:
            a = ans.split('$')[0].strip()
        pred = a
    elif 'he answer is' in pred_str:
        pred = pred_str.split('he answer is')[-1].strip()
    elif 'final answer is' in pred_str:
        pred = pred_str.split('final answer is')[-1].strip()
    elif '答案是' in pred_str:
        # Handle Chinese few-shot multiple choice problem answer extraction
        pred = pred_str.split('答案是')[1].strip().split('\n\n')[0].strip()
    elif 'ANSWER:' in pred_str:
        pred = pred_str.split('ANSWER:')[-1].strip()
    else:  # use the last number
        if use_last_number:
            pattern = '-?\d*\.?\d+'
            pred = re.findall(pattern, pred_str.replace(',', ''))
            if len(pred) >= 1:
                pred = pred[-1]
            else:
                pred = ''
        else:
            pred = ''

    # multiple line
    # pred = pred.split("\n")[0]
    pred = re.sub(r'\n\s*', '', pred)
    if pred != '' and pred[0] == ':':
        pred = pred[1:]
    if pred != '' and pred[-1] == '.':
        pred = pred[:-1]
    if pred != '' and pred[-1] == '/':
        pred = pred[:-1]
    pred = strip_answer_string(pred)
    return pred
