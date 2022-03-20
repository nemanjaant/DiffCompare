# importing the required libraries
import os
import shutil
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from Classes import Validation, Report, generateLogMessage
from zipfile import ZipFile
from datetime import datetime


app = Flask(__name__)

upload_folder = "uploads/"
if not os.path.exists(upload_folder):
    os.mkdir(upload_folder)

app.config['UPLOAD_FOLDER'] = upload_folder
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024


@app.route('/')
def startApp():
    return render_template('upload.html')


@app.route('/compareNER', methods=['GET', 'POST'])
def uploadfile():
    if request.method == 'POST':
        f = request.files['file']  # get the file from the files object
        visuals = request.form.getlist('entities')

        if "ALL" in visuals:
            visuals = ["LOC", "PERS", "ORG", "ROLE", "DEMO", "WORK", "EVENT"]
        # Saving the file in the required destination
        timestamp = str(datetime.utcnow()).replace(":", ".").replace(" ", ".")
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(timestamp+"_"+f.filename)))  # this will secure the file
        savedFilePath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(timestamp+"_"+f.filename))
        f_name, f_ext = os.path.splitext(savedFilePath)
        if f_ext != ".zip":
            return "You uploaded unzipped file"

        with ZipFile(savedFilePath, 'r') as zipped:

            directory = "static/uploads/temp" + timestamp
            zipped.extractall(directory)

            try:
                gold = os.listdir(directory + '/gold') if os.path.isdir(directory + '/gold/') else None
                evalu = os.listdir(directory + '/to_eval') if os.path.isdir(directory + '/to_eval/') else None
                text = os.listdir(directory + '/text') if os.path.isdir(directory + '/text/') else None

            except Exception as ex:
                print(ex)

        try:
            outputFolder = f"output/output{timestamp}"
            os.mkdir(outputFolder)

            if gold is not None and evalu is not None and text is not None:

                validation = Validation(gold, evalu, text, directory)
                fileCount = validation.fileCountValidation()

                if fileCount:

                    extensionCheck = validation.extensionCheckValidation()

                    if not extensionCheck:

                        alignment = validation.checkUnaligned()
                        aligned = []

                        if alignment:

                            validation.createUnalignedLogFile(alignment, outputFolder)

                            for name1, name2, lines in alignment:
                                aligned = validation.getAligned(name1, name2)

                        else:
                            aligned = validation.getAligned()

                        report = Report(aligned, directory)
                        report.analyze(outputFolder)
                        report.getVisualData(outputFolder, visuals)
                        shutil.make_archive(outputFolder, 'zip', outputFolder)
                        shutil.rmtree(outputFolder)
                        path = 'C:/Users/asus/PycharmProjects/flaskProject/' + outputFolder + '.zip'

                        return send_file(path)


                    else:
                        generateLogMessage("Some files have wrong extension. Only ann, xml and txt files are allowed.",
                                           outputFolder)
                        shutil.make_archive(outputFolder, 'zip', outputFolder)
                        shutil.rmtree(outputFolder)
                        path = 'C:/Users/asus/PycharmProjects/flaskProject/' + outputFolder + '.zip'

                        return send_file(path)


                else:
                    generateLogMessage("Number of files doesn't match in all folders.", outputFolder)
                    shutil.make_archive(outputFolder, 'zip', outputFolder)
                    shutil.rmtree(outputFolder)
                    path = 'C:/Users/asus/PycharmProjects/flaskProject/' + outputFolder + '.zip'

                    return send_file(path)

            else:
                generateLogMessage(
                    "Structure of uploaded zip file is wrong. Please include gold, to_eval and text directories.",
                    outputFolder)
                shutil.make_archive(outputFolder, 'zip', outputFolder)
                shutil.rmtree(outputFolder)
                path = 'C:/Users/asus/PycharmProjects/flaskProject/' + outputFolder + '.zip'

                return send_file(path)



        except ValueError as ex:

            print(ex)





if __name__ == '__main__':
    app.run()
