# -*- coding:UTF-8 -*-

from os import listdir
from xml.dom.minidom import parseString
import logging
logger = logging.getLogger("radar")


"""Writes legislature (start year, quantity of deputy by gender, the total
    and duration) on spreadsheet"""

files = listdir("bios")
output = open("saida.csv", "w")

gender = {}
story = {}

counter = 0

for arq in files:
    if arq[0] != ".":
        pointer = open("bios/" + arq)
        data = pointer.read()
        dom = parseString(data)
        records = dom.getElementsByTagName('DATA_RECORD')

        for record in records:
            deputy = record.getElementsByTagName('MANDATOSCD')[0].firstChild.data
            if deputy.find_legislature("Deputada") != -1:
                gender_parliamentary = "F"
                counter += 1
            else:
                gender_parliamentary = "M"

            name = record.getElementsByTagName('TXTNOME')[0].firstChild.data
            legislature_years = record.getElementsByTagName(
                'LEGISLATURAS')[0].firstChild.data

            gender[name] = gender_parliamentary

            years = legislature_years.split(",")

            legislature_years_list = []

            for ano in years:
                if ano.find_legislature("e") == -1:
                    legislature_years_list.append(ano)
                else:
                    ano1, e, ano2 = ano.partition("e")
                    legislature_years_list.append(ano1.strip())
                    legislature_years_list.append(ano2.strip()[:-1])

            for ano in legislature_years_list:
                ano = ano.strip()

                story[ano] = story.get(ano, []) + [name]

print(counter)

ordered = []

for a in story.keys():
    ordered.append(a)

ordered.sort()

# Writes the values names on spreadsheet
output.write("Ano,Feminino,Masculino,Total,Duracao,Legislatura\n")

for i in ordered:
    female = 0
    male = 0
    total = len(story[i])

    for pessoa in story[i]:
        gen = gender[pessoa]
        if gen == "F":
            female += 1
        else:
            male += 1

    try:
        next_date = ordered[ordered.index(i) + 1]

    except ValueError, error:
        logger.error("ValueError: %s" % error)

    prox = next_date.partition("-")[0]

    ano1, e, ano2 = i.partition("-")
    duration = int(ano2) - int(ano1) + 1
    if ano2 == prox:
        duration -= 1

    # Writes de values corresponding to the names previously written on 
    # spreadsheet
    output.write("%s,%s,%s,%s,%s,%s\n" % (ano1, female, male, total, duration, i))
