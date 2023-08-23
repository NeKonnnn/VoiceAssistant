from googlesearch import search

query = 'python'

for i in search(query, tld="com", lang='ru', num=5,
                start=0, stop=5, pause=2):
    print(i)