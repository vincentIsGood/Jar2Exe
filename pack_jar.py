#!/usr/local/bin python3
import subprocess
import os
import shutil
import sys

## Start configuration

## The following options are adviced NOT to touch them.
### if JAVA_HOME is not None, this path is used instead
### default: comes from environment variable JAVA_HOME
JAVA_HOME = None
JAVA_HOME_NAME = None # auto

### if outputArch is not None, this value is used instead
### default: uses the current platform
### Caution: This should match the platform of the configured JAVA_HOME
###          (ie. a "linux-x64" binary cannot run jdk for windows)
### Possible values = ["windows-x64", "macos-x64", "linux-x64"]
outputArch = None

## End configuration

targetJarFile = None
copyWholeDir = ""
if len(sys.argv) > 1:
    targetJarFile = sys.argv[1]
else:
    print("[!] Usage: python3 %s <target.jar> [<copy_directory>]" % sys.argv[0])
    print("[*] copy_directory: A directory to be included into the final exe")
    print("[*]                 (note: the files can only be easily accessed by runner script)")
    print("[*]                 (see function `createRunnerScript` to modify the script)")
    sys.exit(0)

if len(sys.argv) > 2:
    copyWholeDir = sys.argv[2]

SYS_PLATFORM = sys.platform
bundleDir = "./bundle"

if outputArch == None:
    if SYS_PLATFORM == "win32":
        outputArch = "windows-x64"
    elif SYS_PLATFORM == "darwin":
        outputArch = "macos-x64"
    else:
        outputArch = "linux-x64"
binExt    = ".exe" if outputArch == "windows-x64" else ""
scriptExt = ".bat" if outputArch == "windows-x64" else ".sh"

outputBin = targetJarFile[:targetJarFile.rindex(".")] + binExt
runnerScriptFilename = "run" + scriptExt

### Functions
def findJavaHome():
    global JAVA_HOME, JAVA_HOME_NAME
    if JAVA_HOME != None and JAVA_HOME_NAME != None:
        if not os.path.isdir(JAVA_HOME):
            raise ValueError("[-] JAVA_HOME does not exist OR is not a directoy: '%s'" % JAVA_HOME)
        JAVA_HOME_NAME = extractSingleFileName(JAVA_HOME)
        return

    JAVA_HOME = os.getenv("JAVA_HOME")
    if not os.path.isdir(JAVA_HOME):
        raise ValueError("[-] Env variable JAVA_HOME does not exist OR is not a directoy: '%s'" % JAVA_HOME)
    JAVA_HOME = os.path.normpath(JAVA_HOME)
    JAVA_HOME_NAME = extractSingleFileName(JAVA_HOME)

def assertExist(file):
    if file != "" and not os.path.exists(file):
        raise ValueError("[-] Cannot find file: '%s'" % file)

def chmod(file):
    if SYS_PLATFORM != "win32":
        os.chmod(file, 0o750)

def executablePath(file):
    if SYS_PLATFORM != "win32":
        return "./" + file # local file
    return file

def extractSingleFileName(file):
    file = os.path.normpath(file)
    if os.sep in file:
        file = file[file.rindex(os.sep)+1:]
    return file

def extractFirstLevelFileName(file):
    file = os.path.normpath(file)
    if os.sep in file:
        file = file[:file.index(os.sep)]
    return file

def safeMakeDir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)

def safeRmDir(dir):
    if os.path.exists(dir):
        os.rmdir(dir)

def copyDir(srcDir, dstDir, firstLevelExcludeDir = ""):
    if firstLevelExcludeDir:
        firstLevelExcludeDir = extractFirstLevelFileName(os.path.normpath(firstLevelExcludeDir))
    newDstDir = os.path.join(dstDir, extractSingleFileName(srcDir))
    safeMakeDir(dstDir)
    safeMakeDir(newDstDir)
    for file in os.listdir(srcDir):
        pureFileName = file
        if firstLevelExcludeDir == pureFileName:
            continue
        
        file = os.path.join(srcDir, file)
        if os.path.isdir(file):
            copyDir(file, newDstDir)
        else:
            dstFile = os.path.join(newDstDir, pureFileName)
            try:
                shutil.copy2(file, dstFile)
                shutil.copystat(file, dstFile)
            except PermissionError:
                print("[-] Cannot copy '%s' to '%s', ignoring it" % (file, dstFile))

def createRunnerScript():
    runnerScriptFile = "%s%s" % (bundleDir, runnerScriptFilename)

    ## Deprecated (Do not use cd)
    # path/to/target.jar -> {cdDir}/{targetJarFilename}
    # cdDir             = path/to
    # targetJarFilename = target.jar
    # cdDir = os.path.dirname(targetJarFile)
    # targetJarFilename = extractSingleFileName(targetJarFile)

    runnerScriptTextWin = f"""@echo off
set SCRIPT_DIR=%~dp0
set JAVA_HOME=%SCRIPT_DIR%\\{os.path.normpath(JAVA_HOME_NAME)}

%JAVA_HOME%\\bin\\java -jar %SCRIPT_DIR%\\{targetJarFile} %*"""
    
    runnerScriptTextUnix = f"""#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- \"$( dirname -- \"${{BASH_SOURCE[0]}}\" )\" &> /dev/null && pwd )
JAVA_HOME=${{SCRIPT_DIR}}/{os.path.normpath(JAVA_HOME_NAME)}

$JAVA_HOME/bin/java -jar ${{SCRIPT_DIR}}/{targetJarFile} $@"""

    runnerScriptText = runnerScriptTextWin if outputArch == "windows-x64" else runnerScriptTextUnix

    print("[+] Creating runner script at '%s'" % (runnerScriptFile))
    with open(runnerScriptFile, "w+") as file:
        file.write(runnerScriptText)
    
    chmod(runnerScriptFile)

def getWarpPacker():
    import urllib.request
    linPacker = "https://github.com/dgiagio/warp/releases/download/v0.3.0/linux-x64.warp-packer"
    macosPacker = "https://github.com/dgiagio/warp/releases/download/v0.3.0/macos-x64.warp-packer"
    winPacker = "https://github.com/dgiagio/warp/releases/download/v0.3.0/windows-x64.warp-packer.exe"
    
    warpPackerUrl = None
    if SYS_PLATFORM == "win32":
        warpPackerUrl = winPacker
    elif SYS_PLATFORM == "darwin":
        warpPackerUrl = macosPacker
    else:
        warpPackerUrl = linPacker
    
    warpPackerFile = warpPackerUrl[warpPackerUrl.rindex("/")+1:]
    if not os.path.exists(warpPackerFile):
        try:
            print("[*] Cannot find warp-packer locally, downloading it from '%s'" % warpPackerUrl)
            with urllib.request.urlopen(warpPackerUrl) as req, open(warpPackerFile, "wb") as file:
                file.write(req.read())
            print("[+] Successfully downloaded '%s'" % warpPackerFile)
            chmod(warpPackerFile)
        except Exception as e:
            raise Exception("[-] Cannot download warp-packer from '%s'" % warpPackerUrl)
    else:
        print("[+] warp-packer found: '%s'" % warpPackerFile)
    
    return warpPackerFile

def main():
    global bundleDir, copyWholeDir

    assertExist(targetJarFile)
    assertExist(copyWholeDir)
    findJavaHome()

    bundleDir = os.path.normpath(bundleDir) + "/"

    print("[+] Copying jre or jdk from '%s' to '%s'" % (JAVA_HOME, bundleDir))
    copyDir(JAVA_HOME, bundleDir, bundleDir)

    if copyWholeDir.strip() != "":
        print("[+] Copying directory '%s' to '%s'" % (copyWholeDir, bundleDir))
        copyDir(copyWholeDir, bundleDir, bundleDir)

    print("[+] Copying '%s' to '%s'" % (targetJarFile, bundleDir))
    shutil.copy(targetJarFile, bundleDir)

    createRunnerScript()

    cmd = [executablePath(getWarpPacker()), "--arch", outputArch, "--input_dir", bundleDir, "--exec", runnerScriptFilename, "--output", outputBin]
    print("[+] Running warp packer to create the final binary '%s'" % outputBin)
    print(" ".join(cmd))
    subprocess.run(cmd)

    print("[*] Note: All decompressed files will be cached on execution")
    print("[*] Cache Location:")
    print("[*]   - Linux: $HOME/.local/share/warp/packages")
    print("[*]   - macOS: $HOME/Library/Application Support/warp/packges")
    print("[*]   - Windows: %LOCALAPPDATA%\\warp\\packages")
    print("[*] For more info about wrap, https://github.com/dgiagio/warp")

main()