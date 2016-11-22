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
    b = hashlib.sha1(a).hexdigest()
    clientfile.ix[n, 'MiddleName'] = b
    
    
for n in range(clientfile.shape[0]):
    a = clientfile.ix[n, 'LastName']
    if a is np.nan:
        a = ''
    b = hashlib.sha1(a).hexdigest()
    clientfile.ix[n, 'LastName'] = b
    
    
for n in range(clientfile.shape[0]):
    a = clientfile.ix[n, 'SSN']
    if isnan(a):
        a = ''
    else:
        a = str(int(a))
    b = hashlib.sha1(a).hexdigest()
    clientfile.ix[n, 'SSN'] = b
