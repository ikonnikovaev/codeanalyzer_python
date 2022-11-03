import ast
import os
import re
import sys

class MyError:
    def __init__(self, lineno, code, name = ""):
        self.lineno = lineno
        self.code = code
        self.message = ''

        if code == 'S001':
            self.message = 'Too long'
        elif code == 'S002':
            self.message = 'Indentation is not a multiple of four'
        elif code == 'S003':
            self.message = 'Unnecessary semicolon after a statement'
        elif code == 'S004':
            self.message = 'Less than two spaces before inline comments'
        elif code == 'S005':
            self.message = 'TODO found'
        elif code == 'S006':
            self.message = 'More than two blank lines preceding a code line'
        elif code == 'S007':
            self.message = 'Too many spaces after construction_name (def or class)'
        elif code == 'S008':
            self.message = f'Class name {name} should be written in CamelCase'
        elif code == 'S009':
            self.message = f'Function name {name} should be written in snake_case'
        elif code == 'S010':
            self.message = f'Argument name {name} should be written in snake_case'
        elif code == 'S011':
            self.message = f'Variable {name} should be written in snake_case'
        elif code == 'S012':
            self.message = 'The default argument value is mutable'


class CodeAnalyzer:
    errors_dict = {
        'S001': 'Too long',
        'S002': 'Indentation is not a multiple of four',
        'S003': 'Unnecessary semicolon after a statement',
        'S004': 'Less than two spaces before inline comments',
        'S005': 'TODO found',
        'S006': 'More than two blank lines preceding a code line',
        'S007': 'Too many spaces after construction_name (def or class)',
        'S008': 'Class name class_name should be written in CamelCase',
        'S009': 'Function name function_name should be written in snake_case'
    }

    def split_line(self, line):
        quotes = None
        for i in range(len(line)):
            if line[i] == '#' and quotes is None:
                return line[:i], line[i:]
            if line[i] in ['\'', '"']:
                if quotes is None:
                    quotes = line[i]
                elif line[i] == quotes:
                    if i > 0 and line[i - 1] != '\\':
                        quotes = None
        return line, ''

    def check_length(self, line):
        MAX_LEN = 79
        return len(line) <= MAX_LEN

    def check_indentation(self, line):
        indent = len(line) - len(line.lstrip(' '))
        return indent % 4 == 0

    def check_semicolon(self, line):
        statement, comment = self.split_line(line)
        statement = statement.rstrip()
        if (statement):
            return statement.rstrip()[-1] != ';'
        return True

    def check_comment(self, line):
        statement, comment = self.split_line(line)
        if not statement:
            return True
        if comment:
            if len(statement) < 2 or statement[-1] != ' ' or statement[-2] != ' ':
                return False
        return True

    def check_todos(self, line):
        statement, comment = self.split_line(line)
        if comment:
            return comment.lower().find('todo') == -1
        return True

    def check_spaces(self, line):
        statement, comment = self.split_line(line)
        return not re.match('(def|class)\s{2,}', statement.lstrip())


    '''
    def check_class_name(self, line):
        statement, comment = self.split_line(line)
        match = re.match('class\s+(\w+)', statement.lstrip())
        if not match:
            return True
        else:
            class_name = match.group(1)
            return re.match('([A-Z][a-z]*)+', class_name)

    def check_function_name(self, line):
        statement, comment = self.split_line(line)
        match = re.match('def\s+(\w+)', statement.lstrip())
        if not match:
            return True
        else:
            function_name = match.group(1)
            return re.match('[a-z_]+', function_name)
    '''


    def check_line(self, line):
        errors = []
        if not self.check_length(line):
            errors.append(MyError('S001'))
        if not self.check_indentation(line):
            errors.append('S002')
        if not self.check_semicolon(line):
            errors.append('S003')
        if not self.check_comment(line):
            errors.append('S004')
        if not self.check_todos(line):
            errors.append('S005')
        if not self.check_spaces(line):
            errors.append('S007')
        '''
        if not self.check_class_name(line):
            errors.append('S008')
        if not self.check_function_name(line):
            errors.append('S009')
        '''
        return errors

    def check_functions(self, path):
        errors = []
        with open(path) as f:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    lineno = node.lineno
                    function_name = node.name
                    function_args = [a.arg for a in node.args.args]
                    default_values = [d for d in node.args.defaults] + [d for d in node.args.kw_defaults]

                    if not re.match('[a-z_]+', function_name):
                        errors.append(MyError(lineno, 'S009', function_name))
                    for arg in function_args:
                        if not re.match('[a-z_]+', arg):
                            errors.append(MyError(lineno, 'S010', arg))
                    for dv in default_values:
                        if isinstance(dv, ast.List) or isinstance(dv, ast.Dict):
                            errors.append(MyError(lineno, 'S012'))

        return errors

    def check_classes(self, path):
        errors = []
        with open(path) as f:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    lineno = node.lineno
                    class_name = node.name
                    if not re.match('([A-Z][a-z]*)+', class_name):
                        errors.append(MyError(lineno, 'S008', class_name))
        return errors

    def check_variables(self, path):
        errors = []
        with open(path) as f:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    lineno = node.lineno
                    target_names = [t.id for t in node.targets if isinstance(t, ast.Name)]
                    for var_name in target_names:
                        if not re.match('[a-z_]+', var_name):
                            errors.append(MyError(lineno, 'S011', var_name))

        return errors


    def check_lines(self, path):
        errors = []
        with open(path) as f:
            empty_counter = 0
            for (lineno, line) in enumerate(f, start=1):
                if not self.check_length(line):
                    errors.append(MyError(lineno, 'S001'))
                if not self.check_indentation(line):
                    errors.append(MyError(lineno, 'S002'))
                if not self.check_semicolon(line):
                    errors.append(MyError(lineno, 'S003'))
                if not self.check_comment(line):
                    errors.append(MyError(lineno, 'S004'))
                if not self.check_todos(line):
                    errors.append(MyError(lineno, 'S005'))
                if empty_counter > 2:
                    errors.append(MyError(lineno, 'S006'))
                if not self.check_spaces(line):
                    errors.append(MyError(lineno, 'S007'))

                # errors.sort()
                # for e in errors:
                    # print(f'{path}: Line {i}: {e} {analyzer.errors_dict[e]}')
                if not line.strip():
                    empty_counter += 1
                else:
                    empty_counter = 0
        return errors

    def check_file(self, path):
        errors = self.check_lines(path) + self.check_classes(path) \
                 + self.check_functions(path) + self.check_variables(path)
        errors.sort(key=lambda e: (e.lineno, e.code))
        for e in errors:
            print(f'{path}: Line {e.lineno}: {e.code} {e.message}')



    def check_all_files(self, path):
        if os.path.isfile(path) and path.endswith('.py'):
            self.check_file(path)
        elif os.path.isdir(path):
            for p in sorted(os.listdir(path)):
                if p.endswith('.py'):
                    self.check_file(os.path.join(path, p))


if __name__ == '__main__':
    path = sys.argv[1]
    analyzer = CodeAnalyzer()
    analyzer.check_all_files(path)



