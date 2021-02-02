import argparse
import csv
import json
import math
from decimal import Decimal
import os





'''
    --> Lists the parameters to start the commandline program
        --> Everything is required 
'''
parser = argparse.ArgumentParser(description = 'Compiling CSVs into a complete JSON file')

parser.add_argument('-s', '--students', metavar='', required = True, type = str, help = "Enter the path to the students' csv file")

parser.add_argument('-c', '--courses', metavar='', required = True, type = str, help = "Enter the path to the courses csv file")

parser.add_argument('-t', '--tests', metavar='', required = True, type = str, help = "Enter the path to the test csv file")

parser.add_argument('-m', '--marks', metavar='', required = True, type = str, help = "Enter the path to the marks file")


args = parser.parse_args()


global missingKidsClassesDict
global numTestPerClass
global listClasses
global secondCounter
global coursesId
global individualStudentTestsTaken
global studentsIdA
global marksMarkA
global marksTestIdA
global testsWeightA
global testsCourseIdA
global testsTestIdA
global numTestsPerStudent
global numClassesPerStudent
global tempDict
global newInformationD

missingKidsClassesDict = {}
numTestPerClass = []
listClasses = {}
information = {}
courses = {}
coursesId = []
individualStudentTestsTaken = []




'''
    --> Finds the missing classes for the "incomplete" student
'''
def FindClass(testNotTakenArr) -> list:
    missedClassArr = []
    counter = 0
    for test in testsTestIdA:
        for testNotTake in testNotTakenArr:
            if test == testNotTake:
                if testsCourseIdA[counter] not in missedClassArr:
                    missedClassArr.append(testsCourseIdA[counter])
                else:
                    continue
        counter += 1
    
    return missedClassArr


'''
    --> Creates a dictionary for each "incomplete" student
        and the missing class(es)
'''
def CompileMissingStudentD(student, testsTakenArr):
    testNotTakenArr = []
    counter = 0
    for i in range(len(testsTestIdA)):
        if i > len(testsTakenArr) - 1:
            break
        if testsTestIdA[i] != testsTakenArr[i]:
            testNotTakenArr.append(testsTestIdA[i])
    missingKidsClassesDict[student] = FindClass(testNotTakenArr)

with open(args.courses, 'r') as coursesRef:
    coursesReader = csv.DictReader(coursesRef)
    for line in coursesReader:
        coursesId.append(line['id'])
        courseIdA = line['id']
        courses[courseIdA] = line

        



'''
    --> My labeling scheme for the entries are as follows:
        --> First portion comes from the file
        --> Second refers to the header
        --> Third refers to the variable type:
            --> A == List
            --> D == Dictionary
'''
with open(args.students, 'r') as studentsRef:
    studentsReader = csv.DictReader(studentsRef)
    studentsIdA = []
    
    for line in studentsReader:
        line.update(courses)
        studentId = line['id']
        information[studentId] = line
        studentsIdA.append(line['id'])



with open(args.marks, 'r') as marksRef:
    marksReader = csv.DictReader(marksRef)
    marksTestIdA = []
    marksMarkA = []
    marksStudentIdA = []
        
    for line in marksReader:
        marksMarkA.append(int(line['mark']))
        marksStudentIdA.append(line['student_id'])
        marksTestIdA.append(line['test_id'])



with open(args.tests, 'r') as testRef:
    testReader = csv.DictReader(testRef)
    testsTestIdA = []
    testsWeightA = []
    testsCourseIdA = []
    
    for line in testReader:
        testsCourseIdA.append(line['course_id'])
        testsWeightA.append(int(line['weight']))
        testsTestIdA.append(line['id'])





'''
    --> Figures out the students that don't have complete marks
    --> Appends those students in 'studentsWOCompletedMarks'
'''
frequencyCounter = 0
studentsWOCompletedMarks = []


for student in studentsIdA:
    for line in marksStudentIdA:
        if student == line:
            frequencyCounter += 1
    if frequencyCounter < len(testsWeightA):
        studentsWOCompletedMarks.append(student)
        frequencyCounter = 0
    elif frequencyCounter > len(testsWeightA):
        print('More marks were given than tests physically delivered')
        frequencyCounter = 0
    else:
        frequencyCounter = 0



    
'''
    --> Finds the tests that were taken by each each student without
        a full course load
    
    --> Then sends the student and the course load to a function
        --> The two functions create a dictionary for each
            "incomplete" student and their missing classes
'''
counter = 0
secondCounter = 0


for incompleteStudent in studentsWOCompletedMarks:
    for studentId in marksStudentIdA:
        if incompleteStudent == studentId:
            individualStudentTestsTaken.append(marksTestIdA[counter])
            counter += 1
        else: counter += 1
    CompileMissingStudentD(incompleteStudent, individualStudentTestsTaken)
    counter = 0





'''
    --> Finds the number of tests per class
'''
currentCourse = ''
counter = 0
previousIterCounter = 0
iterationCounter = 0


for courseIdA in testsCourseIdA:
    if(counter == 0):
        currentCourse = courseIdA
    counter += 1
    if(currentCourse == courseIdA):
        iterationCounter += 1
        
        if(iterationCounter <= previousIterCounter):
            numTestPerClass.append(previousIterCounter)
            if(counter == len(testsCourseIdA)):
                numTestPerClass.append(previousIterCounter)
            previousIterCounter = 0
        previousIterCounter = iterationCounter
    else:
        iterationCounter = 1
    currentCourse = courseIdA



            

'''
    --> At this point, all of the students have all the classes
        in the information dictionary
    --> This piece of code deletes the missing classes from
        the 'information' dictionary
'''
for mKey, mVal in missingKidsClassesDict.items():
    for element in mVal:
        del information[mKey][element]

        
for iKey, iVal in information.items():
    listClasses[iKey] = []
    for sKey, sVal in iVal.items():
        if type(sVal) == dict:
            listClasses[iKey].append(sVal)





'''
    --> Calculates the number of tests taken per student
'''
numTestsPerStudent = []
counter = 0
currentStudent = 1
end = len(marksStudentIdA) - 1


for i in range(len(marksStudentIdA)):
    if i == end:
        numTestsPerStudent.append(counter + 1)
    elif currentStudent == int(marksStudentIdA[i]):
        counter += 1
    else:
        numTestsPerStudent.append(counter)
        counter = 1
        currentStudent = int(marksStudentIdA[i])



    

'''
    --> Calculates the weighted values for all the marks given
    --> The weighted marks are stored in the 'weightedMarksA' list
'''
weightedMarksA = []
indexArr = []
counter = 0    
calcAverage = 0
sequentialBool = True


for key, val in listClasses.items():
    student = studentsIdA[int(key) - 1]
    if len(val) == len(coursesId):
        if sequentialBool == True:
            for weight in testsWeightA:
                calcAverage = marksMarkA[counter] * (weight * .01)
                calcAverage = round(calcAverage, 2)
                counter += 1
                weightedMarksA.append(calcAverage)
        else:
            for weight in testsWeightA:
                calcAverage = marksMarkA[currentIndex] * (weight * .01)
                calcAverage = round(calcAverage, 2)
                counter += 1
                weightedMarksA.append(calcAverage)
                currentIndex += 1
    else:
        sequentialBool = False
        if len(val) < len(coursesId):
            for key, val in missingKidsClassesDict.items():
                for missingClass in val:
                    for test in testsCourseIdA:
                        for index, mark in enumerate(marksStudentIdA):
                            if mark == student and test != missingClass and index not in indexArr:
                                indexArr.append(index)
                                currentIndex = indexArr[0]                
                    for i in range(len(testsCourseIdA)):
                        if testsCourseIdA[i] != missingClass:
                            calcAverage = marksMarkA[currentIndex] * (testsWeightA[i] * .01)
                            calcAverage = round(calcAverage, 2)
                            weightedMarksA.append(calcAverage)
                            currentIndex += 1                
            indexArr[:] = []
            
        else:
            print('Something seriously wrong happened')





'''    
    --> This block of code, after finding the weighted grades for each
        student, adds together the tests to calculate the final grade 
        in each class for each student
        
    --> This also accounts for those students with an incomplete course load
        --> Calculated in the outermost 'else'
'''
averagedClassTotalsA = []
total = 0
weightedIndex = 0


for studentIndex in range(len(studentsIdA)):
    if numTestsPerStudent[studentIndex] == len(testsTestIdA):
        for cours in range(len(numTestPerClass)):
            for test in range(numTestPerClass[cours]):
                total += weightedMarksA[weightedIndex]
                weightedIndex += 1
            averagedClassTotalsA.append(total)
            total = 0
    else:
        for key, val in missingKidsClassesDict.items():
            if key == studentsIdA[studentIndex]:
                for cours in range(len(numTestPerClass)):
                    for missedClass in val:
                        if cours != int(missedClass):
                            for tests in range(numTestPerClass[cours]):
                                total += weightedMarksA[weightedIndex]
                                weightedIndex += 1
                                total = round(total, 2)
                            averagedClassTotalsA.append(total)
                            total = 0





'''
    --> Calculates the number of classes taken per student
'''
numClassesPerStudent = []
counter = 0


for key, val in listClasses.items():
    counter = 0
    for x in val:
        counter += 1
    numClassesPerStudent.append(counter)





'''
    --> Appends the subkeys ('id', 'name', 'teacher')

    --> Appends the class values to another list to write as rows in the new CSV
'''
classKeys = []
tempList = []


for key, val in listClasses.items():
    for i in val:
        tempList.append(i)
        for x, y in i.items():
            if x not in classKeys:
                classKeys.append(x)





'''
    --> This creates a new CSV with all the class information ('id', 'name', 'teacher')
    
    --> This will allow me to have independent values with duplicate keys
        within the same dictionary
'''
with open('myfile.csv', 'w') as file:
    fileWriter = csv.DictWriter(file, fieldnames = classKeys)
    fileWriter.writeheader()
    fileWriter.writerows(tempList)





'''
    --> Loops through the newly created CSV ('myfile.csv')
        --> Adds the correct average to its respective class

    --> Appends each class with all the information into a list ('completedClassInfoA')

    --> The file is then deleted
'''
newInformationD = {}
completedClassInfoA = []


with open('myfile.csv', 'r') as file:
    fileReader = csv.DictReader(file)
    counter = 0
    for i in range(len(averagedClassTotalsA)):
        for line in fileReader:
            line['Class Average'] = averagedClassTotalsA[i]
            completedClassInfoA.append(line)
            break

os.remove('myfile.csv')





'''
    --> newInformationD has the students' id and name

    --> After some experimenting, I found that since newInformationD has been written to
        from a CSV file, one can add independent values to duplicating keys
'''
with open('students.csv', 'r') as studentsRef:
    studentsReader = csv.DictReader(studentsRef)
    
    
    for line in studentsReader:
        studentId = line['id']
        newInformationD[studentId] = line
        studentsIdA.append(line['id'])





'''
    --> First, for each student, a 'Total Average' key, value pair is created
        --> This will be used later in the code

    --> This section creates the list 'Courses'
        --> Appends the requisite classes to the respective
            'Courses' for each student

    --> Loops through newInformationD

    --> Loops through the class information (with the appropriate class averages)
        --> The loop would start over for every key thus thirdCounter was
            used to keep track of completedClassInfoA's current index
'''
counter = 0
secondCounter = 0
thirdCounter = 0
tripBool = False


for key, val in newInformationD.items():
    val['Total Average'] = 0
    val['Courses'] = []
    tripBool = False
    for i in range(len(completedClassInfoA)):
        if tripBool == True:
            continue
        if counter < numClassesPerStudent[secondCounter] - 1:
            val['Courses'].append(completedClassInfoA[thirdCounter])
            counter += 1
        else:
            counter = 0
            secondCounter += 1
            tripBool = True
            val['Courses'].append(completedClassInfoA[thirdCounter])
        thirdCounter += 1





'''
    --> Calculates the total average for each student

    --> Loops through each student, totals the averages, and sets
        it to 'Total Average' for each student
'''    
totalAverage = 0


for key, val in newInformationD.items():
    counter = 0
    totalAverage = 0
    for x in val['Courses']:
        counter += 1
        for k, v in x.items():
            if k == 'Class Average':
                totalAverage += v
    
    totalAverage = totalAverage / counter
    totalAverage = round(totalAverage, 2)
    val['Total Average'] = totalAverage





'''
    --> 'root' dictionary is created
    
    --> 'Students' key is created with an empty list as its value
        --> newInformationD is looped through and the values
            are appended to the 'Students' list
'''
root = {}
root['Students'] = []

for key, val in newInformationD.items():
    root['Students'].append(val)





'''
    --> Finally, the json file 'Compiled Information' is created
        written with 'root'
'''
with open('Compiled Information.json', "w") as jsonRef:
    jsonRef.write(json.dumps(root, indent = 4))
        
    
    
print('End')