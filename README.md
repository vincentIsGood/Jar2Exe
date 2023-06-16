# Jar2Exe
Pack jar to an exe OR linux compatible executable using wrap-packer.

## Basic Usage (examplejar demo)
```sh
[!] Usage: python3 pack_jar.py <target.jar> [<copy_directory>]
[*] copy_directory: A directory to be included into the final exe
[*]                 (note: the files can only be easily accessed by runner script)
[*]                 (see function `createRunnerScript` to modify the script)
```

```sh
python3 pack_jar.py examplejar/example.jar
```

You then can run the produced binary (`example.exe` on Windows or `example`) 
just like a normal command line util.
```sh
./example --help
```

### Relative paths
If the application uses relative path to access files, the root folder is where you
executed `./example`: 
```sh
# in "/home/test/example" execute this
./example

# gives output
Current root dir: /home/test/example
Seems like you found a way to run this. Congrats.
Exception in thread "main" java.nio.file.NoSuchFileException: ./data/test.txt
```

To resolve the `./data/test.txt` exception, put `data/` in the current directory like:
```sh
/home/test/example
├── data
│   └── test.txt
└── example
```

Then execute `./example`.

## Remain untested
`CTRL + C` handling is not tested.

## Untested Feature
You can also do an advanced configuration in the script (not recommended)
```py
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
```

SHOULD work Scenario: You are using a Linux machine and you make `JAVA_HOME` point to a jdk for Windows. Then, you make `outputArch = "windows-x64"` and use the produced `.exe` file on a windows machine.