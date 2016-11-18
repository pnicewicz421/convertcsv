from django.shortcuts import render, redirect
from django.http import HttpResponse

from forms import UploadFileForm
from models import FileUpload

import os

import zipfile

import numpy as np
import pandas as pd
from pandas import Series, DataFrame

# Import smtplib for the actual sending function
import smtplib

# Here are the email package modules we'll need
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


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

    #csv converted into dataframes will be saved in export:
    # 0: export
    # 1: project
    # 2: projectcoc
    # 3: funder
    # 4: client
    # 5: enrollment
    # 6: enrollmentcoc
    # 7: exit
    # 8: incomebenefits
    # 9: disabilities
    # 10: healthanddv
    # 11: employmenteducation
    # 12: services

    errorfiles = []
    export = []

    for n in range(len(CSVFiles)):
    	error = []
    	exportfile = filedir + CSVFiles[n]
    	exportcolumns = CSVcolumns[n]

    	export.append(pd.read_csv(exportfile))
    	filecolumns = export[n].columns
    	for f in range(len(exportcolumns)):
            if (f > len(filecolumns) - 1):
                #ran out of columns
                error.append((exportcolumns[f], 'Column Missing'))
            elif (exportcolumns[f].lower() != filecolumns[f].lower()):
                error.append((exportcolumns[f], filecolumns[f]))
            elif (exportcolumns[f] != filecolumns[f]):
                export[n].columns = CSVcolumns[n]
                #return HttpResponse(export[n].columns)
    	if len(error) > 0:
    		errorfiles.append((CSVFiles[n], error))
    
    if len(errorfiles) > 0:	
    	html = "<html><body>We were missing the following columns in the following files %s </body></html>" % errorfiles
    	return HttpResponse(html)

    #Make sure it is hashed

    #Make sure there is more than one enrollment in enrollment and client

    #Do the tricks!

    #First, identify whether the project is (SO, ES, or SH) or (TH, PH, or SO, DS, HP, or CE)
    projectfile = export[1] #Read Project.csv as a DF
    project1 = projectfile[projectfile['ProjectType'].isin([1, 4, 8])] #Select only SO, ES, or SH projects
    project2 = projectfile[projectfile['ProjectType'].isin([2, 3, 6, 9, 10, 11, 12, 13, 14])] #3.197B institutions
    projectid1 = project1['ProjectID'] #Select projectids for 3.917A lit homeless
    projectid2 = project2['ProjectID'] #Select projectids for 3.917B institutions

    enrollmentfile = export[5]
    #enrollment1 = enrollmentfile[enrollmentfile['ProjectID'].isin(projectid1)] #113 select only enrollments that match project ID in one of the projects above
    #enrollment2 = enrollmentfile[enrollmentfile['ProjectID'].isin(projectid2)] #109 Select all ProjectID in institutions

    #LOSUnderThrehold for enrollment1 should be 99
    enrollmentfile['LOSUnderThreshold'] = 99
    enrollmentfile['ProjectID'].isin(projectid1)
    #enrollmentfile[enrollmentfile['ProjectID'].isin(projectid1)]['LOSUnderThreshold'] = 99

    #Set all institutions under 90 days 
    #enrollmentfile[(enrollmentfile['ProjectID'].isin(projectid2))]['LOSUnderThreshold'] = 1
    #& (enrollmentfile['ResidencePrior'].isin([4, 5, 6, 7, 15, 24])) & (enrollmentfile['ResidencePriorLengthOfStay'].isin([2, 3, 10, 11]))]['LOSUnderThreshold'] = 1 
    #enrollmentfile[(enrollmentfile['ProjectID'].isin(projectid2)) & (enrollmentfile['ResidencePrior'].isin([14, 23, 21, 3, 22, 19, 25, 20, 26, 12, 13, 2, 17, 8, 9, 99])) & (enrollmentfile['ResidencePriorLengthOfStay'].isin([10, 11]))]['LOSUnderThreshold'] = 1
    
    #Over 90 days
    #enrollmentfile[(enrollmentfile['ProjectID'].isin(projectid2)) & (enrollmentfile['ResidencePrior'].isin([4, 5, 6, 7, 15, 24])) & (enrollmentfile['ResidencePriorLengthOfStay'].isin([4, 5, 8, 9, 99]))]['LOSUnderThreshold'] = 0
    #enrollmentfile[(enrollmentfile['ProjectID'].isin(projectid2)) & (enrollmentfile['ResidencePrior'].isin([14, 23, 21, 3, 22, 19, 25, 20, 26, 12, 13, 2, 17, 8, 9, 99])) & (enrollmentfile['ResidencePriorLengthOfStay'].isin([2, 3, 4, 5, 8, 9, 99]))]['LOSUnderThreshold'] = 0

    #enrollmentfile[(enrollmentfile['ProjectID'].isin(projectid2)) & ~(enrollmentfile['ResidencePrior'].isin([4, 5, 6, 7, 15, 24, 14, 23, 21, 3, 22, 19, 25, 20, 26, 12, 13, 2, 17, 8, 9, 99]))]['LOSUnderThreshold'] = 99
    
    #For both A and B, change ResidencePrior = 17--> 99
    #enrollmentfile['ResidencePrior'].replace(17, 99, inplace=True)

    #A ResidencePriorLengthOfStay -- remains unchanged
    #A DateToStreetESSH --remains unchanged

    #3.917A TimesHomelessPastThreeYears 0 --> 1 
    mask = ((enrollmentfile['ProjectID'].isin(projectid1)) & (enrollmentfile['TimesHomelessPastThreeYears'] == 0)) 
    enrollmentfile.loc[mask, 'TimesHomelessPastThreeYears'] = 1 

    #A MonthsHomelessPastThreeYears remains the same

    #B Select ResidencePrior = 4, 5, 6, 7, 15, 24 (all institutions) and ResidencePriorLengthOfStay = 2, 3, 10, 11 (less than 90 days) --> Yes, LOSUnderThreshold =1 
    #Change LOSUnderThreshold to 1
    maskA = (((enrollmentfile['ResidencePrior'] > 3) | (enrollmentfile['ResidencePrior'] < 8) | (enrollmentfile['ResidencePrior'] == 15) | (enrollmentfile['ResidencePrior'] == 24)) & ((enrollmentfile['ResidencePriorLengthOfStay'] == 2 ) | (enrollmentfile['ResidencePriorLengthOfStay'] == 3 ) | (enrollmentfile['ResidencePriorLengthOfStay'] == 10 ) | (enrollmentfile['ResidencePriorLengthOfStay'] == 11 )))

    #Select ResidencePrior = 2, 3, 8, 9, 12, 13, 14, 17, 19, 20, 21, 22, 23, 25, 26, 99
    #and ResidencePriorLengthOfStay = 10, 11
    maskB = (((enrollmentfile['ResidencePrior'] == 2) | (enrollmentfile['ResidencePrior'] == 3) | (enrollmentfile['ResidencePrior'] == 8) |
            (enrollmentfile['ResidencePrior'] == 9) | (enrollmentfile['ResidencePrior'] == 12) | (enrollmentfile['ResidencePrior'] == 13) |
            (enrollmentfile['ResidencePrior'] == 14) | (enrollmentfile['ResidencePrior'] == 17) | (enrollmentfile['ResidencePrior'] == 19) |
            (enrollmentfile['ResidencePrior'] == 20) | (enrollmentfile['ResidencePrior'] == 21) | (enrollmentfile['ResidencePrior'] == 22) |
            (enrollmentfile['ResidencePrior'] == 23) | (enrollmentfile['ResidencePrior'] == 25) | (enrollmentfile['ResidencePrior'] == 26) |
            (enrollmentfile['ResidencePrior'] == 99)) & ((enrollmentfile['ResidencePriorLengthOfStay'] == 10 ) | (enrollmentfile['ResidencePriorLengthOfStay'] == 11 )))

    #LOSUnderThreshold: for 3.917B projects, input 1 where they fit the one of the two masks or otherwise 0 
    #enrollmentfile.loc[enrollmentfile['ProjectID'].isin(projectid2), 'LOSUnderThreshold'] = np.where(((maskA == True) | (maskB == True)), 1, 0)



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
    enrollmentfile.loc[enrollmentfile['ProjectID'].isin(projectid2), 'PreviousStreetESSH'] = np.where((((maskA == True) | (maskB == True) | (maskC == True)) & (maskD == True)), 0, 1)

    #Carry over date when maskE = ResidencePrior = 1, 16, 18 or maskA or maskB
    maskE = ((enrollmentfile['ResidencePrior'] == 1) | (enrollmentfile['ResidencePrior'] == 16) | (enrollmentfile['ResidencePrior'] == 18))
    
    #For 3.917B projects,  if they are not one of the carry over fields, set that field to blank.
    enrollmentfile.loc[(((maskA == False) & (maskB == False) & (maskE == False)) & enrollmentfile['ProjectID'].isin(projectid2)), 'DateToStreetESSH'] = ''

    #For 3.917B projects, maskE or maskA or maskB --> enrollment TimesHomelessPastThreeYears 0 --> 1
    enrollmentfile.loc[enrollmentfile['ProjectID'].isin(projectid2), 'TimesHomelessPastThreeYears'] = np.where(((maskA == True) | (maskB == True) | (maskE == True)), 0, 1)

    #!(maskE or maskA or maskB) --> enrollment MonthsHomelessPastThreeYears --> ''
    enrollmentfile.loc[(((maskA == False) & (maskB == False) & (maskE == False)) & enrollmentfile['ProjectID'].isin(projectid2)), 'MonthsHomelessPastThreeYears'] = ''

    #DisablingCondition in enrollment.csv -- change any blanks to 99
    enrollmentfile['DisablingCondition'].replace(np.nan, 99, inplace=True)

    #Add HouseholdID in enrollmentcoc.csv -- 
    # For enrollment.csv, create a dictionary {PersonalID: HouseholdID}

    PersonToHouse = dict()
    #row_iterator = enrollmentfile.iterrows()

    for i, row_i in enrollmentfile.iterrows():
        PersonalID = row_i['PersonalID']
        HouseholdID = row_i['HouseholdID']
        PersonToHouse[PersonalID] = HouseholdID

    #Add HP Targeting Critieria and Use of Other Crisis Criteria in enrollment.csv
    enrollmentfile['UrgentReferral'] = ''
    enrollmentfile['TimeToHousingLoss'] = ''
    enrollmentfile['ZeroIncome'] ='' 
    enrollmentfile['AnnualPercentAMI'] = ''
    enrollmentfile['FinancialChange'] = '' 
    enrollmentfile['HouseholdChange'] = ''
    enrollmentfile['EvictionHistory'] = ''
    enrollmentfile['SubsidyAtRisk'] = ''
    enrollmentfile['LiteralHomelessHistory'] = ''
    enrollmentfile['DisabledHoH'] = ''
    enrollmentfile['CriminalRecord'] = ''
    enrollmentfile['SexOffender'] = ''
    enrollmentfile['DependentUnder6'] = '' 
    enrollmentfile['SingleParent'] = ''
    enrollmentfile['HH5Plus'] = ''  
    enrollmentfile['IraqAfghanistan'] = ''
    enrollmentfile['FemVet'] = ''
    enrollmentfile['ThresholdScore'] = ''
    enrollmentfile['ERVisits'] = ''
    enrollmentfile['JailNights'] = ''
    enrollmentfile['HospitalNights'] = ''

    # Input the values based on the personalid as key in enrollmentcoc.csv
    enrollmentcocfile = export[6]
    enrollmentcocfile['HouseholdID'] = enrollmentcocfile['PersonalID']
    enrollmentcocfile['HouseholdID'].replace(PersonToHouse, inplace=True)
    enrollmentcocfile = enrollmentcocfile[['EnrollmentCoCID', 'ProjectEntryID', 'HouseholdID', 'ProjectID', 'PersonalID', 'InformationDate', 'CoCCode', 'DataCollectionStage',
                    'DateCreated', 'DateUpdated', 'UserID', 'DateDeleted', 'ExportID']]

    #delete the abrogated columns in enrollment.csv
    del enrollmentfile['OtherResidencePrior']
    del enrollmentfile['EntryFromStreetESSH']
    del enrollmentfile['InPermanentHousing']

    #change the order of columns in enrollment.csv
    enrollmentfile = enrollmentfile[['ProjectEntryID', 'PersonalID', 'ProjectID', 'EntryDate', 'HouseholdID', 'RelationshipToHoH',
                    'ResidencePrior', 'ResidencePriorLengthOfStay', 'LOSUnderThreshold', 'PreviousStreetESSH', 'DateToStreetESSH',
                    'TimesHomelessPastThreeYears', 'MonthsHomelessPastThreeYears', 'DisablingCondition',
                    'HousingStatus', 'DateOfEngagement', 'ResidentialMoveInDate', 'DateOfPATHStatus',
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
                    'UrgentReferral', 'TimeToHousingLoss', 'ZeroIncome', 'AnnualPercentAMI', 'FinancialChange', 'EvictionHistory',
                    'SubsidyAtRisk', 'LiteralHomelessHistory', 'DisabledHoH', 'CriminalRecord', 'SexOffender', 'DependentUnder6',
                    'SingleParent', 'HH5Plus', 'IraqAfghanistan', 'FemVet', 'HPScreeningScore', 'ThresholdScore',
                    'VAMCStation', 'ERVisits', 'JailNights', 'HospitalNights', 'DateCreated', 'DateUpdated', 'UserID', 'DateDeleted', 'ExportID']]

    #Additional changes in other files
    #Add SourceType in export.csv and change all values to 4 
    exportfile = export[0]
    exportfile['SourceType'] = 4
    exportfile = exportfile[['ExportID', 'SourceType', 'SourceID', 'SourceName', 'SourceContactFirst', 'SourceContactLast',
                'SourceContactPhone', 'SourceContactExtension', 'SourceContactEmail', 'ExportDate',
                'ExportStartDate', 'ExportEndDate', 'SoftwareName', 'SoftwareVersion', 'ExportPeriodType',
                'ExportDirective', 'HashStatus']]


    #Add IndianHealthServices and NoIndianHealthServicesReason in IncomeBenefits.csv
    incomebenefitsfile = export[8]
    incomebenefitsfile['IndianHealthServices'] = ''
    incomebenefitsfile['NoIndianHealthServicesReason'] = ''
    incomebenefitsfile = incomebenefitsfile[['IncomeBenefitsID', 'ProjectEntryID', 'PersonalID', 'InformationDate', 'IncomeFromAnySource', 'TotalMonthlyIncome', 'Earned',
                    'EarnedAmount', 'Unemployment', 'UnemploymentAmount', 'SSI', 'SSIAmount', 'SSDI', 'SSDIAmount', 'VADisabilityService',
                    'VADisabilityServiceAmount', 'VADisabilityNonService', 'VADisabilityNonServiceAmount', 'PrivateDisability', 'PrivateDisabilityAmount',
                    'WorkersComp', 'WorkersCompAmount', 'TANF', 'TANFAmount', 'GA', 'GAAmount', 'SocSecRetirement', 'SocSecRetirementAmount', 'Pension', 'PensionAmount',
                    'ChildSupport', 'ChildSupportAmount', 'Alimony', 'AlimonyAmount', 'OtherIncomeSource', 'OtherIncomeAmount', 'OtherIncomeSourceIdentify', 'BenefitsFromAnySource',
                    'SNAP', 'WIC', 'TANFChildCare', 'TANFTransportation', 'OtherTANF', 'RentalAssistanceOngoing', 'RentalAssistanceTemp', 'OtherBenefitsSource', 'OtherBenefitsSourceIdentify',
                    'InsuranceFromAnySource', 'Medicaid', 'NoMedicaidReason', 'Medicare', 'NoMedicareReason', 'SCHIP', 'NoSCHIPReason', 'VAMedicalServices',
                    'NoVAMedReason', 'EmployerProvided', 'NoEmployerProvidedReason', 'COBRA', 'NoCOBRAReason', 'PrivatePay', 'NoPrivatePayReason', 'StateHealthIns',
                    'NoStateHealthInsReason', 'IndianHealthServices', 'NoIndianHealthServicesReason', 'HIVAIDSAssistance', 'NoHIVAIDSAssistanceReason', 'ADAP', 'NoADAPReason', 'DataCollectionStage', 'DateCreated', 'DateUpdated',
                    'UserID', 'DateDeleted', 'ExportID']]

    # save export.csv, enrollment.csv, enrollmentcoc.csv, incomebenefits.csv as csv
    newpath = filedir + 'newzip'
    if not os.path.exists(newpath):
        os.makedirs (filedir + 'newzip')
    exportfile.to_csv(filedir + 'newzip/Export.csv', sep=',', header=True)
    enrollmentfile.to_csv(filedir + 'newzip/Enrollment.csv', sep=',', header=True)
    enrollmentcocfile.to_csv(filedir + 'newzip/EnrollmentCoC.csv', sep=',', header=True)
    incomebenefitsfile.to_csv(filedir + 'newzip/IncomeBenefits.csv', sep=',', header=True)

    export[1].to_csv(filedir + 'newzip/Project.csv', sep=',', header=True)
    export[2].to_csv(filedir + 'newzip/ProjectCoC.csv', sep=',', header=True)
    export[3].to_csv(filedir + 'newzip/Funder.csv', sep=',', header=True)
    export[4].to_csv(filedir + 'newzip/Client.csv', sep=',', header=True)
    export[7].to_csv(filedir + 'newzip/Exit.csv', sep=',', header=True)
    export[9].to_csv(filedir + 'newzip/Disabilities.csv', sep=',', header=True)
    export[10].to_csv(filedir + 'newzip/HealthAndDV.csv', sep=',', header=True)
    export[11].to_csv(filedir + 'newzip/EmploymentEducation.csv', sep=',', header=True)
    export[12].to_csv(filedir + 'newzip/Services.csv', sep=',', header=True)

    # zip all into 
    # 0: export
    # 1: project
    # 2: projectcoc
    # 3: funder
    # 4: client
    # 5: enrollment
    # 6: enrollmentcoc
    # 7: exit
    # 8: incomebenefits
    # 9: disabilities
    # 10: healthanddv
    # 11: employmenteducation

    # 12: services

    with zipfile.ZipFile(filedir + 'Exportto50.zip', 'w') as myzip:
        myzip.write(filedir + 'newzip/Export.csv')
        myzip.write(filedir + 'newzip/Project.csv')
        myzip.write(filedir + 'newzip/ProjectCoC.csv')
        myzip.write(filedir + 'newzip/Funder.csv')
        myzip.write(filedir + 'newzip/Client.csv')
        myzip.write(filedir + 'newzip/Enrollment.csv')
        myzip.write(filedir + 'newzip/EnrollmentCoC.csv')
        myzip.write(filedir + 'newzip/Exit.csv')
        myzip.write(filedir + 'newzip/IncomeBenefits.csv')
        myzip.write(filedir + 'newzip/Disabilities.csv')
        myzip.write(filedir + 'newzip/HealthAndDV.csv')
        myzip.write(filedir + 'newzip/EmploymentEducation.csv')
        myzip.write(filedir + 'newzip/Services.csv')


    return HttpResponse('<html><body><h1>Congratulations! It has been done. </h1></body></html>')