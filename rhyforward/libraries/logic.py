#Libraries File 
import zipfile 
import rhyforward.libraries.csvspecs as csv

#Functions for Processing Files and Data
#Uses Specs founds in CSVSpecs


def CheckifZipFile(filename):
### Check to see if the filename object is a valid zip file. Input: FileUpload object. Output: Boolean ###
    return zipfile.is_zipfile(filename.filename)
    
def CheckifRightMembers(filename):
    #check to see if the zip file has right members
    testzip = zipfile.ZipFile(filename.filename, 'r')
    filedir = str(filename.filename) + '/' #Create a directory name. If directory name already exists, create a _# system
   # if filedir in models. #
    namelist = testzip.namelist()
    revlist = []
    for nm in namelist:
        if nm in csv.CSVFiles and nm not in revlist:
            testzip.extract(nm, filedir) #'files/'
            revlist.append(nm)
    return revlist
    
#def ExtractMembers(filename):
    #Extract members from a file
    #Create a directory
    #Store files in directory
 #   zip = zipfile.ZipFile(filename.filename, 'r')
  #  for m in zip:
   #     if m in csv.CSVFiles:
    #        zipfile.ZipFile.extract(m)
    #return True