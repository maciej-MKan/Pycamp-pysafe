# Pycamp-pysafe
Project from PyCamp module 

## General info
Console program that protects files against unauthorized access.<br />
It enables: <br />
* encryption of individual files or entire folders
* decryption of previously secured files
* editing encrypted files in the default program
* * in the future, automatic encryption of files thrown into a specific folder

## Technologies
The program was created in Python 3.8 using libraries cryptography and argparse (and wathdog, multiprocessing in the future features).

## Using

### Help
To view help enter:
```
$ python PySafe.py --help
```

### Run
```
PySafe [-h] [-d [option: start / stop]] (-e file | -en [file or dir [file or dir ...]] | -de [file or dir [file or dir ...]]) [Password]

positional arguments:
  Password                          Your Pysafe password.
                                    Recommended not entered on the command line.
                                    Leave blank, and then the program will ask you about it in safe mode.

optional arguments:
  -h, --help            show this help message and exit
  -d [option: start / stop], --daemon [option: start / stop]
                                    The process of automatically encoding files dumped into a specific folder.
                                    The option will be available as you ask nicely :)

  -e file, --edit file              Encrypted file to edit

  -en [file or dir [file or dir ...]], --encrypt [file or dir [file or dir ...]]
                                    File or directory to encrypt

  -de [file or dir [file or dir ...]], --decrypt [file or dir [file or dir ...]]
                                    File or directory to decrypt
```
