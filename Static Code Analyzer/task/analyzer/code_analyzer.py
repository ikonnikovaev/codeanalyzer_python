# write your code here
def check_len(line):
    MAX_LEN = 79
    return len(line) <= MAX_LEN

file_path = input()
with open(file_path) as f:
    for (i, line) in enumerate(f, start=1):
        if not check_len(line):
            print(f'Line {i}: S001 Too long')

