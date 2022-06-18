




class Text:
    
    strings = []
    len_lines = 10
    num_lines = 1
    def __init__(self, num_lines=1, len_lines=10):
        Text.len_lines = len_lines
        Text.num_lines = num_lines

    
    def add(self, string):
        while True:
            if len(string) == 0:
                break
            tmp = string[:Text.len_lines]
            string = string.replace(tmp, '')
            Text.strings.append(tmp)
        Text.strings = Text.strings[-Text.num_lines:]

    
    def text(self):
        return '' if not Text.strings else '\n'.join(Text.strings)


TextInfo = Text(len_lines=40, num_lines=20)






if __name__ == "__main__":
    ...






















