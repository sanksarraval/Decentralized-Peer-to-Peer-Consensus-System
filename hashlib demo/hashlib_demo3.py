import hashlib

b1={   'hash': '9efb33ec9e0ed0a7e837d68d127dff33dba4290ba2535d2312a76f4f00000000',
    'height': 0,
    'messages': [   '3010 rocks',
                    'Warning:',
                    'Procrastinators',
                    'will be sent back',
                    'in time to start',
                    'early.',
                    'Chain 2'],
    'minedBy': 'Prof!',
    'nonce': '967128957948859',
    'timestamp': 1700841637,
    'type': 'GET_BLOCK_REPLY'}


# genesis
m = hashlib.sha256()
m.update('Prof!'.encode())
m.update('3010 rocks'.encode()) 
m.update('Warning:'.encode()) 
m.update('Procrastinators'.encode()) 
m.update('will be sent back'.encode()) 
m.update('in time to start'.encode()) 
m.update('early.'.encode()) 
m.update('Chain 2'.encode()) 
timestamp = int(1700841637)
m.update(timestamp.to_bytes(8, 'big')) # when
m.update('967128957948859'.encode()) # nonce
print('9efb33ec9e0ed0a7e837d68d127dff33dba4290ba2535d2312a76f4f00000000') # should be
print(m.hexdigest()) # is

#next block
b2 = {   'hash': 'f736b5ab33d68fd5f9a45e3ecf48615af1db8a2543e3e0d9bb5063bd00000000',
    'height': 1,
    'messages': [   'cattiness',
                    'carousal',
                    'nominees',
                    "Hokkaido's",
                    'overtimes',
                    "freebie's",
                    'beastliest',
                    'Brazil',
                    'jinricksha',
                    'renewed'],
    'minedBy': 'Prof!',
    'nonce': '9459302409010',
    'timestamp': 1700872826,
    'type': 'GET_BLOCK_REPLY'}

m = hashlib.sha256()
m.update('9efb33ec9e0ed0a7e837d68d127dff33dba4290ba2535d2312a76f4f00000000'.encode())
m.update('Prof!'.encode())
m.update('cattiness'.encode())
m.update('carousal'.encode())
m.update('nominees'.encode())
m.update("Hokkaido's".encode())
m.update('overtimes'.encode())
m.update("freebie's".encode())
m.update('beastliest'.encode())
m.update('Brazil'.encode())
m.update('jinricksha'.encode())
m.update('renewed'.encode())
m.update(int(1700872826).to_bytes(8,'big'))
m.update('9459302409010'.encode())

print('f736b5ab33d68fd5f9a45e3ecf48615af1db8a2543e3e0d9bb5063bd00000000')
print(m.hexdigest())
