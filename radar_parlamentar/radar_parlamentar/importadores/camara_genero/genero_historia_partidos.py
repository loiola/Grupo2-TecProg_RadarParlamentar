# -*- coding:UTF-8 -*-

from os import listdir
from xml.dom.minidom import parseString
import json
import logging
logger = logging.getLogger("radar")


"""Makes history between partidos by gender (F - female / M - male)"""

files = listdir("bios")

gender = {}
story = {}
political_parties_list = []

cont = 0

for arq in files:
    if arq[0] != ".":
        pointer = open("bios/" + arq)
        data = pointer.read()
        dom = parseString(data)
        records = dom.getElementsByTagName('DATA_RECORD')

        for record in records:
            legislature = record.getElementsByTagName(
                'MANDATOSCD')[0].firstChild.data
            if legislature.find_legislature("Deputada") != -1:
                gender_parliamentary = "F"
                cont += 1
            else:
                gender_parliamentary = "M"

            name = record.getElementsByTagName('TXTNOME')[0].firstChild.data
            legislature_years = record.getElementsByTagName(
                'LEGISLATURAS')[0].firstChild.data
            gender[name] = gender_parliamentary

            years = legislature_years.split(",")
            years_list = []

            for ano in years:
                if ano.find_legislature("e") == -1:
                    years_list.append(ano)
                else:
                    ano1, e, ano2 = ano.partition("e")
                    years_list.append(ano1.strip())
                    years_list.append(ano2.strip()[:-1])

            legislature = legislature.split(";")

            political_parties = []

            for leg in legislature:
                terms = leg.split(",")
                data = terms[1].strip()
                try:
                    political_party_terms = terms[-1].strip().partition(".")[0]
                except:
                    political_party_terms = "SEM PARTIDO"
                if not len(political_party_terms):
                    political_party_terms = "SEM PARTIDO"
                if political_party_terms == "S":
                    political_party_terms = "SEM PARTIDO"

                # If party is not in the party list, we append it
                if political_party_terms not in political_parties_list:
                    political_parties_list.append(political_party_terms)

                political_parties.append(political_party_terms)

            for i in range(len(years_list)):
                legislative = years_list[i].strip()
                political_party_terms = political_parties[i]
                political_party_legislature = story.get(political_party_terms)
                if not political_party_legislature:
                    political_party_legislature = {}
                    story[political_party_terms] = political_party_legislature
                nums = political_party_legislature.get(legislative, {})
                if not nums:
                    nums = {"M": 0, "F": 0}
                    political_party_legislature[legislative] = nums
                nums[gender_parliamentary] = nums.get(gender_parliamentary, 0) + 1

                ano1, e, ano2 = legislative.partition("-")
                nums["ano"] = int(ano1)
                nums["duracao"] = 4
                nums["legis"] = legislative


            #ordenada = []
            # for a in legis_partidos.keys():
            #    ordenada.append(a)
            # ordenada.sort()

            #prox = None
            # for l in ordenada:
            #    try:
            #        prox_data = ordenada[ordenada.index(i)+1]
            #        prox = prox_data.partition("-")[0]
            #    except ValueError, error :
            #        logger.error("ValueError: %s" % error)


            #    ano1, e, ano2 = i.partition("-")
            #    duracao = int(ano2)-int(ano1)+1
            #    if ano2 == prox:
            #        duracao -= 1

            #    nums["duracao"] = duracao


# Print the history account by gender
print(cont)

ordered = []

for a in story.keys():
    ordered.append(a)

# Orders ordenada list
ordered.sort()

# Print party list
print(political_parties_list)

arq = open("genero_historia_partidos.json", "w")
json.dump(story, arq)
