import re

r'(?=\w{2,}@[a-zA-Z]{2,}\.[a-zA-Z]{2,})(?=^[a-zA-Z])'
r'(?=\w{4,})(?!^\d)'

re1=r'^\d*$'

str1='1212'

print(re.match(re1,str1))