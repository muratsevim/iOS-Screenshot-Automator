#!/usr/bin/python

#	-- Set all devices you want to use for screenshots here 
#	-- (has to match one of the names returned by 'instruments -w x' command)
#	-- Possible options for iOS 7.1
#      -- iPhone - Simulator - iOS 7.1
#      -- iPhone Retina (3.5-inch) - Simulator - iOS 7.1
#      -- iPhone Retina (4-inch) - Simulator - iOS 7.1
#      -- iPhone Retina (4-inch 64-bit) - Simulator - iOS 7.1
#      -- iPad - Simulator - iOS 7.1
#      -- iPad Retina - Simulator - iOS 7.1
#      -- iPad Retina (64-bit) - Simulator - iOS 7.1

from time import strftime
import fnmatch
import os
import shutil
from subprocess import call
from subprocess import check_output
import sys

fullDeviceNames={
  "iphone": "iPhone Retina (3.5-inch) - Simulator - iOS 7.1",
  "iphone5": "iPhone Retina (4-inch) - Simulator - iOS 7.1",
  "ipad": "iPad Retina - Simulator - iOS 7.1"
}
allDevices=["iphone", "iphone5"]
allLanguages=["zh-Hans", "en", "fr", "de", "it", "ja", "ru", "es", "tr", "uk"]
iOSVersion="7.1"

def logEvent(message):
  date = strftime('%Y-%m-%d %H:%M:%S')
  line = date + " " + message
  print(line)  # >> ~/Library/Logs/AppleScript-events.log

def setupFolders():
#Clear useless instrumentscli files and copy the screenshots to the proper folder
#If you prefer other folder names, just change it here.
  removeInstrumentsTraceFiles()  
  try:
    os.makedirs("Results/Build-All")  
  except:
    pass
  shutil.rmtree("Results/Run 1", True)
  
def removeInstrumentsTraceFiles():
  files = [f for f in os.listdir(".") if f.startswith("instrumentscli")]
  for f in files:
    shutil.rmtree(f)
    
def moveResults(source, destination):
  try:
    files = os.listdir(source)
    for file in files:
      oldPath=source+"/"+file
      newPath=destination+"/"+file
      print("moving " + oldPath + " to " + newPath)
      os.rename(source+"/"+file, destination+"/"+file)
  except:
    pass
    
def expectedScreenshotFilenames(scriptPath, deviceCode, languageCode):
  scriptName = os.path.basename(scriptPath)
  scriptCode = os.path.splitext(scriptName)[0]
  filenames = []
  for i in range(1,6):
    filenames.append(scriptCode+"-"+languageCode+"-"+deviceCode+"-screen"+str(i)+".png")
  return filenames
  
def shouldGenerateScreenshots(scriptPath, deviceCode, languageCode):
  filenames = expectedScreenshotFilenames(scriptPath, deviceCode, languageCode)
  for filename in filenames:
    path = "Results/Build-All/" + filename
    if not os.path.exists(path):
      logEvent("Missing: " + path)
      return True
  return False

setupFolders()

if(len(sys.argv) < 3):
  logEvent("Usage: " + sys.argv[0] + " TestScript.js AppName")
  exit(-1)
scriptPath=sys.argv[1]
appName=sys.argv[2]
automationTemplatePath="/Applications/Xcode.app/Contents/Applications/Instruments.app/Contents/PlugIns/AutomationInstrument.bundle/Contents/Resources/Automation.tracetemplate"
home=os.path.expanduser("~")
applicationsFolder=home + "/Library/Application Support/iPhone Simulator/"+iOSVersion+"/Applications/"
appPath=None;
for root, dirnames, filenames in os.walk(applicationsFolder):
  for dirname in fnmatch.filter(dirnames, appName + ".app"):
    appPath=os.path.join(root, dirname)

if appPath != None :
  logEvent("Found the app: " + appPath)
else:
  logEvent ("Couldn't find the app you were looking for: " + appName)
  exit(-1)
  
errorLog=""
for currentDevice in allDevices:
  logEvent("Simulating on " + currentDevice)
  for currentLang in allLanguages:
    if shouldGenerateScreenshots(scriptPath, currentDevice, currentLang):
      call("./changeLanguage " + currentLang, shell=True)
      logEvent("Changed language to " + currentLang )
      fullDeviceName = fullDeviceNames[currentDevice]
      instrumentsCommand="instruments -w \""+fullDeviceName+"\" -t \""+automationTemplatePath+"\" \""+appPath+"\" -e UIASCRIPT \""+scriptPath+"\" -e UIARESULTSPATH Results"
      logEvent("Executing " + instrumentsCommand)
      currentResults=check_output(instrumentsCommand, shell=True)
      if "Fail:" in currentResults:
        errorLog+=currentResults
      logEvent("Results: " + currentResults)
      moveResults("Results/Run 1", "Results/Build-All")
      shutil.rmtree("Results/Run 1", True)
      call(["osascript", "-e", "tell application \"iPhone Simulator\" to quit"])
    else:
      logEvent("skipping " + currentLang)

  removeInstrumentsTraceFiles()
  if len(errorLog) > 0:
    print (errorLog)
    exit(-1)


