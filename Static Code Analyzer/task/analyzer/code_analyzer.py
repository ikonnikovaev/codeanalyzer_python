import os
import re
import sys

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




    def check_line(self, line):
        errors = []
        if not self.check_length(line):
            errors.append('S001')
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
        if not self.check_class_name(line):
            errors.append('S008')
        if not self.check_function_name(line):
            errors.append('S009')
        return errors

    def check_file(self, path):
        with open(path) as f:
            empty_counter = 0
            for (i, line) in enumerate(f, start=1):
                errors = analyzer.check_line(line)
                if empty_counter > 2:
                    errors.append('S006')
                errors.sort()
                for e in errors:
                    print(f'{path}: Line {i}: {e} {analyzer.errors_dict[e]}')
                if not line.strip():
                    empty_counter += 1
                else:
                    empty_counter = 0

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



