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
                        indexStart = i + 7
                        indexEnd = f.find('</PERS>') - 6
                        word = f[i + 6:indexEnd + 6]
                        f = f[0:i] + f[i + 6:indexEnd + 6] + f[indexEnd + 13:]
                        ann = f"{termNumber} PERS {indexStart} {indexEnd} {word}"
                        annFormat.append(ann)

                    elif f[i + 1:i + 6] == "ROLE>":
                        indexStart = i + 7
                        indexEnd = f.find('</ROLE>') - 6
                        word = f[i + 6:indexEnd + 6]
                        f = f[0:i] + f[i + 6:indexEnd + 6] + f[indexEnd + 13:]
                        ann = f"{termNumber} ROLE {indexStart} {indexEnd} {word}"
                        annFormat.append(ann)

                    elif f[i + 1:i + 6] == "DEMO>":
                        indexStart = i + 7
                        indexEnd = f.find('</DEMO>') - 6
                        word = f[i + 6:indexEnd + 6]
                        f = f[0:i] + f[i + 6:indexEnd + 6] + f[indexEnd + 13:]
                        ann = f"{termNumber} DEMO {indexStart} {indexEnd} {word}"
                        annFormat.append(ann)

                    elif f[i + 1:i + 6] == "WORK>":
                        indexStart = i + 7
                        indexEnd = f.find('</WORK>') - 6
                        word = f[i + 6:indexEnd + 6]
                        f = f[0:i] + f[i + 6:indexEnd + 6] + f[indexEnd + 13:]
                        ann = f"{termNumber} WORK {indexStart} {indexEnd} {word}"
                        annFormat.append(ann)

                    elif f[i + 1:i + 5] == "LOC>":
                        indexStart = i + 6
                        indexEnd = f.find('</LOC>') - 5
                        word = f[i + 5:indexEnd + 5]
                        f = f[0:i] + f[i + 5:indexEnd + 5] + f[indexEnd + 11:]
                        ann = f"{termNumber} LOC {indexStart} {indexEnd} {word}"
                        annFormat.append(ann)

                    elif f[i + 1:i + 5] == "ORG>":
                        indexStart = i + 6
                        indexEnd = f.find('</ORG>') - 5
                        word = f[i + 5:indexEnd + 5]
                        f = f[0:i] + f[i + 5:indexEnd + 5] + f[indexEnd + 11:]
                        ann = f"{termNumber} ORG {indexStart} {indexEnd} {word}"
                        annFormat.append(ann)

                    elif f[i + 1:i + 7] == "EVENT>":
                        indexStart = i + 8
                        indexEnd = f.find('</EVENT>') - 7
                        word = f[i + 7:indexEnd + 7]
                        f = f[0:i] + f[i + 7:indexEnd + 7] + f[indexEnd + 14:]
                        ann = f"{termNumber} EVENT {indexStart} {indexEnd} {word}"
                        annFormat.append(ann)

            except Exception:
                break

        return annFormat


class Validation(Annotation):

    def fileCountValidation(self):

        if len(self.gold) == len(self.eval) and len(self.eval) == len(self.text):
            return True
        else:
            return False

    def getExtension(self, file):
        f_name, f_ext = os.path.splitext(file)
        return f_ext

    def getName(self, file):
        f_name, f_ext = os.path.splitext(file)
        return f_name

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

    def performDiffer(self, file1, file2):

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
                    unalignedList.append(unaligned)

            else:
                # u suprotnom, eval je xml, poredi se on sa originalnim tekstom
                taglessEval = self.stripTags(dirr, "/to_eval/", ev).splitlines(keepends=True)
                text = self.stripTags(dirr, "/text/", txt).splitlines(keepends=True)
                unaligned = self.performDiffer(taglessEval, text)
                if unaligned:
                    unalignedList.append(unaligned)

        return unalignedList

    def getLines(self, lines):
        ln = ""
        for i, line in enumerate(lines):
            if line[0] in ("+", "-"):
                ln = ln + line + "\n"
        return ln

    def createLogFile(self, unaligned):

        text = """******************************************************
        Following files are excluded from analysis because they don't align properly. 
        You can find exact lines in which two files mismatch. 
        Minus and plus signs represent lines that are unique in file1 and file2 respectively. 
        Such lines should be aligned manually.\n******************************************************\n\n\n"""
        with open("unalignedFilesLog.txt", "a", encoding="utf-8") as file:
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
                if name1 == gl or name2 == ev:
                    gold.pop(i)
                    eval.pop(i)
                    text.pop(i)
                else:
                    aligned.append([gl, ev, txt])

        return aligned


class Report(Annotation):
    gold = []
    eval = []
    text = []
    dir = ''
    goldDir = ''
    evalDir = dir + '/to_eval/'
    textDir = dir + '/text/'

    def __init__(self, files, dir):

        for i, (gl, ev, txt) in enumerate(files):
            self.gold.append(gl)
            self.eval.append(ev)
            self.text.append(txt)

        self.dir = dir
        self.goldDir = self.dir + '/gold/'
        self.evalDir = self.dir + '/to_eval/'
        self.textDir = self.dir + '/text/'

    def analyze(self):

        # generating data for analysis
        for i, (gld, evl, txt) in enumerate((zip(self.gold, self.eval, self.text))):

            with open(self.goldDir + gld, 'r', encoding='utf-8') as gl, open(self.evalDir + evl, 'r',
                                                                             encoding='utf-8') as ev, open(
                self.textDir + txt, 'r', encoding='utf-8') as tx:

                if (gld[-3:] == "xml"):
                    gold = self.generateAnn(gl.read())

                else:
                    gold = gl.readlines()

                if (evl[-3:] == "xml"):
                    eval = self.generateAnn(ev.read())

                else:
                    eval = ev.readlines()

                text = tx.read()

            # quantitative analysis
            tpStrong = 0
            tpWeak = 0

            for i, (gl, ev, tx) in enumerate((zip(gold, eval, text))):
                tpStrong = tpStrong + self.countTPstrong(ev, gl)
                tpWeak = tpWeak + self.countTPWeak(ev, gl)

            fpStrong = self.countFPstrong(eval, gold)
            fpWeak = fpStrong - (tpWeak - tpStrong)
            fn = self.countFN(eval, gold)

            strongPrecision = tpStrong / (tpStrong + fpStrong)
            weakPrecision = tpWeak / (tpWeak + fpWeak)
            strongRecall = tpStrong / (tpStrong + fn)
            weakRecall = tpWeak / (tpWeak + fn)
            strongf1 = 2 * strongPrecision * strongRecall / (strongPrecision + strongRecall)
            weakf1 = 2 * weakPrecision * weakRecall / (weakPrecision + weakRecall)

            # generate output of quantitative analysis
            print("TP strong: ", tpStrong)
            print("TP weak: ", tpWeak)
            print("FP strong: ", fpStrong)
            print("FP weak: ", fpWeak)
            print("FN: ", fn)

            print('strong precision: %.3f' % strongPrecision)
            print('weak precision: %.3f' % weakPrecision)
            print('strong recall: %.3f' % strongRecall)
            print('weak recall: %.3f' % weakRecall)
            print('strong F1: %.3f' % strongf1)
            print('weak F1: %.3f' % weakf1)

        return True

    def countTPstrong(self, eval, gold):

        if (eval.split(None, 4)[1:] == gold.split(None, 4)[1:]):
            return 1

        return 0

    def countTPWeak(self, eval, gold):

        ev = eval.split(None, 4)
        gl = gold.split(None, 4)

        evRange = set(range(int(ev[2]), int(ev[3]) + 1))
        glRange = set(range(int(gl[2]), int(gl[3]) + 1))

        if evRange.intersection(glRange):
            return 1

        return 0

    def countFPstrong(self, eval, gold):

        check = 0
        count = 0
        for ev in eval:
            for gl in gold:
                if (ev.split(None, 4)[1:] != gl.split(None, 4)[1:]):
                    check = 0
                else:
                    check = 1
                    break
            if (check == 0):
                count = count + 1

        return count

    def countFN(self, eval, gold):

        check = 0
        count = 0
        wrongLabel = 0
        for gl in gold:
            for ev in eval:

                if (ev.split(None, 4)[1:] != gl.split(None, 4)[1:]):
                    check = 0
                else:
                    check = 1
                    break
            if (check == 0):
                count = count + 1

        for gl in gold:
            for ev in eval:

                if (ev.split(None, 4)[1] != gl.split(None, 4)[1] and ev.split(None, 4)[2:] == gl.split(None, 4)[2:]):
                    wrongLabel = wrongLabel + 1

        return count - wrongLabel
