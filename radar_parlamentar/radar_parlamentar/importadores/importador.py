# -*- coding: utf-8 -*-
def main(list_legislative_houses):
    """Assigns importers to legislative houses and calls the function 
    that imports the data"""

    for legislative_house in list_legislative_houses:

        if legislative_house == 'conv':
            from importadores import conv as importador_convencao

            importador_convencao.main()

        elif legislative_house == 'cmsp':
            from importadores import cmsp as importador_cmsp

            importador_cmsp.main()

        elif legislative_house == 'sen':
            from importadores import sen as importador_senado

            importador_senado.main()

        elif legislative_house == 'cdep':
            from importadores import cdep as importador_camara

            importador_camara.main()

        else:
            print "Casa %s não encontrada" % legislative_house
