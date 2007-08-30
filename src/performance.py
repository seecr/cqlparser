from time import time
from cqlparser import parseString
start = time()
for i in range(1000):
  parseString("aap")
print (time() - start)
  
