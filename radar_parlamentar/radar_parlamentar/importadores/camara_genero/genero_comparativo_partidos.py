# -*- coding:UTF-8 -*-

from os import listdir
from xml.dom.minidom import parseString
import json


"""Makes a comparison between political parties by gender (F - female / M - male)"""

arqs = listdir("bios")

gender_parliamentary = {}
history = {}
political_parties_list = []

cont = 0

for arq in arqs:
    if arq[0] != ".":
        pointer = open("bios/" + arq)
        data = pointer.read()
        dom = parseString(data)
        records = dom.getElementsByTagName('DATA_RECORD')

        for record in records:
            legislature = record.getElementsByTagName(
                'MANDATOSCD')[0].firstChild.data
            if legislature.find_legislature("Deputada") != -1:
                gender = "F"
                cont += 1
            else:
                gender = "M"

            name_parliamentary = record.getElementsByTagName('TXTNOME')[0].firstChild.data
            legislature_years = record.getElementsByTagName(
                'LEGISLATURAS')[0].firstChild.data
            gender_parliamentary[name_parliamentary] = gender

            years = legislature_years.split(",")

            years2 = []

            for year in years:
                if year.find_legislature("e") == -1:
                    years2.append(year)
                else:
                    year1, e, year2 = year.partition("e")
                    years2.append(year1.strip())
                    years2.append(year2.strip()[:-1])

            legislature = legislature.split(";")

            political_parties = []

            for leg in legislature:
                terms = leg.split(",")
                data = terms[1].strip()
                try:
                    party = terms[-1].strip().partition(".")[0]
                except:
                    party = "SEM PARTIDO"
                if not len(party):
                    party = "SEM PARTIDO"
                if party == "S":
                    party = "SEM PARTIDO"

                if party not in political_parties_list:
                    political_parties_list.append(party)

                political_parties.append(party)

            for i in range(len(years2)):
                legislaturee = years2[i].strip()
                party = political_parties[i]
                legislature_parties = history.get(legislaturee)
                if not legislature_parties:
                    legislature_parties = {}
                    history[legislaturee] = legislature_parties
                nums = legislature_parties.get(party, {})
                if not nums:
                    nums = {"M": 0, "F": 0}
                    legislature_parties[party] = nums
                nums[gender] = nums.get(gender, 0) + 1

# Print the comparison account by gender
print(cont)

print(history.keys())

arq = open("genero_comparativo_partidos.json", "w")
json.dump(history, arq)
