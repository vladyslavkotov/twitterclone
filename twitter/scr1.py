import re

r'(?=\w{2,}@[a-zA-Z]{2,}\.[a-zA-Z]{2,})(?=^[a-zA-Z])'
r'(?=\w{4,})(?!^\d)'

re1=r'\n{3,}'
str1="kakwjdhawd\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\nkajwhd"

print(re.sub("(\r\n){3,}","\n\r",str1))