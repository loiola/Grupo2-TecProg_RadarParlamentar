#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2012, Leonardo Leite, Saulo Trento, Diego Rabatone
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import numpy
import analise
import sys
 
# Modifiable parameters:
# Political parties to be included in the analyzes:

parts = [u'PMDB', u'PTB', u'PDT', u'PT', u'DEM', u'PCdoB', u'PSB', u'PSDB', u'PSC', u'PMN', u'PPS', u'PV', u'PTdoB', u'PP', u'PHS', u'PRB', u'PSOL', u'PR', u'PSD']

ano_inicial = 2002
ano_final = 2011

arquivo_de_saida = 'colar_num_html.txt'


 
# Algorithm:  
# Lista of objects like Analise (que serão análises anuais):     
anuais = [] 

anos = range(ano_inicial,ano_final+1)

# Make PCAs:
for ano in anos:
    anuais.append(analise.Analise(str(ano)+'-01-01', str(ano)+'-12-31', [], parts))

dados = []
print "Fazendo PCAs:"
print '-'*(len(anuais)-1)+'v'
for a in anuais:
    dados.append( a.partidos_2d('/dev/null') )
    sys.stdout.write('.')
    sys.stdout.flush()


# Auxiliary functions:
def quantidade_movimento(i,graus=0,espelho=0):
    """Calculates the amount of movement between the instant i (corresponding to the year years [i]) and the time i + 1.
     When calculating the time i has the rotated axes (degree value between 0 and 360) and the first axis multiplied by -1 if the mirror = 0."""

    qm = 0
    antes = dados[i]
    depois = dados[i+1]
    if espelho:
        antes = numpy.dot( antes,numpy.array( [[-1.,0.],[0.,1.]] ) )
    if graus != 0:
        antes = numpy.dot( antes,matrot(graus) )
    for j in range(len(parts)):
        qm += numpy.sqrt( numpy.dot( antes[j,:] - depois[j,:],  antes[j,:] - depois[j,:] ) ) * anuais[i+1].tamanho_partido[j]
    return qm

def matrot(graus):
   """Returns 2x2 rotation that rotates the axes in degrees (0-360) in counterclockwise array (as if the points spun clockwise around fixed axes).""" 
   
   graus = float(graus)
   rad = numpy.pi * graus/180.
   c = numpy.cos(rad)
   s = numpy.sin(rad)
   return numpy.array([[c,-s],[s,c]])


print ' '
print 'Espelhando e rotacionando...'


# Indices of years, backwards:
for i in range(len(anos)-2,-1,-1): 
    print anos[i]

    # Minimizing the amount of motion:
    qm_min = 1000000 

    # Mirror, degrees:
    campeao = (0,0) 
    for espelhar in [0,1]:
        for graus in [0,45,90,135,180,225,270,315]:
            qm_agora = quantidade_movimento(i,graus,espelhar)
            #print '%d, %d, %f' % (espelhar,graus,qm_agora )
            if qm_agora < qm_min:
                campeao = (espelhar, graus)
                qm_min = qm_agora
    print campeao
    if campeao[0] == 1: 

        # Mirror:
        dados[i] = numpy.dot( dados[i], numpy.array([[-1.,0.],[0.,1.]]) )
    if campeao[1] != 0: 

        # Rotate:
        dados[i] = numpy.dot( dados[i], matrot(campeao[1]) )

print 'Fim'

# Writing file:
f = open(arquivo_de_saida,'w')
f.write("""<script type="text/javascript" src="http://www.google.com/jsapi"></script>
  <script type="text/javascript">
    google.load('visualization', '1', {packages: ['motionchart']});

    function drawVisualization() {

""")
f.write('var data = new google.visualization.DataTable();\n')
f.write("data.addColumn('string', 'Partido');\n")
f.write("data.addColumn('date', 'Data');\n")
f.write("data.addColumn('number', 'Eixo1');\n")
f.write("data.addColumn('number', 'Eixo2');\n")
f.write("data.addColumn('number', 'Tamanho');\n")
f.write("data.addRows([\n")
for ia in range(len(anuais)): 
    a = anuais[ia]
    d_ano = int(a.data_final[0:4])
    d_mes = int(a.data_final[5:7])-1 
    d_dia = int(a.data_final[8:10])
    for ip in range(len(parts)): 
        linha = "  ['%s',new Date(%d,%d,%d), %f,%f,%d],\n" % (parts[ip],d_ano,d_mes,d_dia,dados[ia][ip,0],dados[ia][ip,1],a.tamanho_partido[ip])
        f.write(linha)
f.seek(-2,1)
f.write("\n]);")
f.write("""     
      var motionchart = new google.visualization.MotionChart(
          document.getElementById('visualization'));

      var options = {};
      options['state'] = '{"yAxisOption":"3","xLambda":1,"colorOption":"_UNIQUE_COLOR","playDuration":40000,"showTrails":false,"iconKeySettings":[],"xAxisOption":"2","nonSelectedAlpha":0.4,"uniColorForNonSelected":false,"xZoomedDataMax":0.815577,"sizeOption":"4","orderedByY":false,"iconType":"BUBBLE","dimensions":{"iconDimensions":["dim0"]},"yZoomedDataMax":0.907421,"orderedByX":false,"xZoomedIn":false,"xZoomedDataMin":-0.510363,"time":"2002-12-31","duration":{"timeUnit":"D","multiplier":1},"yLambda":1,"yZoomedIn":false,"yZoomedDataMin":-0.558064}'
      options['width'] = 800;
      options['height'] = 500;

      motionchart.draw(data, options);

    }
    

    google.setOnLoadCallback(drawVisualization);
  </script>

<div id="visualization" style="width: 800px; height: 400px;"></div>
""")
f.close()

