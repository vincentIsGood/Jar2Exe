# Jar2Exe
Pack jar to an exe OR linux compatible executable using wrap-packer.

Command line arguments are currently not supported.

## Usage
However, you can do a quick configuration in the script
```py
## Real configuration
targetJarFile = "example.jar"

### if JAVA_HOME is not None, this path is used instead
### JAVA_HOME_NAME is adviced to be the name of JAVA_HOME directory (eg. "jdk-17/")
JAVA_HOME = None
JAVA_HOME_NAME = None

### if outputArch is not None, this value is used instead
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