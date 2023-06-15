# Jar2Exe
Pack jar to an exe OR linux compatible executable using wrap-packer.

Command line arguments are currently not supported.

## Usage
However, you can do a quick configuration in the script
```py
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
### default: uses the current platform
### Caution: This should match the platform of the configured JAVA_HOME
###          (ie. a "linux-x64" binary cannot run jdk for windows)
### Possible values = ["windows-x64", "macos-x64", "linux-x64"]
outputArch = None

## End configuration
```

Then, you can simply run the python script with
```sh
python pack_jar.py

OR

python3 pack_jar.py
```

## Untested Configuration
SHOULD work Scenario: You are using a Linux machine and you make `JAVA_HOME` point to a jdk for Windows. Then, you make `outputArch = "windows-x64"` and use the produced `.exe` file on a windows machine.