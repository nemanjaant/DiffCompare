import os
from difflib import Differ


class Annotation:

    def __init__(self, gold, toeval, text, directory=None):
        self.gold = gold
        self.eval = toeval
        self.text = text
        self.directory = directory

    def stripTags(self, directory, folder, file):
        cleanUp = ["<PERS>", "</PERS>", "<ORG>", "</ORG>", "<LOC>", "</LOC>", "<ROLE>", "</ROLE>", "<DEMO>", "</DEMO>",
                   "<EVENT>", "</EVENT>", "<WORK>", "</WORK>"]

        with open(directory + folder + file, "r", encoding="utf-8") as openFile:
            f = openFile.read()
            for tag in cleanUp:
                tagless = f.replace(tag, '')
                f = tagless

        return tagless

    def generateAnn(self, f):
        mf = f
        annFormat = []
        term = 0

        for i in range(len(mf)):

            try:
                if f[i] == "<" and (f[i + 1:i + 6] in ("PERS>", "ROLE>", "DEMO>", "WORK>")
                                    or f[i + 1:i + 5] in ("LOC>", "ORG>") or f[i + 1:i + 7] in "EVENT>"):
                    termNumber = f"T{term}"
                    term = term + 1

                    if f[i + 1:i + 6] == "PERS>":
                        indexStart = i
                        indexEnd = f.find('</PERS>') - 6
                        word = f[i + 6:indexEnd + 6]
                        f = f[0:i] + f[i + 6:indexEnd + 6] + f[indexEnd + 13:]
                        ann = f"{termNumber} PERS {indexStart} {indexEnd} {word}\n"
                        annFormat.append(ann)


                    elif f[i + 1:i + 6] == "ROLE>":
                        indexStart = i
                        indexEnd = f.find('</ROLE>') - 6
                        word = f[i + 6:indexEnd + 6]
                        f = f[0:i] + f[i + 6:indexEnd + 6] + f[indexEnd + 13:]
                        ann = f"{termNumber} ROLE {indexStart} {indexEnd} {word}\n"
                        annFormat.append(ann)

                    elif f[i + 1:i + 6] == "DEMO>":
                        indexStart = i
                        indexEnd = f.find('</DEMO>') - 6
                        word = f[i + 6:indexEnd + 6]
                        f = f[0:i] + f[i + 6:indexEnd + 6] + f[indexEnd + 13:]
                        ann = f"{termNumber} DEMO {indexStart} {indexEnd} {word}\n"
                        annFormat.append(ann)

                    elif f[i + 1:i + 6] == "WORK>":
                        indexStart = i
                        indexEnd = f.find('</WORK>') - 6
                        word = f[i + 6:indexEnd + 6]
                        f = f[0:i] + f[i + 6:indexEnd + 6] + f[indexEnd + 13:]
                        ann = f"{termNumber} WORK {indexStart} {indexEnd} {word}\n"
                        annFormat.append(ann)

                    elif f[i + 1:i + 5] == "LOC>":
                        indexStart = i
                        indexEnd = f.find('</LOC>') - 5
                        word = f[i + 5:indexEnd + 5]
                        f = f[0:i] + f[i + 5:indexEnd + 5] + f[indexEnd + 11:]
                        ann = f"{termNumber} LOC {indexStart} {indexEnd} {word}\n"
                        annFormat.append(ann)

                    elif f[i + 1:i + 5] == "ORG>":
                        indexStart = i
                        indexEnd = f.find('</ORG>') - 5
                        word = f[i + 5:indexEnd + 5]
                        f = f[0:i] + f[i + 5:indexEnd + 5] + f[indexEnd + 11:]
                        ann = f"{termNumber} ORG {indexStart} {indexEnd} {word}\n"
                        annFormat.append(ann)

                    elif f[i + 1:i + 7] == "EVENT>":
                        indexStart = i
                        indexEnd = f.find('</EVENT>') - 7
                        word = f[i + 7:indexEnd + 7]
                        f = f[0:i] + f[i + 7:indexEnd + 7] + f[indexEnd + 14:]
                        ann = f"{termNumber} EVENT {indexStart} {indexEnd} {word}\n"
                        annFormat.append(ann)

            except Exception:
                break

        return annFormat

    def getExtension(self, file):
        f_name, f_ext = os.path.splitext(file)
        return f_ext

    def getName(self, file):
        f_name, f_ext = os.path.splitext(file)
        return f_name


class Validation(Annotation):

    def fileCountValidation(self):

        if len(self.gold) == len(self.eval) and len(self.eval) == len(self.text):
            return True
        else:
            return False

    def extensionCheckValidation(self):

        errors = []

        for file in self.gold:
            f_ext = self.getExtension(file)
            if f_ext not in ('.ann', '.xml'):
                errors.append("There are files with wrong extensions in gold folder")
                break
        for file in self.eval:
            f_ext = self.getExtension(file)
            if f_ext not in ('.ann', '.xml'):
                errors.append("There are files with wrong extensions in to_eval folder")
                break
        for file in self.text:
            f_ext = self.getExtension(file)
            if f_ext not in '.txt':
                errors.append("There are files with wrong extensions in text folder")
                break

        return errors

    @staticmethod
    def performDiffer(file1, file2):

        differ = Differ()
        compared = differ.compare(file1, file2)
        unaligned = []
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

            # check if both gold and to_eval directories have only .ann files
            if self.getExtension(gl) == self.getExtension(ev) and self.getExtension(ev) == ".ann":

                continue

            elif self.getExtension(gl) == self.getExtension(ev) and self.getExtension(ev) == ".xml":

                taglessGold = self.stripTags(dirr, "/gold/", gl).splitlines(keepends=True)
                taglessEval = self.stripTags(dirr, "/to_eval/", ev).splitlines(keepends=True)
                # text files are originally tagless; though they are sent to stripTags method as it also opens a file
                # and prepares it for processing
                text = self.stripTags(dirr, "/text/", txt).splitlines(keepends=True)

                unaligned = self.performDiffer(taglessGold, taglessEval)
                if not unaligned:
                    # if gold and eval are aligned, check if one of them (e.g. gold) is aligned with the original text
                    unaligned = self.performDiffer(taglessGold, text)
                    if unaligned:
                        unalignedList.append([gl, ev, unaligned])
                else:
                    unalignedList.append([gl, ev, unaligned])


            elif self.getExtension(gl) == ".xml":
                # ako je samo gold xml, poredi se on sa originalnim tekstom
                taglessGold = self.stripTags(dirr, "/gold/", gl).splitlines(keepends=True)

                text = self.stripTags(dirr, "/text/", txt).splitlines(keepends=True)

                unaligned = self.performDiffer(taglessGold, text)

                if unaligned:
                    unalignedList.append([gl, txt, unaligned])


            else:
                # u suprotnom, eval je xml, poredi se on sa originalnim tekstom
                taglessEval = self.stripTags(dirr, "/to_eval/", ev).splitlines(keepends=True)
                text = self.stripTags(dirr, "/text/", txt).splitlines(keepends=True)
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

    def getAligned(self, name1=None, name2=None):
        gold = self.gold
        eval = self.eval
        text = self.text
        aligned = []

        for i, (gl, ev, txt) in enumerate(zip(gold, eval, text)):

            if name1 is None and name2 is None:

                aligned.append([gl, ev, txt])

            else:

                if name1 not in (gl, ev, txt) or name2 not in (gl, ev, txt):
                    aligned.append([gl, ev, txt])

        return aligned


class Report(Annotation):
    gold = []
    eval = []
    text = []
    dir = ''
    goldDir = ''
    evalDir = ''
    textDir = ''

    def __init__(self, files, dir):

        for i, (gl, ev, txt) in enumerate(files):
            self.gold.append(gl)
            self.eval.append(ev)
            self.text.append(txt)

        self.dir = dir
        self.goldDir = dir + '/gold/'
        self.evalDir = dir + '/to_eval/'
        self.textDir = dir + '/text/'

    def generateDataForAnalysis(self):

        data = []
        gold = []
        eval = []
        text = []
        fileName = []
        # generating data for analysis
        for i, (gld, evl, txt) in enumerate((zip(self.gold, self.eval, self.text))):

            goldPath = self.goldDir + gld
            evalPath = self.evalDir + evl
            txtPath = self.textDir + txt
            with open(goldPath, 'r', encoding='utf-8') as gl, open(evalPath, 'r', encoding='utf-8') as ev, open(txtPath,
                                                                                                                'r',
                                                                                                                encoding='utf-8') as tx:

                if (gld[-3:] == "xml"):
                    gold.append(self.generateAnn(gl.read()))

                else:
                    originalAnn = gl.readlines()
                    if originalAnn[len(originalAnn) - 1] == '\n':
                        originalAnn.pop()
                    gold.append(originalAnn)

                if (evl[-3:] == "xml"):
                    eval.append(self.generateAnn(ev.read()))

                else:
                    originalAnn = ev.readlines()
                    if originalAnn[len(originalAnn) - 1] == '\n':
                        originalAnn.pop()
                    eval.append(originalAnn)

                text.append(tx.read())
                fileName.append(gld[0:-4])

        data.append(gold)
        data.append(eval)
        data.append(text)
        data.append(fileName)

        return data

    def analyze(self, outputfolder):

        data = self.generateDataForAnalysis()
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

        return True

    @staticmethod
    def counttpStrict(eval, gold):

        if (eval.split(None, 4)[1:] == gold.split(None, 4)[1:]):
            return 1

        return 0

    @staticmethod
    def countTPWeighted(eval, gold):

        ev = eval.split(None, 4)
        gl = gold.split(None, 4)
        evRange = set(range(int(ev[2]), int(ev[3]) + 1))
        glRange = set(range(int(gl[2]), int(gl[3]) + 1))
        evChar = len(ev[4])
        glChar = len(gl[4])

        large = 0
        small = 0

        if evChar > glChar:
            large = evChar
            small = glChar
        else:
            large = glChar
            small = evChar

        if evRange.intersection(glRange):
            return small / large

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
            if (check == 0):
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

    def getVisualData(self, outputFolder, annTypes):

        data = self.generateDataForAnalysis()
        gold = data[0]
        eval = data[1]
        text = data[2]
        fileName = data[3]
        # quantitative analysis

        for i, (glS, evS, txT, fnS) in enumerate((zip(gold, eval, text, fileName))):

            for annType in annTypes:

                glN = self.splitByAnnType(glS, annType)
                evN = self.splitByAnnType(evS, annType)
                text = txT

                status = 1
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

                            if entrys[i][1] == 5 or entrys[i][1] == 15 or entrys[i][1] == 25:

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
                                    if entrys[i + 1][1] == 9:
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


                    if text == "":
                        text = "No matches!"
                    outputDir = f"{outputFolder}/{fnS}"
                    name = fnS + "_" + annType + ".html"
                    htmlTemplate = self.getHTMLTemplate()
                    with open(outputDir + "/" + name, 'w', encoding='utf-8') as out:
                        out.write(htmlTemplate[0] + text + htmlTemplate[1])

                except Exception as e:
                    print('exception: {} -- no entries for {} in {}'.format(e, annType, fnS))


def generateLogMessage(msg):
    with open("errorLog.txt", "w") as log:
        log.write(msg)
