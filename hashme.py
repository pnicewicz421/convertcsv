#hashing algorithm
import pandas as pd
import numpy as np
import hashlib

clientfile = pd.read_csv('client.csv')
for n in range(clientfile.shape[0]):
    a = clientfile.ix[n, 'FirstName']
    if a is np.nan:
        a = ''
    b = hashlib.sha1(a).hexdigest()
    clientfile.ix[n, 'FirstName'] = b
    
    
for n in range(clientfile.shape[0]):
    a = clientfile.ix[n, 'MiddleName']
    if a is np.nan:
        a = ''
    else:
        a = str(a)
    b = hashlib.sha1(a).hexdigest()
    clientfile.ix[n, 'MiddleName'] = b
    
    
for n in range(clientfile.shape[0]):
    a = clientfile.ix[n, 'LastName']
    if a is np.nan:
        a = ''
    b = hashlib.sha1(a).hexdigest()
    clientfile.ix[n, 'LastName'] = b

filen = clientfile
n = 'SSN'
if (filen[n].notnull().sum() > 0): 
    as_object = filen[n].fillna(0).astype(np.int64).astype(np.object)
    as_object[filen[n].isnull()] = ''
    filen[n] = as_object
    clientfile[n] = filen[n]

for n in range(clientfile.shape[0]):
    a = clientfile.ix[n, 'SSN']
    if a is np.nan:
        a = ''
    else:
        a = str(a)
    b = hashlib.sha1(a).hexdigest()
    clientfile.ix[n, 'SSN'] = b