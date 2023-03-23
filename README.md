# DiffCompare -- A web tool for comparing annotations in XML, standoff (ann) and CoNLL-2002 format


DiffCompare is an online tool for evaluating named entity recognition models. It provides quantitative (precision, recall and F1) and qualitative (visualization) data analysis.

The input data should be prepared in a zip file, with the structure defined below. 

The user can enter the classes of entities for which they want to see a visual representation of the results of the model operation. Each class the user enters should be separated with a comma (for example, "PERS, ORG, LOC" or "PERS,ORG,LOC" are both fine entries)

![slika](https://user-images.githubusercontent.com/49460346/227198103-8dd2b1e8-535e-43fc-92b9-b1df8a369529.png)

The input data is divided into two groups: the gold standard and the evaluation standard. Data can be in standoff (ann), XML and CoNLL-2002 format.
Additionally, if a gold standard or evaluation standard file is in standoff or XML format, a third group of input data needs to be included: text files. 
The third group of data is required for testing whether the content of the unannotated text is identical in all groups of input data, which is a prerequisite for correct analysis.

Text files are also required for cases where both gold and evaluation standards are in standoff format, in order to obtain qualitative analysis. 
If both files are in standoff format, and the output files for visualization show incorrect information, the problem is probably mismatched information in the input data, and such files need to be further analyzed and corrected.
In case of a mismatch, the user receives information about the exact lines in which there are differences, in the form of a log file that can be downloaded or opened via link. Unmatched files will be excluded from the analysis.
 
![slika](https://user-images.githubusercontent.com/49460346/227199498-1fe29d6b-8a45-4097-a1d1-57c98ff740cd.png)
 
If it is determined that the files completely match, but are still excluded from the analysis, there is a possibility that they are encoded differently, which should be corrected. A different encoding usually causes a log file entry like the image below, where the first line is shown to be different:

![slika](https://user-images.githubusercontent.com/49460346/227199549-7ed27df5-d259-4b23-afc2-fdff08ed4083.png)

While for standoff and XML format it is possible to combine input files, with CoNLL-2002 format, the gold standard file and its counterpart in the evaluation standard must be CoNLL-2002. In that case, the text file is not needed.

Input files should be in *.zip, with folders named gold, to_eval and, if necessary, text. Below is an example of a properly structured directory:
 
 ![slika](https://user-images.githubusercontent.com/49460346/227199586-1cc6f316-421c-4fed-866f-9de8aaab389e.png)

The requirement for all formats is that the files of each group (gold, to_eval , text) have the same name as their counterparts in other groups.

![slika](https://user-images.githubusercontent.com/49460346/227199643-978ba575-2156-41f4-9497-dba133e208ff.png)

The user can obtain quantitative and qualitative data through the link, and has the option to download the data. The downloaded data will also contain a log file with information about unaligned files.
 
 ![slika](https://user-images.githubusercontent.com/49460346/227199672-b0bd9a1e-7361-4e7b-b5de-59f5941c794a.png)

It is necessary to set the path on the server so that access to the output files is possible via a link.

Images below show example of output data

