word='ىفاض'
lst=['يفاص','ةصالخ']
t=list()
for y in lst:
    DP=list()
    l=list()
    for i in range(len(word)+1):
        DP.append(list())
        for j in range(len(y)+1):
            DP[i].append(0)
    for i in range(len(word)):
        for j in range(len(y)):
            if word[i]==y[j]:
                DP[i+1][j+1]=DP[i][j]+1
    for i in DP:
        l.append(max(i))
    t.append(max(l)/len(y))
print(t)