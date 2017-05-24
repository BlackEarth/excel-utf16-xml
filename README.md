# excel-utf16-xml
Convert Excel UTF-16 (tab-separated) text to XML.

## Installation
* Download this package. 
* Make sure you have python3 installed.
* From the command line run:
```bash
    $ cd /path/to/excel-utf16-xml
    $ ./install
```

## Usage
* Make sure the file was saved from Excel as "UTF-16 Unicode Text (.txt)".

* from the command line, run either:
    ```bash
    $ bin/csv_to_xml /full/path/to/utf-16/txt
    ```
    or
    ```bash
    $ bin/csv_to_aid /full/path/to/utf-16/txt
    ```
    The "aid" version of the script does a couple of extra things to prepare the file for InDesign.

* You can also add the "bin" folder to your system path so that you can run the scripts without reference to their location (without the "bin/" prefix).