import os
import shutil
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from Classes import Validation, Report
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
    return render_template('appInterface.html')


@app.route('/compareNER', methods=['POST'])
def compareNER():
    if request.method == 'POST':

        f = request.files['file']  # get the file from the files object
        visuals = request.form.getlist('entities')

        if "ALL" in visuals:
            visuals = ["PERS", "LOC", "ORG", "ROLE", "DEMO", "WORK", "EVENT", 'MONEY', 'DEMONYM', 'TIME', 'AMOUNT',
                       'PERCENT', 'MEASURE']

        # Saving the file in the required destination
        timestamp = str(datetime.utcnow()).replace(":", ".").replace(" ", ".")
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],
                            secure_filename(timestamp + "_" + f.filename)))  # this will secure the file
        savedFilePath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(timestamp + "_" + f.filename))
        f_name, f_ext = os.path.splitext(savedFilePath)
        if f_ext != ".zip":
            return "Please, upload .zip archive"

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

            if not os.path.exists('output'):
                os.mkdir('output')

            outputFolder = f"output/output{timestamp}"
            os.mkdir(outputFolder)

            if gold is not None and evalu is not None:

                validation = Validation(gold, evalu, text, directory)
                fileCount = validation.fileCountValidation()

                if fileCount[0]:

                    wrongExtensions = validation.extensionCheckValidation()

                    if not wrongExtensions:

                        conll = False

                        if fileCount[1] != 0:
                            # if there are conll files they will be moved to another folder because they require additioanl prepocessing
                            validation.moveConllFiles()
                            validation.convertConllToXml()
                            conll = True

                        differentNames = validation.differentNamesValidation(conll)

                        if not differentNames:

                            if validation.text is not None:

                                alignment = validation.checkUnaligned()

                                if alignment:

                                    validation.createUnalignedLogFile(alignment, outputFolder)
                                    aligned = validation.getSomeAligned(alignment)


                                else:
                                    aligned = validation.getAllAligned()
                            else:
                                aligned = None

                            report = Report(aligned, directory)
                            report.analyze(outputFolder, conll)
                            report.getVisualData(outputFolder, visuals, conll)
                            shutil.make_archive(outputFolder, 'zip', outputFolder)
                            # shutil.rmtree(outputFolder)  # removing output folder after creating zip
                            # todo PODESITI LINKOVE ZA SERVER
                            path = 'C:/Users/asus/PycharmProjects/flaskProject/' + outputFolder
                            visuals.insert(0, "REPORT")
                            tableData = report.generateTableData(path, visuals)
                            donwnloadPath = 'C:/Users/asus/PycharmProjects/flaskProject/' + outputFolder + '.zip'

                            return render_template("appInterface.html", data=tableData[0], lenData=len(tableData[0]),
                                                   log=tableData[1], visuals=visuals, download=donwnloadPath)

                        else:
                            return render_template("appInterface.html",
                                                   text="There are files in gold, to_eval or text folder whose names are not the same.")


                    else:
                        return render_template("appInterface.html",
                                               text="There are files with wrong extension in following folder(s): " + ", ".join(
                                                   wrongExtensions))

                else:
                    return render_template("appInterface.html",
                                           text="Number of files doesn't match in all folders. Please check if each ann/xml file in gold/to_eval has its corresponding txt file, or if each conll file in gold folder has its corresponding conll file in to_eval folder")

            else:
                return render_template("appInterface.html",
                                       text="Structure of uploaded zip file is wrong. Please include only gold, to_eval and text directories.")



        except ValueError as ex:

            print(ex)


@app.route('/download', methods=['POST'])
def downloadFile():
    if request.method == 'POST':
        path = request.form.get('download')
        return send_file(path)


if __name__ == '__main__':
    app.run()
