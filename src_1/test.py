y1 = 0
x1 = []

def recurse(x,y):
    x.append(y)
    print(x)
    print(y)
    if y > 8:
        x.pop()
        return
    else:
        recurse(x,y+1)
    print(x)
    print(y)
    x.pop()
    
recurse(x1,y1)

print('\n')
x1 = [0,1,2,3,4,5,6,7,8,9]

for i in reversed (x1):
    print(i, end = " ")

print('\n')
print(x1[len(x1)-1])

x1 = {}

x1['apples'] = 3
x1['oranges'] = 5
print(x1['apples'])
print(x1['oranges'])

if 'oranges' in x1:
    print('We have 5 oranges\n')
else:
    print('We have no oranges')
    
    
for k in x1:
    print (f'We have {x1[k]} {k}\n');
    
#x1[['bananas', 'grapefruit']] = 7 # no worky worky
x1[('squash', 'watermelon')] = 9

for k in x1:
    print (k)
    
test = list()

for item in test:
    print("found item")
else:
    print("no items")
    
test = True 

if test is True:
    print('test is true')