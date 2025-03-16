import hashlib

# genesis
m = hashlib.sha256()
m.update('Prof!'.encode())
m.update('Keep it'.encode())
m.update('simple.'.encode()) 
m.update('Veni'.encode()) 
m.update('vidi'.encode()) 
m.update('vici'.encode()) 
timestamp = int(1730910874)
m.update(timestamp.to_bytes(8, 'big')) # when
m.update('663135608617883'.encode()) # nonce
print('75977fa09516d028befa0695e16c93be20271b66630236d38718e35700000000') # should be
print(m.hexdigest()) # is

#next block


m = hashlib.sha256()
m.update('75977fa09516d028befa0695e16c93be20271b66630236d38718e35700000000'.encode())
m.update('Prof!'.encode())
m.update('test'.encode())
m.update(int(1730974785).to_bytes(8,'big'))
m.update('4776171179467'.encode())

print('5c25ae996e712fc8e93c10a1b9fd3b42dd408aaa65f4c3e4dfe8982800000000')
print(m.hexdigest())
