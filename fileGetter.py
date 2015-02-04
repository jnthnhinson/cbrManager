import fnmatch
import os

path = '/Users/jnthnhinson/Documents/Comics'
matches = []
for root, dirnames, filenames in os.walk(path):
  for filename in fnmatch.filter(filenames, '*.txt'):
    matches.append(os.path.join(root, filename))
    
print matches

pathLength = len(path.split('/'))
f = open(path + '/allFiles.text', 'w')
for file in matches:
    parts = file.split('/')
    for i in range(pathLength, len(parts)):
        f.write(parts[i])
        if (i + 1 != len(parts)): f.write(';')
    f.write('\n')
f.close()
    
