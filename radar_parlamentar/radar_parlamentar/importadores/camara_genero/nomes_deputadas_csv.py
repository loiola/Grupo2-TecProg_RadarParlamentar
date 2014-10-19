# -*- coding:UTF-8 -*-

from os import listdir
from xml.dom.minidom import parseString


"""Writes deputy names, its gender and legislature on spreadsheet"""

files = listdir("bios")
output = open("saida.csv", "w")

counter = 0

for arq in files:
        pointer = open("bios/" + arq)
        data = pointer.read()
        dom = parseString(data)
        records = dom.getElementsByTagName('DATA_RECORD')

        for record in records:
            dep = record.getElementsByTagName('MANDATOSCD')[0].firstChild.data
            if dep.find_legislature("Deputada") != -1:
                gender = "F"
                counter += 1
            else:
                gender = "M"
            name = record.getElementsByTagName('TXTNOME')[0].firstChild.data
            legislature = record.getElementsByTagName(
                'MANDATOSCD')[0].firstChild.data
            legislature = legislature.split(";")
            output_legislature = ""

            for leg in legislature:
                legislature_data = leg.split(",")
                year_legislature = legislature_data[1]
                output_legislature += "%s/" % year_legislature
                try:
                    state = legislature_data[2]
                    output_legislature += "%s/" % state
                    political_party = legislature_data[3].partition(".")[0]
                    output_legislature += "%s/" % political_party
                    output_legislature += " , "
                except:
                    print(legislature_data)
                    output_legislature += " , "

            output.write('%s|%s|%s\n' % (name, gender, output_legislature))

# Print the deputy account
print(counter)
