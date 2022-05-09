import os
from difflib import Differ
import xml.etree.ElementTree as ET
import shutil


class Annotation:

    def __init__(self, gold, toeval, text, directory=None):
        self.gold = gold
        self.eval = toeval
        self.text = text
        self.directory = directory

    @staticmethod
    def readFromFile(path):
        with open(path, "r", encoding='utf-8') as f:
            file = f.read()

        return file

    def getTagsFromXML(self, xmldata):
        # taking only annotation tags, which are conditioned to be capitalized

        try:
            xml = ET.fromstring(xmldata)
            tags = set()

            for child in xml.iter():
                if child.tag.isupper():
                    tags.add(child.tag)

            return tags

        except Exception as ex:
            print(ex)



    def stripTags(self, xmldata):
        try:
            cleanUp = self.getTagsFromXML(xmldata)
            tagless = ''
            f = xmldata
            for tag in cleanUp:
                tagless = f.replace("<" + tag + ">", '').replace("</" + tag + ">", '')
                f = tagless

            return tagless

        except Exception as ex:
            print(ex)

    def generateAnn(self, f, tags):

        annFormat = []
        term = 0

        for i in range(len(f)):
            try:
                if f[i] == "<":

                    tagEnd = f.find(">", i)
                    tag = f[i + 1:tagEnd]

                    if not tag.startswith("/") and tag in tags:
                        termNumber = f"T{term}"
                        term = term + 1

                        indexStart = i
                        alignStart = len(tag) + 2
                        alignEnd = len(tag) + 3
                        indexEnd = f.find('</' + tag + ">") - alignStart

                        word = f[indexStart + alignStart:indexEnd + alignStart]

                        f = f[0:i] + f[i + alignStart:indexEnd + alignStart] + f[indexEnd + alignStart + alignEnd:]

                        ann = f"{termNumber} {tag} {indexStart} {indexEnd} {word}\n"
                        annFormat.append(ann)



            except Exception as ex:
                continue

        return annFormat

    def getExtension(self, file):
        f_name, f_ext = os.path.splitext(file)
        return f_ext

    def getName(self, file):
        f_name, f_ext = os.path.splitext(file)
        return f_name

    def moveConllFiles(self):

        for g in self.gold:
            if g[-5:] == "conll":

                newpath = self.directory + '/goldConll'
                if not os.path.exists(newpath):
                    os.mkdir(newpath)
                if not os.path.exists(self.directory + '/gold/' + g + '/' + newpath):
                    shutil.move(self.directory + '/gold/' + g, newpath)

        for e in self.eval:
            if e[-5:] == "conll":

                newpath = self.directory + '/evalConll'
                if not os.path.exists(newpath):
                    os.mkdir(newpath)
                if not os.path.exists(self.directory + '/to_eval/' + e + '/' + newpath):
                    shutil.move(self.directory + '/to_eval/' + e, newpath)

    @staticmethod
    def clearUpLines(data):
        for i in range(len(data)):
            data[i] = data[i].replace('ᐸ', '<')
            data[i] = data[i].replace('ᐳ', '>')
            data[i] = data[i].replace('&', '&amp;')

        return data

    def convertConllToXml(self):

        inputDirs = [self.directory + '/goldConll', self.directory + '/evalConll']

        for dir in inputDirs:
            data_dir = dir + "/converted"

            for filename in os.listdir(dir):
                if not os.path.exists(data_dir):
                    os.mkdir(data_dir)
                try:
                    with open(os.path.join(dir, filename), 'r', encoding='utf-8') as file1:
                        file2 = open("{}/{}.xml".format(data_dir, filename.replace(".conll", "")), "w",
                                     encoding='utf-8')
                        curent = []
                        lines = file1.readlines()
                        lines.insert(0, '* O\n')
                        for line in lines:
                            if line == '\n':
                                lines.remove(line)

                        self.clearUpLines(lines)
                        file2.write('<xml>')
                        for i in range(len(lines) - 1):
                            item = lines[i]
                            part = item.split()
                            beg = part[0]  # pocetak
                            if beg[:3] == '<p>':
                                file2.write("\n")

                            if part[1] == 'O':
                                if len(curent) == 0:
                                    file2.write(part[0] + " ")
                                else:
                                    if curent[1] == 'O':
                                        file2.write(part[0] + " ")
                                    else:
                                        m = curent[1]
                                        file2.write("</" + m[2:].upper() + ">" + " " + part[0] + " ")
                            if part[1][0:2] in "B-":
                                a = part[1]
                                if curent[1][0:2] in "B-" or curent[1][0:2] in "I-":
                                    k = curent[1]
                                    file2.write("</" + k[2:].upper() + ">" + " " + "<" + a[2:].upper() + ">" + part[0])
                                else:
                                    if curent[1] == 'O':
                                        file2.write("<" + a[2:].upper() + ">" + part[0])
                            if part[1][0:2] in "I-":
                                file2.write(" " + part[0])
                            curent = part

                        file2.write('</xml>')
                except IndexError as ex:
                    file2.write('</xml>')
                    print(ex)

            file2.close()


class Validation(Annotation):

    def fileCountValidation(self):

        goldCount = 0
        evalCount = 0

        goldConllCount = 0
        evalConllCount = 0

        textCount = len(self.text) if self.text is not None else 0

        for f in self.gold:

            if f[-5:] == "conll":

                goldConllCount = goldConllCount + 1
            else:
                goldCount = goldCount + 1

        for f in self.eval:
            if f[-5:] == "conll":
                evalConllCount = evalConllCount + 1
            else:
                evalCount = evalCount + 1

        if textCount > 0:
            if goldCount == evalCount and evalCount == textCount and goldConllCount == evalConllCount:
                return [True, goldConllCount]
            else:
                return [False, False]
        else:
            if goldCount == evalCount and goldConllCount == evalConllCount:
                return [True, goldConllCount]
            else:
                return [False, False]

    def differentNamesValidation(self, conll):

        gold = self.gold
        eval = self.eval
        text = self.text

        if gold is not None and eval is not None and text is not None:
            for i, (gl, ev, txt) in enumerate(zip(gold, eval, text)):

                if self.getName(gl) == self.getName(ev) and self.getName(gl) == self.getName(txt):
                    continue
                else:
                    return True
        if conll:
            goldConllDir = os.listdir(self.directory + '/goldConll')
            evalConllDir = os.listdir(self.directory + '/evalConll')

            for i, (gl, ev) in enumerate(zip(goldConllDir, evalConllDir)):
                if self.getName(gl) == self.getName(ev):
                    continue
                else:
                    return True

    def extensionCheckValidation(self):

        errors = False

        for file in self.gold:
            f_ext = self.getExtension(file)
            if f_ext not in ('.ann', '.xml', '.conll'):
                errors = True
                break
        for file in self.eval:
            f_ext = self.getExtension(file)
            if f_ext not in ('.ann', '.xml', '.conll'):
                errors = True
                break
        if self.text is not None:
            for file in self.text:
                f_ext = self.getExtension(file)
                if f_ext not in '.txt':
                    errors = True
                    break

        return errors

    @staticmethod
    def performDiffer(file1, file2):

        differ = Differ()
        compared = differ.compare(file1, file2)

        for line in compared:
            if line[0] in ("+", "-"):
                """ on the first occurrence of a line that starts with + or -, we conclude
                 there are some differences so the function will return
                file name and result of Differ object comparison - which is needed for creating log report for
                unaligned files """
                return compared

        return False

    def checkUnaligned(self):

        gold = self.gold
        eval = self.eval
        text = self.text
        dirr = self.directory
        unalignedList = []

        for i, (gl, ev, txt) in enumerate(zip(gold, eval, text)):



            # check if current gold and to_eval files have .ann or .conll extension
            if self.getExtension(gl) == self.getExtension(ev) and (self.getExtension(ev) in ".ann" or ".conll"):

                pass

            if self.getExtension(gl) == self.getExtension(ev) and self.getExtension(ev) == ".xml":


                taglessGold = self.stripTags(self.readFromFile(dirr + "/gold/" + gl)).splitlines(keepends=True)
                taglessEval = self.stripTags(self.readFromFile(dirr + "/to_eval/" + ev)).splitlines(keepends=True)
                # text files are originally tagless; though they are sent to stripTags method as it also opens a file
                # and prepares it for processing
                text = self.readFromFile(dirr + "/text/" + txt).splitlines(keepends=True)

                unaligned = self.performDiffer(taglessGold, taglessEval)
                if not unaligned:
                    # if gold and eval are aligned, check if one of them (e.g. gold) is aligned with the original text
                    unaligned = self.performDiffer(taglessGold, text)
                    if unaligned:
                        unalignedList.append([gl, ev, unaligned])
                else:
                    unalignedList.append([gl, ev, unaligned])

            if self.getExtension(gl) == ".xml" and self.getExtension(ev) != ".xml":


                # ako je samo gold xml, poredi se on sa originalnim tekstom
                taglessGold = self.stripTags(self.readFromFile(dirr + "/gold/" + gl)).splitlines(keepends=True)

                text = self.readFromFile(dirr + "/text/" + txt).splitlines(keepends=True)

                unaligned = self.performDiffer(taglessGold, text)

                if unaligned:
                    unalignedList.append([gl, txt, unaligned])

            if self.getExtension(ev) == ".xml" and self.getExtension(gl) != ".xml":


                # u suprotnom, eval je xml, poredi se on sa originalnim tekstom
                taglessEval = self.stripTags(self.readFromFile(dirr + "/to_eval/" + ev)).splitlines(keepends=True)
                text = self.readFromFile(dirr + "/text/" + txt).splitlines(keepends=True)
                unaligned = self.performDiffer(taglessEval, text)
                if unaligned:
                    unalignedList.append([ev, txt, unaligned])

        return unalignedList

    @staticmethod
    def getLines(lines):
        ln = ""
        for i, line in enumerate(lines):

            if line[0] in ("+", "-"):
                ln = ln + line + "\n"
        return ln

    def createUnalignedLogFile(self, unaligned, outputfolder):

        text = """******************************************************
        Following files are excluded from analysis because they don't align properly. 
        You can find exact lines in which two files mismatch. 
        
        If you find that lines are identical please make sure files have the same encoding. For example, UTF-8 and UTF-8-BOM are not the same!
        
        Minus and plus signs represent lines that are unique in file1 and file2 respectively. 
        Such lines should be aligned manually.\n******************************************************\n\n\n"""
        with open(f"{outputfolder}/unalignedXMLFilesLog.txt", "a", encoding="utf-8") as file:
            input = ""

            for name1, name2, lines in unaligned:
                files = f"\n\nFile 1 {name1} // File 2 {name2} \n\n"
                linesText = self.getLines(lines)
                separator = "\n\n**************\n\n"

                input = input + files + linesText + separator

            file.write(text.strip() + "\n\n" + input.strip())

    def getAllAligned(self):
        gold = self.gold
        eval = self.eval
        text = self.text
        aligned = []

        for i, (gl, ev, txt) in enumerate(zip(gold, eval, text)):
            aligned.append([gl, ev, txt])

        return aligned

    def getSomeAligned(self, alignment):
        gold = self.gold
        eval = self.eval
        text = self.text
        aligned = []

        for name1, name2, lines in alignment:
            if name1 in gold:
                index = gold.index(name1)
                gold.pop(index)
                eval.pop(index)
                text.pop(index)
                continue

        for i, (gl, ev, txt) in enumerate(zip(gold, eval, text)):
            aligned.append([gl, ev, txt])

        return aligned


class Report(Annotation):


    def __init__(self, files, dir):
        self.dir = dir

        self.goldDir = dir + '/gold/'
        self.evalDir = dir + '/to_eval/'
        self.textDir = dir + '/text/'
        self.goldConllDir = self.dir + '/goldConll/converted/'
        self.evalConllDir = self.dir + '/evalConll/converted/'

        self.goldRep = []
        self.evalRep = []
        self.textRep = []

        if files is not None:
            for i, (gl, ev, txt) in enumerate(files):
                self.goldRep.append(gl)
                self.evalRep.append(ev)
                self.textRep.append(txt)




    def generateDataForAnalysis(self, conll=False):

        data = []
        gold = []
        eval = []
        text = []
        fileName = []
        # generating data for analysis of xml and ann files
        if self.textRep is not None:
            for i, (gld, evl, txt) in enumerate((zip(self.goldRep, self.evalRep, self.textRep))):

                goldPath = self.goldDir + gld
                evalPath = self.evalDir + evl
                txtPath = self.textDir + txt
                with open(goldPath, 'r', encoding='utf-8') as gl, open(evalPath, 'r', encoding='utf-8') as ev, open(
                        txtPath,
                        'r',
                        encoding='utf-8') as tx:

                    if gld[-3:] == "xml":
                        goldText = gl.read()
                        tags = self.getTagsFromXML(goldText)
                        gold.append(self.generateAnn(goldText, tags))

                    else:
                        originalAnn = gl.readlines()
                        if originalAnn[len(originalAnn) - 1] == '\n':
                            originalAnn.pop()
                        gold.append(originalAnn)

                    if evl[-3:] == "xml":
                        evalText = ev.read()
                        tags = self.getTagsFromXML(evalText)
                        eval.append(self.generateAnn(evalText, tags))

                    else:
                        originalAnn = ev.readlines()
                        if originalAnn[len(originalAnn) - 1] == '\n':
                            originalAnn.pop()
                        eval.append(originalAnn)

                    text.append(tx.read())
                    fileName.append(gld[0:-4])

        # generating data for analysis of conll files
        if conll:
            for filename in os.listdir(self.goldConllDir):
                fileName.append(filename[0:-4])
                goldPath = self.goldConllDir + filename

                with open(goldPath, 'r', encoding='utf-8') as gl:
                    go = gl.read()
                    text.append(self.stripTags(go))
                    tags = self.getTagsFromXML(go)
                    gold.append(self.generateAnn(go, tags))

            for filename in os.listdir(self.evalConllDir):
                evPath = self.evalConllDir + filename
                with open(evPath, 'r', encoding='utf-8') as ev:
                    eva = ev.read()
                    tags = self.getTagsFromXML(eva)
                    eval.append(self.generateAnn(eva, tags))

        data.append(gold)
        data.append(eval)
        data.append(text)
        data.append(fileName)

        return data

    def analyze(self, outputfolder, data):


        gold = data[0]
        eval = data[1]
        fileName = data[3]

        # quantitative analysis

        for i, (glS, evS, fnS) in enumerate((zip(gold, eval, fileName))):

            tpStrict = 0
            tpWeak = 0
            tpWeighted = 0

            for gl in glS:
                for ev in evS:
                    tpStrict = tpStrict + self.counttpStrict(ev, gl)
                    tpWeak = tpWeak + self.countTPWeak(ev, gl)
                    tpWeighted = tpWeighted + self.countTPWeighted(ev, gl)

            fpStrict = self.countfpStrict(evS, glS)
            fpWeak = fpStrict - (tpWeak - tpStrict)
            fn = self.countFN(evS, glS)

            try:
                strictPrecision = tpStrict / (tpStrict + fpStrict) if tpStrict != 0 and tpStrict + fpStrict != 0 else 0
                weightedPrecision = tpWeighted / (
                        tpWeighted + fpStrict) if tpWeighted != 0 and tpWeighted + fpStrict != 0 else 0
                weakPrecision = tpWeak / (tpWeak + fpWeak) if tpWeak != 0 and tpWeak + fpWeak != 0 else 0

                strictRecall = tpStrict / (tpStrict + fn) if tpStrict != 0 and tpStrict + fn != 0 else 0
                weightedRecall = tpWeighted / (tpWeighted + fn) if tpWeighted != 0 and tpWeighted + fn != 0 else 0
                weakRecall = tpWeak / (tpWeak + fn) if tpWeak != 0 and tpWeak + fn != 0 else 0

                strictf1 = 2 * strictPrecision * strictRecall / (
                        strictPrecision + strictRecall) if 2 * strictPrecision * strictRecall != 0 and strictPrecision + strictRecall != 0 else 0
                weightedf1 = 2 * weightedPrecision * weightedRecall / (
                        weightedPrecision + weightedRecall) if 2 * weightedPrecision * weightedRecall != 0 and weightedPrecision + weightedRecall != 0 else 0
                weakf1 = 2 * weakPrecision * weakRecall / (
                        weakPrecision + weakRecall) if 2 * weakPrecision * weakRecall != 0 and weakPrecision + weakRecall != 0 else 0
            except Exception as ex:
                print(ex)
                strictPrecision = 0
                weightedPrecision = 0
                weakPrecision = 0
                strictRecall = 0
                weightedRecall = 0
                weakRecall = 0
                strictf1 = 0
                weightedf1 = 0
                weakf1 = 0

            # save output in output/FILENAMEdir
            outputDir = f"{outputfolder}/{fnS}"
            if not os.path.exists(outputDir):
                os.mkdir(outputDir)
            content = f"""
 **PRECISION**
 strict precision: {format(strictPrecision, '.3f')}
 weighted precision: {format(weightedPrecision, '.3f')}
 weak precision: {format(weakPrecision, '.3f')}

 **RECALL**
 strict recall: {format(strictRecall, '.3f')}
 weighted recall: {format(weightedRecall, '.3f')}
 weak recall: {format(weakRecall, '.3f')}

 **F1**
 strict F1: {format(strictf1, '.3f')}
 weighted F1: {format(weightedf1, '.3f')}
 weak F1: {format(weakf1, '.3f')}
                    """
            with open(outputDir + "/" + str(fnS) + "_REPORT.txt", 'w', encoding='utf-8') as out:
                out.write(content)


    @staticmethod
    def counttpStrict(eval, gold):

        if eval.split(None, 4)[1:] == gold.split(None, 4)[1:]:
            return 1

        return 0

    @staticmethod
    def countTPWeighted(eval, gold):

        ev = eval.split(None, 4)
        gl = gold.split(None, 4)

        if ev[1:] == gl[1:]:
            return 1

        evRange = set(range(int(ev[2]), int(ev[3]) + 1))
        glRange = set(range(int(gl[2]), int(gl[3]) + 1))
        evChar = len(ev[4])
        glChar = len(gl[4])

        if evRange.intersection(glRange):
            numberOfIntersectedChars = len(evRange.intersection(glRange))
            return numberOfIntersectedChars / (evChar + glChar)

        return 0

    @staticmethod
    def countTPWeak(eval, gold):

        ev = eval.split(None, 4)
        gl = gold.split(None, 4)

        evRange = set(range(int(ev[2]), int(ev[3]) + 1))
        glRange = set(range(int(gl[2]), int(gl[3]) + 1))

        if evRange.intersection(glRange):
            return 1

        return 0

    @staticmethod
    def countfpStrict(eval, gold):

        check = 0
        count = 0
        for ev in eval:
            for gl in gold:
                if ev.split(None, 4)[1:] != gl.split(None, 4)[1:]:
                    check = 0
                else:
                    check = 1
                    break
            if check == 0:
                count = count + 1

        return count

    @staticmethod
    def countFN(eval, gold):

        check = 0
        count = 0
        wrongLabel = 0
        for gl in gold:
            for ev in eval:

                if ev.split(None, 4)[1:] != gl.split(None, 4)[1:]:
                    check = 0
                else:
                    check = 1
                    break
            if check == 0:
                count = count + 1

        for gl in gold:
            for ev in eval:

                if ev.split(None, 4)[1] != gl.split(None, 4)[1] and ev.split(None, 4)[2:] == gl.split(None, 4)[2:]:
                    wrongLabel = wrongLabel + 1

        return count - wrongLabel

    def splitByAnnType(self, annotation, annType):
        result = []
        for ann in annotation:
            split = ann.split(None, 4)[1:]
            if split[0] in annType:
                result.append(split)
        return result

    def splitAnn(self, annotation):
        result = []
        for ann in annotation:
            split = ann.split(None, 4)[1:]
            result.append(split)

        return result

    def annBelongCheck(self, ann, annArray):

        for arr in annArray:
            if ann[1:] == arr[1:]:
                return True
        return False

    def differentTypesCheck(self, ann, annArray):

        for arr in annArray:
            if ann == arr:
                return True
        return False

    @staticmethod
    def getHTMLTemplate():
        pt1 = '''
            <!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualisation</title>
    <style>
         *{
	margin: 0px;
	padding: 0px;
        }
        #legends{
            display: block;
            margin:100px auto;
            width:90%;
            min-height: 200px;
            background-color: RGB(237, 209, 176);

        }
		body {
		
    background-color: RGB(219, 225, 241);
		}
        #text{
            display: block;
            padding: 2.5rem;
            margin: 100px auto;
            width:90%;
            border: solid thin #000;
            border-radius: 0.5rem;
            letter-spacing: 2px;
            font-size: 2rem;
            background-color: #f1dca7;
            box-shadow: 20px 20px 10px grey;
			line-height: 50px;
        }

        #text p{
            background-color: #f1dca7;
        }
		
			
.TT1_all {border:4px;
border-style:solid;
border-color:#f77f00;
padding: 4px;}
 .TT2_all {border:4px;
border-style:solid;
border-color:#023e8a;
}
.TT1_sta{
border-top: 4px solid #f77f00;
border-bottom: 4px solid #f77f00;
border-left: 4px solid #f77f00;
padding: 4px;
}
.TT1_end{
border-top: 4px solid #f77f00;
border-bottom: 4px solid #f77f00;
border-right: 4px solid #f77f00;
padding: 4px;
}
.TT1_mid{
border-top: 4px solid #f77f00;
border-bottom: 4px solid #f77f00;
padding: 4px;
}
.TT2_sta{
border-top: 4px solid #023e8a;
border-bottom: 4px solid #023e8a;
border-left: 4px solid #023e8a;
}
.TT2_end{
border-top: 4px solid #023e8a;
border-bottom: 4px solid #023e8a;
border-right: 4px solid #023e8a;
}
.TT2_mid{
border-top: 4px solid #023e8a;
border-bottom: 4px solid #023e8a;
}
		#legends ul {
			list-style-type:none;
			padding:2rem;
			font-size:2rem;
			
		}
		
		#legends ul li{
			margin-top: 15px;
		}
    </style>
</head>
<body>
    <div id="content">
    <div id="legends">
        <ul>
			<li><span class='TT2_all'>blue border</span>: entity recognized in gold annotation</li>
			<li><span class='TT1_all'>orange border</span>: entity recognized in to_eval annotation</li>
		</ul>
    </div>
    <div id="text">
        '''

        pt2 = "</div></body></html>"

        return [pt1, pt2]

    @staticmethod
    def getNext(index, array):
        element = array[index + 1][0:4] if index < len(array) - 1 else array[index][0:4]
        return element

    def getElementRange(self, element):
        return set(range(int(element[1]), int(element[2]) + 1))

    def intersectionConditions(self, current, nextEl, arrayOfIntersected):
        return self.getElementRange(current).intersection(self.getElementRange(
            nextEl)) and current != nextEl and current not in arrayOfIntersected and nextEl not in arrayOfIntersected

    @staticmethod
    def containsKey(changeStatus, position):

        chStatus = changeStatus

        for i in range(len(chStatus)):

            if chStatus[i][0] == position:
                return True

        return False

    @staticmethod
    def getValueByKey(changeStatus, position):

        chStatus = changeStatus

        for i in range(len(chStatus)):
            if chStatus[i][0] == position:
                return chStatus[i][1]

        return 0

    def getVisualData(self, outputFolder, visuals, data):


        gold = data[0]
        eval = data[1]
        text = data[2]
        fileName = data[3]
        # qualitative analysis

        for i, (glS, evS, txT, fnS) in enumerate((zip(gold, eval, text, fileName))):

            for annType in visuals:

                glN = self.splitByAnnType(glS, annType)
                evN = self.splitByAnnType(evS, annType)
                text = txT

                changeStatus = []

                for e in evN:
                    if e[1] == e[2]:
                        continue
                    start = int(e[1])
                    end = int(e[2])

                    changeStatus.append([start, 1])
                    changeStatus.append([end, 3])



                for g in glN:
                    if g[1] == g[2]:
                        continue
                    start = int(g[1])
                    end = int(g[2])

                    status = 2 if not self.containsKey(changeStatus, start) else self.getValueByKey(changeStatus,
                                                                                                    start) + 4
                    changeStatus.append([start, status])

                    status = 4 if not self.containsKey(changeStatus, end) else self.getValueByKey(changeStatus, end) + 5
                    changeStatus.append([end, status])




                changeStatus = sorted(changeStatus)

                removal = []

                for i in range(len(changeStatus) - 1):

                    if changeStatus[i][0] == changeStatus[i + 1][0]:
                        removal.append(changeStatus[i])

                for r in removal:
                    changeStatus.remove(r)



                nbLetterBefore = 0



                try:
                    entrys = changeStatus

                    for x in range(1, 3):
                        textStatus = 0

                        for i in range(len(entrys)):

                            if x == 2:
                                for c in range(textStatus):
                                    text = text[0:entrys[i][0] + nbLetterBefore] + "</span>" + text[entrys[i][
                                                                                                        0] + nbLetterBefore:]
                                    nbLetterBefore = nbLetterBefore + 7

                            if entrys[i][1] == 1 or entrys[i][1] == 6:

                                if entrys[i][1] == 6:
                                    textStatus = textStatus - 1
                                if textStatus == 1:
                                    entrys[i][1] = 9

                                else:
                                    if x == 2:
                                        if entrys[i + 1][1] == 3 or entrys[i + 1][1] == 7:
                                            text = text[
                                                   0:entrys[i][0] + nbLetterBefore] + '<span class="TT1_all">' + text[
                                                                                                                 entrys[
                                                                                                                     i][
                                                                                                                     0] + nbLetterBefore:]
                                        if entrys[i + 1][1] == 10:
                                            text = text[
                                                   0:entrys[i][0] + nbLetterBefore] + '<span class="TT1_sta">' + text[
                                                                                                                 entrys[
                                                                                                                     i][
                                                                                                                     0] + nbLetterBefore:]
                                        nbLetterBefore = nbLetterBefore + 22

                                    textStatus = textStatus + 1

                            if entrys[i][1] == 2 or entrys[i][1] == 7:

                                if entrys[i][1] == 7:
                                    textStatus = textStatus - 1
                                if textStatus == 1:
                                    entrys[i][1] = 10
                                else:
                                    if x == 2:
                                        if entrys[i + 1][1] == 4 or entrys[i + 1][1] == 6:
                                            text = text[
                                                   0:entrys[i][0] + nbLetterBefore] + '<span class="TT2_all">' + text[
                                                                                                                 entrys[
                                                                                                                     i][
                                                                                                                     0] + nbLetterBefore:]
                                        if entrys[i + 1][1] == 9:
                                            text = text[
                                                   0:entrys[i][0] + nbLetterBefore] + '<span class="TT2_sta">' + text[
                                                                                                                 entrys[
                                                                                                                     i][
                                                                                                                     0] + nbLetterBefore:]
                                        nbLetterBefore = nbLetterBefore + 22

                                    textStatus = textStatus + 1

                            if entrys[i][1] == 3 or entrys[i][1] == 4:


                                if textStatus == 2:

                                    entrys[i][1] = entrys[i][1] + 8



                                else:
                                    textStatus = textStatus - 1

                            if entrys[i][1] == 5:

                                if x == 2:


                                    if entrys[i + 1][1] == 11:


                                        text = text[
                                               0:entrys[i][
                                                     0] + nbLetterBefore] + '<span class="TT1_all"><span class="TT2_sta">' + text[
                                                                                                                             entrys[
                                                                                                                                 i][
                                                                                                                                 0] + nbLetterBefore:]
                                    if entrys[i + 1][1] == 12:


                                        text = text[
                                               0:entrys[i][
                                                     0] + nbLetterBefore] + '<span class="TT1_sta"><span class="TT2_all">' + text[
                                                                                                                             entrys[
                                                                                                                                 i][
                                                                                                                                 0] + nbLetterBefore:]

                                    if entrys[i + 1][1] == 8:

                                        text = text[
                                               0:entrys[i][
                                                     0] + nbLetterBefore] + '<span class="TT1_all"><span class="TT2_all">' + text[
                                                                                                                             entrys[
                                                                                                                                 i][
                                                                                                                                 0] + nbLetterBefore:]

                                    nbLetterBefore = nbLetterBefore + 44

                                textStatus = textStatus + 2

                            if entrys[i][1] == 8:
                                textStatus = textStatus - 2

                            if entrys[i][1] == 9:


                                if x == 2:
                                    if entrys[i + 1][1] == 11:
                                        text = text[
                                               0:entrys[i][
                                                     0] + nbLetterBefore] + '<span class="TT1_all"><span class="TT2_mid">' + text[
                                                                                                                             entrys[
                                                                                                                                 i][
                                                                                                                                 0] + nbLetterBefore:]
                                    if entrys[i + 1][1] == 12:
                                        text = text[
                                               0:entrys[i][
                                                     0] + nbLetterBefore] + '<span class="TT1_sta"><span class="TT2_end">' + text[
                                                                                                                             entrys[
                                                                                                                                 i][
                                                                                                                                 0] + nbLetterBefore:]
                                    if entrys[i + 1][1] == 8:
                                        text = text[
                                               0:entrys[i][
                                                     0] + nbLetterBefore] + '<span class="TT1_all"><span class="TT2_end">' + text[
                                                                                                                             entrys[
                                                                                                                                 i][
                                                                                                                                 0] + nbLetterBefore:]

                                    nbLetterBefore = nbLetterBefore + 44

                                textStatus = textStatus + 1

                            if entrys[i][1] == 10:


                                if x == 2:
                                    if entrys[i + 1][1] == 11:
                                        text = text[
                                               0:entrys[i][
                                                     0] + nbLetterBefore] + '<span class="TT1_end"><span class="TT2_sta">' + text[
                                                                                                                             entrys[
                                                                                                                                 i][
                                                                                                                                 0] + nbLetterBefore:]
                                    if entrys[i + 1][1] == 12:
                                        text = text[
                                               0:entrys[i][
                                                     0] + nbLetterBefore] + '<span class="TT1_mid"><span class="TT2_all">' + text[
                                                                                                                             entrys[
                                                                                                                                 i][
                                                                                                                                 0] + nbLetterBefore:]
                                    if entrys[i + 1][1] == 8:

                                        text = text[
                                               0:entrys[i][
                                                     0] + nbLetterBefore] + '<span class="TT1_end"><span class="TT2_all">' + text[
                                                                                                                             entrys[
                                                                                                                                 i][
                                                                                                                                 0] + nbLetterBefore:]


                                    nbLetterBefore = nbLetterBefore + 44

                                textStatus = textStatus + 1

                            if entrys[i][1] == 11:


                                if x == 2:
                                    if entrys[i + 1][1] == 4 or entrys[i + 1][1] == 6:

                                        text = text[
                                               0:entrys[i][
                                                     0] + nbLetterBefore] + '<span class="TT2_end">' + text[entrys[i][
                                                                                                                0] + nbLetterBefore:]
                                    if entrys[i + 1][1] == 9:

                                        text = text[
                                               0:entrys[i][
                                                     0] + nbLetterBefore] + '<span class="TT2_mid">' + text[entrys[i][
                                                                                                                0] + nbLetterBefore:]

                                    nbLetterBefore = nbLetterBefore + 22

                                textStatus = textStatus - 1

                            if entrys[i][1] == 12:

                                if x == 2:

                                    if entrys[i + 1][1] == 3 or entrys[i + 1][1] == 7:
                                        text = text[
                                               0:entrys[i][0] + nbLetterBefore] + '<span class="TT1_end">' + text[
                                                                                                             entrys[i][
                                                                                                                 0] + nbLetterBefore:]
                                    if entrys[i + 1][1] == 10:
                                        text = text[
                                               0:entrys[i][
                                                     0] + nbLetterBefore] + '<span class="TT1_mid">' + text[entrys[i][
                                                                                                                0] + nbLetterBefore:]

                                    nbLetterBefore = nbLetterBefore + 22

                                textStatus = textStatus - 1

                        if x == 2:
                            for c in range(textStatus + 1):

                                text = text[0:entrys[i][0] + nbLetterBefore] + '</span>' + text[entrys[i][
                                                                                                    0] + nbLetterBefore:]



                    # creating a file
                    text = text.replace("ᐸ", "<")
                    text = text.replace("ᐳ", ">")
                    text = text.replace("<s>", "")
                    text = text.replace("</s>", "")

                    outputDir = f"{outputFolder}/{fnS}"
                    name = fnS + "_" + annType + ".html"
                    htmlTemplate = self.getHTMLTemplate()
                    with open(outputDir + "/" + name, 'w', encoding='utf-8') as out:
                        out.write(htmlTemplate[0] + text + htmlTemplate[1])

                except Exception as e:
                    print('exception: {} -- no entries for {} in {}'.format(e, annType, fnS))

    def generateTableData(self, path, visuals):
        global present
        links = []
        logFilePath = None

        for folder in os.listdir(path):
            if folder[-3:] != 'txt':
                rowData = [folder]
                for visType in visuals:
                    present = False
                    folderPath = path + '/' + folder
                    for file in os.listdir(folderPath):

                        if visType in file:
                            present = True
                            rowData.append(folderPath + '/' + file)
                            break

                    if not present:
                        rowData.append("-")

                links.append(rowData)
            else:
                logFilePath = path + '/' + folder

        return [links, logFilePath]
