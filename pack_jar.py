import subprocess
import os
import shutil
import sys

## Start configuration
targetJarFile = "example.jar"

## The following options are adviced NOT to touch them.
### if JAVA_HOME is not None, this path is used instead
### default: comes from environment variable JAVA_HOME
JAVA_HOME = None

### JAVA_HOME_NAME is adviced to be the name of JAVA_HOME directory
### eg. "jdk-17/"
JAVA_HOME_NAME = None

### if outputArch is not None, this value is used instead
### Caution: This should match the platform of the configured JAVA_HOME
###          (ie. a "linux-x64" binary cannot run jdk for windows)
### Possible values = ["windows-x64", "macos-x64", "linux-x64"]
outputArch = None

## End configuration
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

if not os.path.exists(targetJarFile):
    raise ValueError("[-] Cannot find target jar file: '%s'" % targetJarFile)

### Functions
def findJavaHome():
    global JAVA_HOME, JAVA_HOME_NAME
    if JAVA_HOME != None and JAVA_HOME_NAME != None:
        if not os.path.isdir(JAVA_HOME):
            raise ValueError("[-] JAVA_HOME does not exist OR is not a directoy: '%s'" % JAVA_HOME)
        return

    JAVA_HOME = os.getenv("JAVA_HOME")
    if not os.path.isdir(JAVA_HOME):
        raise ValueError("[-] Env variable JAVA_HOME does not exist OR is not a directoy: '%s'" % JAVA_HOME)
    JAVA_HOME = os.path.normpath(JAVA_HOME)
    JAVA_HOME_NAME = JAVA_HOME[JAVA_HOME.rindex(os.sep)+1:]

def chmod(file):
    if SYS_PLATFORM != "win32":
        os.chmod(file, 0o750)

def executablePath(file):
    if SYS_PLATFORM != "win32":
        return "./" + file
    return file

def createRunnerScript():
    runnerScriptFile = "%s%s" % (bundleDir, runnerScriptFilename)
    runnerScriptTextWin = f"""@echo off
set JAVA_HOME={os.path.normpath(bundleDir + JAVA_HOME_NAME)}

%JAVA_HOME%\\bin\\java -jar {targetJarFile} %*
    """
    runnerScriptTextUnix = f"""#!/bin/sh
JAVA_HOME={os.path.normpath(bundleDir + JAVA_HOME_NAME)}

$JAVA_HOME/bin/java -jar {targetJarFile} $@
    """

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
    findJavaHome()

    global bundleDir
    bundleDir = os.path.normpath(bundleDir) + "/"

    runtimeDir = bundleDir + JAVA_HOME_NAME

    os.makedirs(runtimeDir, exist_ok=True)

    print("[+] Copying jre/jdk from '%s' to '%s'" % (JAVA_HOME, runtimeDir))
    shutil.copytree(JAVA_HOME, runtimeDir, dirs_exist_ok=True, ignore_dangling_symlinks=True)

    print("[+] Copying '%s' to '%s'" % (targetJarFile, bundleDir))
    shutil.copy(targetJarFile, bundleDir)

    createRunnerScript()

    cmd = [executablePath(getWarpPacker()), "--arch", outputArch, "--input_dir", bundleDir, "--exec", runnerScriptFilename, "--output", outputBin]
    print("[+] Running warp packer to create the final binary '%s'" % outputBin)
    print(" ".join(cmd))
    subprocess.run(cmd)

    print("[*] Note: All decompressed files will be cached on execution")
    print("[*] For more info about wrap, https://github.com/dgiagio/warp")

main()