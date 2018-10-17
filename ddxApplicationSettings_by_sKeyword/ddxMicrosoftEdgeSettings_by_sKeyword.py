import os;
from dxConfig import dxConfig;
from fsFirstExistingFile import fsFirstExistingFile;
from mColors import *;
from mWindowsAPI import fauProcessesIdsForExecutableNames, fbTerminateProcessForId, oSystemInfo;
from oConsole import oConsole;
import mFileSystem;

sLocalAppData = os.getenv("LocalAppData");

dxConfigSettings = {
  "bApplicationTerminatesWithMainProcess": True,
  "cBugId.bIgnoreCPPExceptions": True,
  "cBugId.bIgnoreWinRTExceptions": True,
};

sEdgeRecoveryPath = mFileSystem.fsPath(os.getenv("LocalAppData"), \
    "Packages", "Microsoft.MicrosoftEdge_8wekyb3d8bbwe", "AC", "MicrosoftEdge", "User", "Default", "Recovery", "Active");

def fEdgeSetup(bFirstRun):
  if bFirstRun:
    if oSystemInfo.uOSBuild < 15063:
      oConsole.fPrint(ERROR, "Debugging Microsoft Edge directly using BugId is only supported on Windows");
      oConsole.fPrint(ERROR, "builds ", ERROR_INFO, "15063", ERROR, " and higher, and you are running build ", \
          ERROR_INFO, oSystemInfo.sOSBuild, ERROR, ".");
      oConsole.fPrint();
      oConsole.fPrint("You could try using the ", INFO, "EdgeBugId.cmd", NORMAL, " script that comes with EdgeDbg,");
      oConsole.fPrint("which you can download from ", INFO, "https://github.com/SkyLined/EdgeDbg", NORMAL, ".");
      oConsole.fPrint("It can be used to debug Edge in BugId on Windows versions before 10.0.15063.");
      os._exit(4);
  # RuntimeBroker.exe can apparently hang with dbgsrv.exe attached, preventing Edge from opening new pages. Killing
  # all processes running either exe appears to resolve this issue.
  fKillRuntimeBrokerAndDbgSrv();
  # Prevent keeping state between different runs of the application.
  fDeleteRecovery();

def fEdgeCleanup():
  fDeleteRecovery();

def fKillRuntimeBrokerAndDbgSrv():
  for uProcessId in fauProcessesIdsForExecutableNames(["dbgsrv.exe", "RuntimeBroker.exe"]):
    fbTerminateProcessForId(uProcessId);

def fDeleteRecovery():
  # Delete the recovery path to clean up after the application ran.
  if not mFileSystem.fbIsFolder(sEdgeRecoveryPath):
    return;
  if mFileSystem.fbDeleteChildrenFromFolder(sEdgeRecoveryPath, fbRetryOnFailure = False):
    return;
  # Microsoft Edge will have a lock on these files if its running; terminate it.
  oConsole.fPrint(WARNING, "Microsoft Edge appears to be running becasuse the recovery files cannot be");
  oConsole.fPrint(WARNING, "deleted. All running Microsoft Edge processes will now be terminated to try");
  oConsole.fPrint(WARNING, "to fix this...");
  # Microsoft Edge may attempt to restart killed processes, so we do this in a loop until there are no more processes
  # running.
  while 1:
    auProcessIds = fauProcessesIdsForExecutableNames(["MicrosoftEdge.exe", "MicrosoftEdgeCP.exe"])
    if not auProcessIds:
      break;
    for uProcessId in auProcessIds:
      fbTerminateProcessForId(uProcessId);
  if mFileSystem.fbDeleteChildrenFromFolder(sEdgeRecoveryPath, fbRetryOnFailure = False):
    return;
  oConsole.fPrint(ERROR, "The recovery files still cannot be deleted. Please manually terminated all");
  oConsole.fPrint(ERROR, "processes related to Microsoft Edge and try again.");
  os._exit(4);

def fasGetEdgeOptionalArguments(bForHelp = False):
  return bForHelp and ["<dxConfig.sDefaultBrowserTestURL>"] or [dxConfig["sDefaultBrowserTestURL"]];


ddxMicrosoftEdgeSettings_by_sKeyword = {
  "edge": {
    "dxUWPApplication": {
      "sPackageName": "Microsoft.MicrosoftEdge",
      "sId": "MicrosoftEdge",
    },
    "asApplicationAttachToProcessesForExecutableNames": ["browser_broker.exe"],
    "fasGetOptionalArguments": fasGetEdgeOptionalArguments,
    "fSetup": fEdgeSetup,
    "fCleanup": fEdgeCleanup,
    "dxConfigSettings": dxConfigSettings,
  },
};