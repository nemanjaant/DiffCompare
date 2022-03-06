from Classes import Validation, Report, generateLogMessage
from zipfile import ZipFile
import os
import sys
from datetime import datetime

file_name = "input.zip"

with ZipFile(file_name, 'r') as zipped:
    timestamp = str(datetime.utcnow()).replace(":", ".").replace(" ", ".")
    directory = "temp" + timestamp
    zipped.extractall(directory)
    try:
        gold = os.listdir(directory + '/gold')
        evalu = os.listdir(directory + '/to_eval')
        text = os.listdir(directory + '/text')
    except Exception as ex:
        print(ex)
        sys.exit(1)

validation = Validation(gold, evalu, text, directory)
fileCount = validation.fileCountValidation()
outputFolder = f"output{timestamp}"
os.mkdir(outputFolder)
visuals = ["LOC", "PERS", "ORG", "ROLE", "DEMO", "WORK", "EVENT"]



try:
    if fileCount:

        extensionCheck = validation.extensionCheckValidation()

        if not extensionCheck:

            alignment = validation.checkUnaligned()

            if alignment:

                validation.createUnalignedLogFile(alignment, outputFolder)

                for name1, name2, lines in alignment:
                    aligned = validation.getAligned(name1, name2)

            else:
                aligned = validation.getAligned()

            report = Report(aligned, directory)
            report.analyze(outputFolder)
            report.getVisualData(outputFolder, visuals)

        else:
            generateLogMessage("Some files have wrong extension. Only ann, xml and txt files are allowed.")
            sys.exit(1)

    else:
        generateLogMessage("Number of files doesn't match in all folders.")
        sys.exit(1)


except ValueError as ex:

    print(ex)
