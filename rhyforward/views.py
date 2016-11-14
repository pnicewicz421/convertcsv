from django.shortcuts import render, redirect
from django.http import HttpResponse

from forms import UploadFileForm
from models import FileUpload

import zipfile

import numpy as np
import pandas as pd
from pandas import Series, DataFrame


# Create your views here.
def index_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES) #form
        if form.is_valid():
            #save the file into the database 
            fileupload = FileUpload(filename = request.FILES['filename'], email = request.POST['email'])
            fileupload.save()
            # html = '<html><body>The form was valid. Form was %s. Filename was %s (model). finally, in the post request. Request.FILES[\'filename\'] was %s </body></html>' % (form, filename, request.FILES['filename'])
            return redirect('/handlefile')
        return HttpResponse("<html><body>Form was not valid</body></html>")
    else:
        form = UploadFileForm() #empty, unbound form
        files = FileUpload.objects.all()
        return render(request, 'index.html', {'form': form})
        
def handle_file(request):
    length = len(FileUpload.objects.all())
    file = FileUpload.objects.all()[length - 1] #get the latest file (again, the actual filename, and the email)
    
    #Series of Checks

    #First Check if the file is a zip file
    if not zipfile.is_zipfile(file.filename):
    	return HttpResponse("<html><body>The file you provided is not a zip file. Please try again.</body></html>")

    #Second check to make sure the csv files are in place
    #and extract files
    CSVFiles = ['Export.csv', 'Project.csv', 'ProjectCoC.csv', 'Funder.csv', 'Client.csv',
            'Enrollment.csv', 'EnrollmentCoC.csv',
            'Exit.csv', 'IncomeBenefits.csv', 'Disabilities.csv', 'HealthAndDV.csv', 
            'EmploymentEducation.csv', 'Services.csv']   

    testzip = zipfile.ZipFile(file.filename, 'r')
    filedir = 'upload' + str(length - 1) + '/' #Create a directory name (upload + number)

    namelist = testzip.namelist()

    revlist = []
    missing = []
    for nm in CSVFiles:
    	if nm in namelist and nm not in revlist:
    		testzip.extract(nm, filedir)
    		revlist.append(nm)
    	else:
    		missing.append(nm)
    if len(missing) > 0:
    	html = "<html><body>The following files were missing from the ZIP file: %s </body></html>" % missing
    	return HttpResponse(html)

    #Third make sure that the structure is 4.1	-- i.e., columns match up
    #CSV columns is a list of lists of all columns in all CSV files 
    CSVcolumns = [['ExportID', 'SourceID', 'SourceName', 'SourceContactFirst', 'SourceContactLast',
    				'SourceContactPhone', 'SourceContactExtension', 'SourceContactEmail', 'ExportDate',
    				'ExportStartDate', 'ExportEndDate', 'SoftwareName', 'SoftwareVersion', 'ExportPeriodType',
    				'ExportDirective', 'HashStatus'], 
    				['ProjectID', 'OrganizationID', 'ProjectName', 'ProjectCommonName', 'ContinuumProject',
    				'ProjectType', 'ResidentialAffiliation', 'TrackingMethod', 'TargetPopulation', 'PITCount', 'DateCreated',
    				'DateUpdated', 'UserID', 'DateDeleted', 'ExportID'],
    				['ProjectCoCID', 'ProjectID', 'CoCCode', 'DateCreated', 'DateUpdated', 'UserID',
    				'DateDeleted', 'ExportID'],
    				['FunderID', 'ProjectID', 'Funder', 'GrantID', 'StartDate', 'EndDate', 'DateCreated', 'DateUpdated',
    				'UserID', 'DateDeleted', 'ExportID'],
    				['PersonalID', 'FirstName', 'MiddleName', 'LastName', 'NameSuffix', 'NameDataQuality',
    				'SSN', 'SSNDataQuality', 'DOB', 'DOBDataQuality', 'AmIndAKNative', 'Asian', 'BlackAfAmerican',
    				'NativeHIOtherPacific', 'White', 'RaceNone', 'Ethnicity', 'Gender', 'OtherGender', 'VeteranStatus',
    				'YearEnteredService', 'YearSeparated', 'WorldWarII', 'KoreanWar', 'VietnamWar', 'DesertStorm',
    				'AfghanistanOEF', 'IraqOIF', 'IraqOND', 'OtherTheater', 'MilitaryBranch', 'DischargeStatus',
    				'DateCreated', 'DateUpdated', 'UserID', 'DateDeleted', 'ExportID'],
    				['ProjectEntryID', 'PersonalID', 'ProjectID', 'EntryDate', 'HouseholdID', 'RelationshipToHoH',
    				'ResidencePrior', 'OtherResidencePrior', 'ResidencePriorLengthOfStay', 'DisablingCondition',
    				'EntryFromStreetESSH', 'DateToStreetESSH', 'TimesHomelessPastThreeYears', 'MonthsHomelessPastThreeYears',
    				'HousingStatus', 'DateOfEngagement', 'InPermanentHousing', 'ResidentialMoveInDate', 'DateOfPATHStatus',
    				'ClientEnrolledInPATH', 'ReasonNotEnrolled', 'WorstHousingSituation', 'PercentAMI', 'LastPermanentStreet',
    				'LastPermanentCity', 'LastPermanentState', 'LastPermanentZIP', 'AddressDataQuality', 'DateOfBCPStatus',
    				'FYSBYouth', 'ReasonNoServices', 'SexualOrientation', 'FormerWardChildWelfare', 'ChildWelfareYears',
    				'ChildWelfareMonths', 'FormerWardJuvenileJustice', 'JuvenileJusticeYears', 'JuvenileJusticeMonths', 'HouseholdDynamics',
    				'SexualOrientationGenderIDYouth', 'SexualOrientationGenderIDFam', 'HousingIssuesYouth', 'HousingIssuesFam',
    				'SchoolEducationalIssuesYouth', 'SchoolEducationalIssuesFam', 'UnemploymentYouth', 'UnemploymentFam',
    				'MentalHealthIssuesYouth', 'MentalHealthIssuesFam', 'HealthIssuesYouth', 'HealthIssuesFam', 'PhysicalDisabilityYouth',
    				'PhysicalDisabilityFam', 'MentalDisabilityYouth', 'MentalDisabilityFam', 'AbuseAndNeglectYouth',
    				'AbuseAndNeglectFam', 'AlcoholDrugAbuseYouth', 'AlcoholDrugAbuseFam', 'InsufficientIncome', 'ActiveMilitaryParent',
    				'IncarceratedParent', 'IncarceratedParentStatus', 'ReferralSource', 'CountOutreachReferralApproaches', 'ExchangeForSex',
    				'ExchangeForSexPastThreeMonths', 'CountOfExchangeForSex', 'AskedOrForcedToExchangeForSex', 'AskedOrForcedToExchangeForSexPastThreeMonths',
    				'WorkPlaceViolenceThreats', 'WorkplacePromiseDifference', 'CoercedToContinueWork', 'LaborExploitPastThreeMonths',
    				'HPScreeningScore', 'VAMCStation', 'DateCreated', 'DateUpdated', 'UserID', 'DateDeleted', 'ExportID'],
    				['EnrollmentCoCID', 'ProjectEntryID', 'ProjectID', 'PersonalID', 'InformationDate', 'CoCCode', 'DataCollectionStage',
    				'DateCreated', 'DateUpdated', 'UserID', 'DateDeleted', 'ExportID'],
    				['ExitID', 'ProjectEntryID', 'PersonalID', 'ExitDate', 'Destination', 'OtherDestination', 'AssessmentDisposition',
    				'OtherDisposition', 'HousingAssessment', 'SubsidyInformation', 'ConnectionWithSOAR', 'WrittenAftercarePlan', 'AssistanceMainstreamBenefits',
    				'PermanentHousingPlacement', 'TemporaryShelterPlacement', 'ExitCounseling', 'FurtherFollowUpServices', 'ScheduledFollowUpContacts',
    				'ResourcePackage', 'OtherAftercarePlanOrAction', 'ProjectCompletionStatus', 'EarlyExitReason', 'FamilyReunificationAchieved',
    				'DateCreated', 'DateUpdated', 'UserID', 'DateDeleted', 'ExportID'],
    				['IncomeBenefitsID', 'ProjectEntryID', 'PersonalID', 'InformationDate', 'IncomeFromAnySource', 'TotalMonthlyIncome', 'Earned',
    				'EarnedAmount', 'Unemployment', 'UnemploymentAmount', 'SSI', 'SSIAmount', 'SSDI', 'SSDIAmount', 'VADisabilityService',
    				'VADisabilityServiceAmount', 'VADisabilityNonService', 'VADisabilityNonServiceAmount', 'PrivateDisability', 'PrivateDisabilityAmount',
    				'WorkersComp', 'WorkersCompAmount', 'TANF', 'TANFAmount', 'GA', 'GAAmount', 'SocSecRetirement', 'SocSecRetirementAmount', 'Pension', 'PensionAmount',
    				'ChildSupport', 'ChildSupportAmount', 'Alimony', 'AlimonyAmount', 'OtherIncomeSource', 'OtherIncomeAmount', 'OtherIncomeSourceIdentify', 'BenefitsFromAnySource',
    				'SNAP', 'WIC', 'TANFChildCare', 'TANFTransportation', 'OtherTANF', 'RentalAssistanceOngoing', 'RentalAssistanceTemp', 'OtherBenefitsSource', 'OtherBenefitsSourceIdentify',
    				'InsuranceFromAnySource', 'Medicaid', 'NoMedicaidReason', 'Medicare', 'NoMedicareReason', 'SCHIP', 'NoSCHIPReason', 'VAMedicalServices',
    				'NoVAMedReason', 'EmployerProvided', 'NoEmployerProvidedReason', 'COBRA', 'NoCOBRAReason', 'PrivatePay', 'NoPrivatePayReason', 'StateHealthIns',
    				'NoStateHealthInsReason', 'HIVAIDSAssistance', 'NoHIVAIDSAssistanceReason', 'ADAP', 'NoADAPReason', 'DataCollectionStage', 'DateCreated', 'DateUpdated',
    				'UserID', 'DateDeleted', 'ExportID'],
    				['DisabilitiesID', 'ProjectEntryID', 'PersonalID', 'InformationDate', 'DisabilityType', 'DisabilityResponse', 'IndefiniteAndImpairs', 
    				'DocumentationOnFile', 'ReceivingServices', 'PATHHowConfirmed', 'PATHSMIInformation', 'TCellCountAvailable', 'TCellCount', 'TCellSource',
    				'ViralLoadAvailable', 'ViralLoad', 'ViralLoadSource', 'DataCollectionStage', 'DateCreated', 'DateUpdated', 'UserID', 'DateDeleted', 'ExportID'],
    				['HealthAndDVID', 'ProjectEntryID', 'PersonalID', 'InformationDate', 'DomesticViolenceVictim', 'WhenOccurred', 'CurrentlyFleeing', 'GeneralHealthStatus',
    				'DentalHealthStatus', 'MentalHealthStatus', 'PregnancyStatus', 'DueDate', 'DataCollectionStage', 'DateCreated', 'DateUpdated', 'UserID',
    				'DateDeleted', 'ExportID'],
    				['EmploymentEducationID', 'ProjectEntryID', 'PersonalID', 'InformationDate', 'LastGradeCompleted', 'SchoolStatus', 'Employed', 'EmploymentType', 'NotEmployedReason',
    				'DataCollectionStage', 'DateCreated', 'DateUpdated', 'UserID', 'DateDeleted', 'ExportID'],
    				['ServicesID', 'ProjectEntryID', 'PersonalID', 'DateProvided', 'RecordType', 'TypeProvided', 'OtherTypeProvided', 'SubTypeProvided', 'FAAmount', 'ReferralOutcome',
    				'DateCreated', 'DateUpdated', 'UserID', 'DateDeleted', 'ExportID']]

    errorfiles = []

    for n in range(len(CSVFiles)):
    	error = []
    	exportfile = filedir + CSVFiles[n]
    	exportcolumns = CSVcolumns[n]

    	export = pd.read_csv(exportfile)
    	filecolumns = export.columns
    	for f in range(len(exportcolumns)):
    		if f > len(filecolumns) - 1:
    			#ran out of columns
    			error.append((exportcolumns[f], 'Column Missing'))
    		elif exportcolumns[f] != filecolumns[f]:
    			error.append((exportcolumns[f], filecolumns[f]))
    	if len(error) > 0:
    		errorfiles.append((CSVFiles[n], error))
    
    if len(errorfiles) > 0:	
    	html = "<html><body>We were missing the following columns in the following files %s </body></html>" % errorfiles
    	return HttpResponse(html)

    #Make sure it is hashed

    #Make sure there is more than one enrollment in enrollment and client

    #Do the tricks!

    #First, identify whether the project is (SO, ES, or SH) or (TH, PH, or SO, DS, HP, or CE)
    projectfile = pd.read_csv('Project.csv') #Read Project.csv as a DF
    project1 = projectfile[projectfile['ProjectType'].isin([1, 4, 8])] #Select only SO, ES, or SH projects
    project2 = projectfile[projectfile['ProjectType'].isin([2, 3, 6, 9, 10, 11, 12, 13, 14])] #3.197B
    projectid1 = project1['ProjectID'] #Select projectids for 3.917A
    projectid2 = project2['ProjectID'] #Select projectids for 3.917B

    enrollmentfile = pd.read_csv('Enrollment.csv')
    enrollment1 = enrollmentfile[enrollmentfile['ProjectID'].isin(projectid1)] #select only enrollments that match project ID in one of the projects above
    
    #For both A and B, change ResidencePrior = 17--> 99
    enrollmentfile['ResidencePrior'].replace(17, 99, inplace=True)

    #A ResidencePriorLengthOfStay -- remains unchanged
    #A DateToStreetESSH --remains unchanged

    #3.917A TimesHomelessPastThreeYears 0 --> 1 
    mask = ((enrollmentfile['ProjectID'].isin(projectid1)) & (enrollmentfile['TimesHomelessPastThreeYears'] == 0)) 
    enrollmentfile.loc[mask, 'TimesHomelessPastThreeYears'] = 1 

    #A MonthsHomelessPastThreeYears remains the same

    #B Select ResidencePrior = 4, 5, 6, 7, 15, 24 and ResidencePriorLengthOfStay = 2, 3, 10, 11
    #Change LOSUnderThreshold to 1
    maskA = (((enrollmentfile['ResidencePrior'] > 3) | (enrollmentfile['ResidencePrior'] < 8) | 
    	   (enrollmentfile['ResidencePrior'] == 15) | (enrollmentfile['ResidencePrior'] == 24))
    	   	& ((enrollmentfile['ResidencePriorLengthofStay'] == 2 ) | (enrollmentfile['ResidencePriorLengthofStay'] == 3 ) |
    	   	(enrollmentfile['ResidencePriorLengthofStay'] == 10 ) | (enrollmentfile['ResidencePriorLengthofStay'] == 11 )))

    #Select ResidencePrior = 2, 3, 8, 9, 12, 13, 14, 17, 19, 20, 21, 22, 23, 25, 26, 99
    #and ResidencePriorLengthOfStay = 10, 11
    maskB = (((enrollmentfile['ResidencePrior'] == 2) | (enrollmentfile['ResidencePrior'] == 3) | (enrollmentfile['ResidencePrior'] == 8) |
    		(enrollmentfile['ResidencePrior'] == 9) | (enrollmentfile['ResidencePrior'] == 12) | (enrollmentfile['ResidencePrior'] == 13) |
    		(enrollmentfile['ResidencePrior'] == 14) | (enrollmentfile['ResidencePrior'] == 17) | (enrollmentfile['ResidencePrior'] == 19) |
    		(enrollmentfile['ResidencePrior'] == 20) | (enrollmentfile['ResidencePrior'] == 21) | (enrollmentfile['ResidencePrior'] == 22) |
    		(enrollmentfile['ResidencePrior'] == 23) | (enrollmentfile['ResidencePrior'] == 25) | (enrollmentfile['ResidencePrior'] == 26) |
    		(enrollmentfile['ResidencePrior'] == 99)) & ((enrollmentfile['ResidencePriorLengthofStay'] == 10 ) | (enrollmentfile['ResidencePriorLengthofStay'] == 11 )))

    #LOSUnderThreshold: for 3.917B projects, input 1 where they fit the one of the two masks or otherwise 0 
    enrollmentfile.loc[enrollmentfile['ProjectID'].isin(projectid2), 'LOSUnderThreshold'] = np.where(((maskA == True) | (maskB == True)), 1, 0)

    #New Element PreviousStreetESSH
    #Select ResidencePrior = 1, 16, 18 and EntryFromStreetESSH = 8, 9, 99
    maskC = ((enrollmentfile['ResidencePrior'] == 1) | (enrollmentfile['ResidencePrior'] == 16) | (enrollmentfile['ResidencePrior'] == 18))

    #Set PreviousStreetESSH = 0

    #Select ResidencePrior = 4, 5, 6,  7, 15, 24 and ResidencePriorLengthOfStay = 2, 3, 10, 11 (maskA) EntryFromStreetESSH = 8, 9, 99
    #Set PreviousStreetESSH = 0

    ##Select ResidencePrior = 2, 3, 8, 9, 12, 13, 14, 17, 19, 20, 21, 22, 23, 25, 26, 99
    #and ResidencePriorLengthOfStay = 10, 11 (maskB) and EntryFromStreetESSH = 8, 9, 99, 0
    maskD = ((enrollmentfile['EntryFromStreetESSH'] == 0) | (enrollmentfile['EntryFromStreetESSH'] == 8) | (enrollmentfile['EntryFromStreetESSH'] == 9) | (enrollmentfile['EntryFromStreetESSH'] == 99))
    #Set PreviousStreetESSH = 0 

    #For 3.917B projects, input 1 for maskA, maskB, or maskC or 0 in PreviousStreetESSH
    enrollmentfile.loc[enrollmentfile['ProjectID'].isin(projectid2), 'PreviousStreetESSH'] = np.where((((maskA == True) | (maskB == True) | (maskC = True)) & (maskD == True)), 0, 1)

    #Carry over date when maskE = ResidencePrior = 1, 16, 18 or maskA or maskB
    maskE = ((enrollmentfile['ResidencePrior'] = 1) | (enrollmentfile['ResidencePrior'] = 16) | (enrollmentfile['ResidencePrior'] = 18))
    
    #For 3.917B projects,  if they are not one of the carry over fields, set that field to blank.
    enrollmentfile.loc[(((maskA == False) & (maskB == False) & (maskE == False)) & enrollmentfile['ProjectID'].isin(projectid2)), 'DateToStreetESSH'] = ''

    #For 3.917B projects, maskE or maskA or maskB --> enrollment TimesHomelessPastThreeYears 0 --> 1
    enrollmentfile.loc[enrollmentfile['ProjectID'].isin(projectid2), 'TimesHomelessPastThreeYears'] = np.where(((maskA == True) | (maskB == True) | (maskE == True)), 0, 1)

    #!(maskE or maskA or maskB) --> enrollment MonthsHomelessPastThreeYears --> ''
    enrollmentfile.loc[(((maskA == False) & (maskB == False) & (maskE == False)) & enrollmentfile['ProjectID'].isin(projectid2)), 'MonthsHomelessPastThreeYears'] = ''


    #enrollmentfile
#def CheckifRightMembers(filename):
 #   #check to see if the zip file has right members
  #  

    # first check to see if it's a zip file
    #response = lg.CheckifZipFile(file.filename)
    #if not response:
   # 	return HttpResponse("<html><body>The file you provided is not a zip file. Please try again.</body></html>")
   # filedir = lg.CheckifRightMembers(file.email)
    
    #Extract each member (note: not all files necessarily) and save each file on the disk (not read into memory)
    #mmm = lg.ExtractMembers(ZIPfile)
    
    #Go through the Files that have Fields with Hash requirements
    
    #processhash = lg.CheckifHashed(filename)
    
    #Attempt to Hash it for them.
    
    
    