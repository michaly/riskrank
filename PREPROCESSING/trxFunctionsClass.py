#!/usr/local/anaconda/bin/python2.7
'''
Created on Nov 7, 2013

@author: nancy
'''


from datetime import datetime
from urlparse import urlparse #used to extract the URL domain
import re #used for regular expressions
import os

import linesClass
import generalMethods as  gm
#global lines; lines = linesClass.Logs.lines;
global l; l=linesClass.l;
global Label; Label=linesClass.lbl

global malwareDomains; malwareDomains = dict({})      # The value 1 is dummy, the hash defined just for efficient search
global copyrightDomains; copyrightDomains = dict({})    # The value 1 is dummy, the hash defined just for efficient search
global malRiskWeight; malRiskWeight=3; global keyRiskWeight; keyRiskWeight=2; global copyRiskWeight; copyRiskWeight=1;
'''
class Label():

    TS = 0              # UnixTimeStamp
    cId = 1             # Cluster Id - Not In Use 
    subId = 2           # ml - Not In Use
    uId = 3             # User Id
    bSesId = 4          # Browser Session Id
    IP = 5              # IP
    countryId = 6       # Country Id
    CUA = 7             # Client User Agent - consider using the splited str (OS, browser,...) 
    isFromOneWay = 8    # isFromOneWay - Not In Use
    isLink = 9          # Is Link
    httpRefer = 10      # Http Refer - Not In Use
    prevSite = 11       # Previous Site
    reqSite = 12        # Requested Site
    httpCode = 13       # HttpCode
    httpRedirectToUrl = 14   # Http Redirect To URL- if httpCode starts with 3XX the redirected URL will appear here
    domain = 15         # The requested Site's Domain
    isRisky = 16        # Risk Indicator - if malware OR copyright OR keyword
    malRisk = 17        # Indicator, 1 = include malware black list 
    copyrightRisk = 18  # Indicator, 1 = include Google removed domains (copyrights) 
    keywordRisk = 19    # Indicator, 1 = include keywords
    countryName = 20    # Country name 
    utcDate =  21       # Calculated time fields
    dayInWeek = 22      # Calculated time fields
    isWeekend = 23      # Calculated time fields
    time = 24           # Calculated time fields
    hour = 25           # Calculated time fields
    partOfDay = 26      # Calculated time fields 
    isReqSiteHttps = 27 # Indicator for https requested site  
    genSesId = 28       # Generated by generateSessionAndTimeSpent() function
    shouldProcess = 29
    timeSpent = 30      # Approximated Time Spent in a site, by the prevSite = reqSite (see function calcTimeSpent())
    hasChild = 31   '''
    

class TrxFunctions(object):
    
    
    
    def addExtractedData_domainsGraph(self):
        ''' update "lines" with extracted data '''
        global l
        for i in l.lines:
            currIdx = l.lines.index(i)
            TrxFunctions.addRiskyExtractedData(self, currIdx)
            l.lines[currIdx] += [0, 0, 0, 0, 0, 0, 0, 0] 
            
        return  
    
    def addExtractedData(self):
        ''' update "lines" with extracted data '''
        global l
        for i in l.lines:
            currIdx = l.lines.index(i)
            TrxFunctions.addRiskyExtractedData(self, currIdx)
            TrxFunctions.addConutryName(self, currIdx)
            TrxFunctions.addDateExtractedData(self, currIdx)
            TrxFunctions.isHttps(self, currIdx)
            
        return  
        
    def addRiskyExtractedData(self, index):
        
        global l
        isRisky = 0;
        domain = getDomainFromRequestedSite(l.lines[index][Label.reqSite])
        if(domain != ''):   #getDomainFromRequestedSite returns '' if failed extracting the domain
            l.lines[index] += [domain]
            (isRisky, malRisk, copyrightRisk, keywordRisk) = TrxFunctions.isRiskyURL(self, l.lines[index][Label.reqSite], l.lines[index][Label.domain])
            l.lines[index] = l.lines[index] + [ isRisky, malRisk, copyrightRisk, keywordRisk]
            #print(str(isRisky + malRisk + copyrightRisk + keywordRisk) + "\t" + str(lines[currIdx][Label.uId]))   
        else: # Couldn't parse Domain
            l.lines[index] = l.lines[index] + [ '', 0, 0, 0, 0]
        
        return 
   
    def addConutryName(self, index):
        global l
        l.lines[index] = l.lines[index] + ['None'] #TBD!
        return
    
    def addDateExtractedData(self, index):
        
        unixDate = float(l.lines[index][Label.TS])
        utcDate = TrxFunctions.getUTCDateFromUnixDateDate(self, unixDate)
        dayInWeek = TrxFunctions.getDayInWeek(self, utcDate)
        isWeekend = str(getWeekend(dayInWeek))
        hour = str(utcDate.hour)
        time = TrxFunctions.getTime(self, utcDate)
        partOfDay = TrxFunctions.getPartOfDay(self, str(time))
            
        l.lines[index] = l.lines[index] + [ str(utcDate) , dayInWeek , isWeekend ,str(time), hour, partOfDay]   
        
        return 
    
    def isHttps(self, index):
        
        l.lines[index] = l.lines[index] + [str(isRequestedSiteHttps(l.lines[index][Label.reqSite]))] 
        return 
    
    def getUTCDateFromUnixDateDate(self, unixDate):
        '''Convert a unix time to a datetime object''' 
        return datetime.fromtimestamp(unixDate)

    def getDayInWeek(self, date):
        '''Monday is 1 and Sunday is 7'''
        dayInt = datetime.isoweekday(date)
        if  (dayInt == 1): return 'Monday'
        if  (dayInt == 2): return 'Tuesday'
        if  (dayInt == 3): return 'Wednesday'
        if  (dayInt == 4): return 'Thursday'
        if  (dayInt == 5): return 'Friday'
        if  (dayInt == 6): return 'Saturday'
        else : return 'Sunday'
    
    def getTime(self, date):
        ''' Return full Time as string'''
        return datetime.time(date)
    
    def getPartOfDay(self, time):
        ''' Returns Part of the Day as string'''
        if (time >= '05:00:00.000000' and time <= '11:00:00.000000') : return 'Morning'
        if (time >= '12:00:00.000000' and time <= '16:00:00.000000') : return 'Noon'
        if (time >= '17:00:00.000000' and time <= '21:00:00.000000') : return 'Evening'
        else: return 'Night'
        
    def containKeyword(self, url):
        risky = re.compile('Torrent|Crack|[^s]Hack|Keygen|1337x|Bitsnoop|Ailbreak|Spyware|Pirate|Astalavista|Demonoid|Phrozencrew|Underground|Warez|Btjunkie|H33t', re.IGNORECASE).search(url)
        if (risky is not None): 
            return 1    # True: if the URL contains at least one of the risky keywords return isRisky = 1 , riskLevel = 1
        else: return 0
        
    def searchKeyInHash(self, type, key):       
        if (type == 'malware'):
            global malwareDomains
            if (key in malwareDomains): 
                return 1    #if the domain known as containing malware return isRisky=1
                   
        elif (type == 'copyright'):
            global copyrightDomains
            if (key in copyrightDomains): 
                return 1    #if the domain known as containing malware return isRisky=1
            
        return 0
        
    def isRiskyURL(self ,url,domain):   
        '''
        Risk indicator by substrings contained in the Requested Site 
        
        Makes the problem Supervised Learning
        
        '''
        isRisky = 0
        risk_level = {'Mal':0,'Copyright':0,'Keyword':0}
        
        if (TrxFunctions.searchKeyInHash(self,'malware', domain)):     
            isRisky = 1
            risk_level['Mal'] = 1
        if (TrxFunctions.searchKeyInHash(self, 'copyright', domain)): 
            isRisky = 1
            risk_level['Copyright'] = 1
        if (TrxFunctions.containKeyword(self, url)): 
            isRisky = 1
            risk_level['Keyword'] = 1

        return (isRisky,risk_level['Mal'],risk_level['Copyright'],risk_level['Keyword'])
    
    def createMalDomainsHash(self, malDomainsFile):
        global malwareDomains
        with open(malDomainsFile,"r") as myFile:      
            for line in myFile:
                domain = getDomainFromRequestedSite(line.rstrip())
                if(domain):     #we do not want to get a None key!!!
                    if (domain not in malwareDomains): malwareDomains[domain] = 1
        malwareDomains = writeHashToFile(malwareDomains,'/home/michal/Desktop/MalDomainsLast')
        return None
    
    def createCopyrightDomainHash(self, file):            #TBD - CHECK!!!!!
        global copyrightDomains
        with open(file,"r") as myFile:      
            for line in myFile:
                domain = getDomainFromRequestedSite(line.rstrip())
                if(domain):     #we do not want to get a None key!!!
                    if (domain not in copyrightDomains): copyrightDomains[domain] = 1
        
        # this is for future runs- we will be able to read the list from a file:
        copyrightDomains = writeHashToFile(copyrightDomains,'/home/michal/Desktop/copyDomainsLast')
        return None

def createRiskHashes(malSource,googleSource,ignore_domain_list=[]):
    # ignore_domain_list is a list of domains which will be ignored 
    # (won't appear as malware/copyright domains) for evaluation flow
    global malwareDomains; global copyrightDomains
    clear_risk_hashes() #clear malwareDomains copyrightDomains dicts (might be full from optional prev run)
    malware_file_path='/home/michal/malware_dict.csv'
    copyright_file_path='/home/michal/copyright_dict.csv'
    if os.path.exists(malware_file_path):
        malwareDomains=gm.readDict(malware_file_path)
        copyrightDomains=gm.readDict(copyright_file_path)
    else:   # First time- the files don't exist
        createDomainsHashFromFile('malwareDomains',malSource)
        #DEBUG: writeHashToFile('malwareDomains','/home/michal/Desktop/malwareDomainsForTest')
        gm.saveDict(malware_file_path, malwareDomains)
        createDomainsHashFromFile('copyrightDomains',googleSource)
        #DEBUG: writeHashToFile('copyrightDomains','/home/michal/Desktop/copyrightDomainsForTest')
        gm.saveDict(copyright_file_path, copyrightDomains)
        
    if ignore_domain_list:  #for evaluation cases- this won't be None
        for d in ignore_domain_list:    
            if d in malwareDomains:
                malwareDomains.pop(d)
            if d in copyrightDomains:
                copyrightDomains.pop(d)
    return

def createHashFirstTime(hashName,sourceFile):
    hashNameStr = hashName
    if (hashName == 'malwareDomains'):
        hashName = malwareDomains 
    else:
        hashName = copyrightDomains
    with open(sourceFile,"r") as sFile:      
            for line in sFile:
                domain = getDomainFromRequestedSite(line.rstrip())
                if(domain):     #we do not want to get a None key!!!
                    if (domain not in hashName): hashName[domain] = 1
        
    # this is for future runs- we will be able to read the list from a file:
    writeHashToFile(hashName,'/home/michal/Desktop/' + hashNameStr)
    return None

def createDomainsHashFromFile(hashName,sourceFile):
    #NOTE: sourceFile must be a file contains ONLY ONE DOMAIN (NOT URL) in each line with NO DUPLICATES!!!
    if (hashName == 'malwareDomains'):
        global malwareDomains
        hashName = malwareDomains 
    else:
        global copyrightDomains
        hashName = copyrightDomains
    with open(sourceFile,"r") as sFile:      
            for line in sFile:
                hashName[line.rstrip()] = 1
    return None

def writeHashToFile(hashName,fileName):
    os.path.exists(fileName) and os.remove(fileName)
    target = open(fileName, 'a')
   
    for i in hashName: 
        target.write(i)
        target.write("\n")
    
    target.close()
    return 

def writeHashWithValuesToFile(hashName,fileName):
    os.path.exists(fileName) and os.remove(fileName)
    target = open(fileName, 'a')
   
    for i in hashName: 
        target.write(i)
        target.write(", ")
        target.write(str(hashName[i]))
        target.write("\n")
    
    target.close()
    return 
 

def getDomainFromRequestedSite(url): 
    
    if(url):
        if(re.compile('\[|\]').search(url) != None):   
            parsed = ''
            return parsed
        else: 
            parsed = urlparse(url)
            
            if (parsed.netloc == ''): # mostly- urls without http
                tmp = 'http://'+ str(url)
                tmpParsed = urlparse(tmp)
                parsed = tmpParsed   
                        
            return parsed.hostname
    else: return '' 
    
def isRequestedSiteHttps(url): #returns 1 if https, 0 otherwise
    if (url):
        if (re.compile('\[|\]').search(url) != None):   
            return 0
        else: 
            parsed = urlparse(url)
            if (parsed.scheme == 'https'): return '1' #True
            else: return 0 #False
    else: return 0
    
def getWeekend(dayInt):
        ''' Returns True if is weekend'''
        if (dayInt == 'Sunday' or dayInt == 'Saturday'): return '1' #True 
        else: return '0' #False
 
#--------------------------------------------------------------------------------------------------------------------------------------------------------

# The below functions are THE SAME AS TrxFunctions  but not need the fucking SELF!!!!!!!!!!!!!!!!!!!


def searchKeyInHash(type, key):
    if (type == 'malware'):
        global malwareDomains
        if (key in malwareDomains): return 1    #if the domain known as containing malware return isRisky=1
        else: return 0
    if (type == 'copyright'):
        global copyrightDomains
        if (key in copyrightDomains): return 1    #if the domain known as containing malware return isRisky=1
        else: return 0

def containKeyword(str):
    risky = re.compile('Torrent|Crack|[^s]Hack|Keygen|1337x|Bitsnoop|Ailbreak|Spyware|Pirate|Astalavista|Demonoid|Phrozencrew|Underground|Warez|Btjunkie|H33t', re.IGNORECASE).search(str)
    if (risky is not None): return 1    # True: if the URL contains at least one of the risky keywords return isRisky = 1 , riskLevel = 1
    else: return 0

#------------------------------------------------------------------------------------------------------
# CHANGED METOD!!! THE KEYWORD IS CHECKED UPON THE DOMAIN INSTEAD OF THE URL!!!!

def isRiskyDomain(domain):         #def isRiskyURL(url,domain): 
    '''
    
    Risk indicator by substrings contained in the Requested Site 
    Makes the problem Supervised Learning
    '''
    isRisky = 0
    risk_level = {'Mal':0,'Copyright':0,'Keyword':0}
    
    if (searchKeyInHash('malware', domain)):     
        isRisky = 1
        risk_level['Mal'] = 1
    if (searchKeyInHash('copyright', domain)): 
        isRisky = 1
        risk_level['Copyright'] = 1
    # we check if the domain contains keyword and not if the entire url contains it 
    #cause if the user searched the keyword in google it doesn't mean google is a risky domain  
    if (containKeyword(domain)):        #if (containKeyword(url)):    
        isRisky = 1
        risk_level['Keyword'] = 1

    return (isRisky,risk_level['Mal'],risk_level['Copyright'],risk_level['Keyword'])

#-------------------------------------------------------------------------------------------------------
#NEW METHOD!!!!

def getRiskLevel(isRisky, malRisk, copyRisk, keyRisk):   # keywordRisk is not needed here, we can evaluate its value if isRisky=1 and malRisk=0 and copyRisk=0
    riskLevel = 0   # Init as not risky
    if (isRisky):                          
        if (malRisk): riskLevel = malRiskWeight             # Malicious
        elif (keyRisk): riskLevel = keyRiskWeight           # Keyword 
        elif (copyRisk): riskLevel = copyRiskWeight         # Copyright
        else: riskLevel = 0 # For cases when isRisky=1 only cause a keyword found in the URL, but the method was called for checking the domain,which don't include the keyword (like google search)
    return riskLevel

# WRONG IMPLEMENTATION- was for cyclic dependencies:
def addExtractedData_domainsGraph():
    # update the line in "lines" with extracted data 
    global l
    for line in l.lines:
        addRiskyExtractedData(line)
        line += [0, 0, 0, 0, 0, 0, 0, 0] 
    return   
   
def addRiskyExtractedData(line):
    isRisky = 0;
    domain = getDomainFromRequestedSite(line[Label.reqSite])
    if(domain != ''):   #getDomainFromRequestedSite returns '' if failed extracting the domain
        line += [domain]
        (isRisky, malRisk, copyrightRisk, keywordRisk) = isRiskyDomain(line[Label.domain])
        line += [ isRisky, malRisk, copyrightRisk, keywordRisk]
        #print(str(isRisky + malRisk + copyrightRisk + keywordRisk) + "\t" + str(lines[currIdx][Label.uId]))   
    else: # Couldn't parse Domain
        line += [ '', 0, 0, 0, 0]
    
    return 

def addPervDomain():
    global l
    for line in l.lines:
        line.append(getDomainFromRequestedSite(line[Label.prevSite]))
    return

def addRiskRank():
    global l
    w = {'mal':1.0, 'key':0.4, 'copy':0.1}
    for line in l.lines:
        line.append(min(1, line[Label.malRisk]*w['mal']+line[Label.keywordRisk]*w['key']+line[Label.copyrightRisk]*w['copy']))
    return

def addPrevSiteRiskRank():
    global l ,w   #lines, risk weights dict
    
    for line in l.lines:
        prevDomain = line[Label.prevDomain]
        if(prevDomain != ''):   #getDomainFromRequestedSite returns '' if failed extracting the domain
            if prevDomain == line[Label.domain]:    # current and prev domains are the same
                line.append(line[Label.riskRank])
            else:   # current and prev domains are different
                (isRisky, malRisk, copyrightRisk, keywordRisk) = isRiskyDomain(prevDomain)
                line.append(min(1, malRisk*w['mal']+keywordRisk*w['key']+copyrightRisk*w['copy']))
        else: # no prev domain
            line.append(0)
    return

def add_redirect_domain_and_riskRank():
    global l, w    #lines, risk weights dict
    for line in l.lines:
        redirDomain = getDomainFromRequestedSite(line[Label.httpRedirectToUrl])
        line.append(redirDomain)    
        if redirDomain: # redirection exists (getDomainFromRequestedSite returns '' if failed extracting the domain)
            if redirDomain == line[Label.domain]:    # requested and redirect domains are the same
                line.append(line[Label.riskRank])
            else:   # requested and redirect domains are different
                (isRisky, malRisk, copyrightRisk, keywordRisk) = isRiskyDomain(redirDomain)
                line.append(min(1, malRisk*w['mal']+keywordRisk*w['key']+copyrightRisk*w['copy']))
        else: # no redirection
            line.append(0)
    return

def clear_risk_hashes():
    global malwareDomains; global copyrightDomains
    malwareDomains.clear()
    copyrightDomains.clear()
    return

def clear_lines():
    global l
    l.clear()               #clear lines

# Global risk weights dict:
w = {'mal':1.0, 'key':0.4, 'copy':0.1}

