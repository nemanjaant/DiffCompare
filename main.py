from Classes import Validation, Report
from zipfile import ZipFile
import os
from datetime import datetime

file_name = "tt.zip"

with ZipFile(file_name, 'r') as zip:

    timestamp = str(datetime.utcnow()).replace(":","-")
    directory = "temp"+timestamp
    zip.extractall(directory)
    gold = os.listdir(directory + '/gold')
    eval = os.listdir(directory + '/to_eval')
    text = os.listdir(directory + '/text')

validation = Validation(gold, eval, text, directory)
fileCount = validation.fileCountValidation()

if fileCount:

    extensionCheck = validation.extensionCheckValidation()

    if not extensionCheck:

        alignment = validation.checkUnaligned()
        aligned = []
        if alignment:
            validation.createLogFile(alignment)
            for name1, name2, lines in alignment:
                aligned = validation.getAligned(name1, name2)
        else:
            aligned = validation.getAligned()

        report = Report(aligned, directory)
        report.analyze()


    else:
        print("Pogresne ekstenzije")
else:
    print("broj fajlova se ne poklapa")

























