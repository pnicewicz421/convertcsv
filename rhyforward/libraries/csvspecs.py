#HMIS Logic

CSVFiles = ['organization.csv', 'project.csv', 'funder.csv', 'projectcoc.csv', 'inventory.csv',
            'site.csv', 'affiliation.csv', 'client.csv', 'enrollment.csv', 'enrollmentcoc.csv',
            'exit.csv', 'incomebenefits.csv', 'healthanddv.csv', 'employmentandeducation.csv', 
            'disabilities.csv', 'services.csv']    
            
class CSVFile(object):
    # The object for each required CSV file.
    # Has the name, number of max records, and a list of Fields 
    # corresponding to each required field. 
    
    def __init__(self, name, maxrecords=-1):
        self.name = name
        self.maxrecords = maxrecords
        self.fields = []
        
    def addField(self, field):
        #Add a required field (a Field object) to the name
        self.fields.append(field)
        
    def listFields(self):
        return self.fields
        
class Field(object):
    
    def __init__(self, dtype, maxchars=0, null=False, List=[], format="", dataElement="", unique=False, related=""):
        # Initiates a field 
        # Each field has the following args:
        # dtype: data type of field (string) (options: 'D', 'T', 'I', 'M', 'M+', 'S')
        # maxchars: number of max chars if dtype is a string, otherwise None (integer)
        # null: True if field is allowed to be null; otherwise False (Boolean)
        # List: allowable responses (list of integers)
        # format: additional formatting requirements in RegEx (string)
        # dataElement: the HMIS data element number, if any (string)
        # unique: Unique identifier (cannot have duplicates within file) (Boolean)
        # related: Must match another Field (Field type)
        
        self.dtype = dtype
        self.maxchar = maxchars
        self.null = null
        self.List = List
        self.format = format
        self.dataElement = dataElement
        self.unique = unique
        self.related = related
        #self.CSVFile.AddField(self)
        
#CSV Specs

#Export File - export.csv
ExportFile = CSVFile('export.csv', 1)
ExportID = Field('S', 32, False)
ExportFile.addField(ExportID)
SourceID = Field('S', 32, True)
ExportFile.addField(SourceID)
SourceName = Field('S', 50, True)
ExportFile.addField(SourceName)
SourceContactFirst = Field('S', 50, True)
ExportFile.addField(SourceContactFirst)
SourceContactLast = Field('S', 50, True)
ExportFile.addField(SourceContactLast)
SourceContactPhone = Field('S', 10, True, format="[2-9][0-9]{2}[2-9][0-9]{2}[0-9]{4}")
ExportFile.addField(SourceContactPhone)
SourceContactExtension = Field('S', 5, True, format="[0-9]{1,5}]")
ExportFile.addField(SourceContactExtension) 
SourceContactEmail = Field('S', 70, True, format="(([A-Za-z0-9]+_+)|([A-Za-z0-9]+\-+)|([A-Za-z0-9]+\.+)|([A-Za-z0-9]+\++))*[A-Za-  z0-  9]+@((\w+\  -+)|(\w+\.))*\w{1,63}\.[a-zA-Z]{2,6}")
ExportFile.addField(SourceContactEmail)
ExportDate = Field('T')
ExportFile.addField(ExportDate)
ExportStartDate = Field('D')
ExportFile.addField(ExportStartDate)
ExportEndDate = Field('D')
ExportFile.addField(ExportEndDate)
SoftwareName = Field('S', 50)
ExportFile.addField(SoftwareName)
SoftwareVersion = Field('S', 50, null=True)
ExportFile.addField(SoftwareVersion)
ExportPeriodType = Field('I', List=[1, 2, 3, 4])
ExportFile.addField(ExportPeriodType)
ExportDirective = Field('I', List=[1, 2, 3])
ExportFile.addField(ExportDirective)
HashStatus = Field('I', List=[1, 2, 3])
ExportFile.addField(HashStatus)

#Project Descriptor Files
#Organization.csv
#One Record in Organization.csv for each OrganizationID in Project.csv
# Each field has the following args:
        # dtype: data type of field (string) (options: 'D', 'T', 'I', 'M', 'M+', 'S')
        # maxchars: number of max chars if dtype is a string, otherwise None (integer)
        # null: True if field is allowed to be null; otherwise False (Boolean)
        # List: allowable responses (list of integers)
        # format: additional formatting requirements in RegEx (string)
        # dataElement: the HMIS data element number, if any (string)
        
OrganizationFile = CSVFile('organization.csv')
OrganizationID = Field('S', 32, unique=True, dataElement="2.1.1")
OrganizationFile.addField(OrganizationID)
OrganizationName = Field('S', 50, dataElement="2.1.2")
OrganizationFile.addField(OrganizationName)
OrganizationCommonName = Field('S', 50, null=True)
OrganizationFile.addField(OrganizationCommonName)
DateCreated = Field('T')
OrganizationFile.addField(DateCreated)
DateUpdated = Field('T')
OrganizationFile.addField(DateUpdated)
UserID = Field('S', 32)
OrganizationFile.addField(UserID)
DateDeleted = Field('T')
OrganizationFile.addField(DateDeleted)
ExportID1 =  Field('S', 32, related=ExportID) #must match ExportID in Export.csv
OrganizationFile.addField(ExportID1)

#Project.csv
ProjectFile = CSVFile('project.csv')
ProjectID = Field('S', 32, dataElement="2.2.1", unique=True)
ProjectFile.addField(ProjectID)
OrganizationID1 = Field('S', 32, related=OrganizationID)
ProjectFile.addField(OrganizationID1)
ProjectName = Field('S', 50, null=True, dataElement="2.2.2")
ProjectFile.addField(ProjectName)
ProjectCommonName = Field('S', 50, null=True)
ProjectFile.addField(ProjectCommonName)
ContinuumProject = Field('I', List=[0, 1, 99])
ProjectFile.addField(ContinuumProject)
ProjectType = Field('I', List=range(1, 15), null=True, dataElement="2.4.2")# may be null if ContinuumProject != 1
ProjectFile.addField(ProjectType)
ResidentialAffiliation = Field('I', List=[0, 1, 99], null=True, dataElement="2.4.A") #may be null if ProjectType != 6
ProjectFile.addField(ResidentialAffiliation)
TrackingMethod = Field('I', List=[0, 3], null=True, dataElement="2.5.1") # may be null if ProjecType != 1
ProjectFile.addField(TrackingMethod)
TargetPopulation = Field('I', List=[1,3,4], null=True, dataElement="2.9.1")
ProjectFile.addField(TargetPopulation)
PITCount = Field('I', null=True)
ProjectFile.addField(PITCount)
DateCreated1 = Field('T')
ProjectFile.addField(DateCreated1)
DateUpdated1 = Field('T')
ProjectFile.addField(DateUpdated1)
UserID1 = Field('S', 32)
ProjectFile.addField(UserID)
DateDeleted1 = Field('T',null=True)
ProjectFile.addField(DateDeleted)
ExportID3 = Field('S', 32, related=ExportID)
ProjectFile.addField(ExportID3)

#Funder.csv
#One record in funder.csv for each record in project.csv where
#ContinuumProject =1
FunderFile = CSVFile('funder.csv')
FunderID = Field('S', 32, unique=True)
ProjectID2 = Field('S', 32, related=ProjectID)
Funder = Field('I', List=range(1, 35), dataElement="2.6.1")
GrantID = Field('S', 32, null=True, dataElement="2.6.2")
StartDate = Field('D', dataElement="2.6.3")
EndDate = Field('D', null=True, dataElement="2.6.4")
DateCreated2 = Field('T')
DateUpdated2 = Field('T')
UserID2 = Field('S', 32)
DateDeleted2 = Field('T', null=True)
ExportID4 = Field('S', 32, related=ExportID)


#ProjectCoC.csv
ProjectCoC = CSVFile('projectcoc.csv')
ProjectCoCID = Field('S', 32, unique=True)
ProjectID3 = Field('s', 32, related=ProjectID)
CoCCode = Field('S', 6, dataElement="2.3.1", format="^[a-zA-Z]{2}-[0-9]{3}$")
DateCreated = Field('T')
DateUpdated = Field('T')
UserID = Field('S', 32)
DateDeleted = Field('T', null=True)
ExportID5 = Field('S', 32, related=ExportID)

#Inventory.csv
InventoryID = Field('S', 32, unique=True)
ProjectID4 = Field('S', 32, related=ProjectID)
CoCCode2 = Field('S', 6, related=CoCCode)
InformationDate = Field('D', dataElement="2.7.1")
HouseholdType = Field('I', List=[1, 3, 4], dataElement="2.7.2")
BedType = Field('I', List=[1, 2, 3], dataElement="2.7.3", null=True) #Null ProjectType=1
Availability = Field('I', List=[1, 2, 3], dataElement="2.7.4", null=True) #Null unless ProjectType = 1 
UnitInventory = Field('I', dataElement="2.7.5")
BedInventory = Field('I', dataElement="2.7.5")
CHBedInventory = Field('I', null=True, dataElement="2.7.A")
VetBedInventory = Field('I', null=True, dataElement="2.7.A")
YouthBedInventory = Field('I', null=True, dataElement="2.7.A")
YouthAgeGroup = Field('I', List=[1, 2, 3], null=True, dataElement="2.7.B")
InventoryStartDate = Field('D', null=True, dataElement="2.7.6")
InventoryEndDate = Field('D', null=True, dataElement="2.7.7")
HMISParticipatingBeds = Field('I', dataElement="2.7.8")
DateCreated = Field('T')
DateUpdated = Field('T')
UserID = Field('S', 32)
DateDeleted = Field('T', null=True)
ExportID6 = Field('S', 32, related=ExportID)

#Site.csv
SiteID = Field('S', 32)


#Affiliation.csv

#Clients
#Client.csv

#Enrollment Files
#Enrollment.csv
#EnrollmentCoC.csv
#Exit.csv
#IncomeBenefits.csv

