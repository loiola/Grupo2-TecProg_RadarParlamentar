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
                genero = "F"
                cont += 1
            else:
                genero = "M"

            name_parliamentary = record.getElementsByTagName('TXTNOME')[0].firstChild.data
            legislature_years = record.getElementsByTagName(
                'LEGISLATURAS')[0].firstChild.data
            gender_parliamentary[name_parliamentary] = genero

            anos = legislature_years.split(",")

            anos2 = []

            for ano in anos:
                if ano.find_legislature("e") == -1:
                    anos2.append(ano)
                else:
                    ano1, e, ano2 = ano.partition("e")
                    anos2.append(ano1.strip())
                    anos2.append(ano2.strip()[:-1])

            legislature = legislature.split(";")

            political_parties = []

            for leg in legislature:
                termos = leg.split(",")
                data = termos[1].strip()
                try:
                    partido = termos[-1].strip().partition(".")[0]
                except:
                    partido = "SEM PARTIDO"
                if not len(partido):
                    partido = "SEM PARTIDO"
                if partido == "S":
                    partido = "SEM PARTIDO"

                if partido not in political_parties_list:
                    political_parties_list.append(partido)

                political_parties.append(partido)

            for i in range(len(anos2)):
                legislatura = anos2[i].strip()
                partido = political_parties[i]
                legis_partidos = history.get(legislatura)
                if not legis_partidos:
                    legis_partidos = {}
                    history[legislatura] = legis_partidos
                nums = legis_partidos.get(partido, {})
                if not nums:
                    nums = {"M": 0, "F": 0}
                    legis_partidos[partido] = nums
                nums[genero] = nums.get(genero, 0) + 1

# Print the comparison account by gender
print(cont)

print(history.keys())

arq = open("genero_comparativo_partidos.json", "w")
json.dump(history, arq)
