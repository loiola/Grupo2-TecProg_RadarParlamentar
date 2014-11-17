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


# Modifiable parameters
# Political partidos to be included in the analyzes
#
# Receives the list of political partidos to be included in the analysis
parties = [u'PMDB', u'PTB', u'PDT', u'PT', u'DEM', u'PCdoB', u'PSB', u'PSDB',
	u'PSC', u'PMN', u'PPS', u'PV', u'PTdoB', u'PP', u'PHS', u'PRB', u'PSOL', 
	u'PR', u'PSD']

# Receives the initial year of analysis equal to 2012
initial_year = 2002

# Receives the final year of analysis equal to 2011
final_year = 2011

# Receives a txt file in which data is stored
output_file = 'colar_num_html.txt'
 
# Algorithm:  
# List of objects like Analysis (that will be analisis anunual):
annual_list = []

# Receives list of years of analysis (2012-2011)
years = range(initial_year,final_year+1)

# Make PCAs:
for year in years:
    annual_list.append(analise.Analysis(str(year)+'-01-01', str(year)+'-12-31', [],
                                  parties))

# Receives the PCA list of data
data = []

# annual: Temporary loop variable in the list which includes data PCA
print "Fazendo PCAs:"
print '-'*(len(annual_list)-1)+'v'
for annual in annual_list:
    data.append(annual.do_coordinates_2d_of_political_parties('/dev/null'))
    sys.stdout.write('.')
    sys.stdout.flush()


# Auxiliary functions:
def movement_amount(i,graus=0,espelho=0):
<<<<<<< HEAD
    """Calculates the amount of movement between the instant i (corresponding
    to the year years [i]) and the time i + 1.
     When calculating the time i has the rotated axes (degree value between 0
     and 360) and the first axis multiplied by -1 if the mirror = 0."""
=======
    """ Calculates the amount of movement between the instant i (corresponding 
	to the year years [i]) and the time i + 1.
     When calculating the time i has the rotated axes (degree value between 0
	and 360) and the first axis multiplied by -1 if the mirror = 0."""

>>>>>>> estilo-e-design

    # Receives the amount of movement between two instants (i and i + 1)
    moviment_amount = 0

    # Receives a list of existing data before applying the movement amount
    before = data[index]

    # Receives a list of existing data after applying the movement amount
    after = data[index+1]

    if espelho:
        before = numpy.dot( before,numpy.array( [[-1.,0.],[0.,1.]] ) )

    elif degrees != 0:
        before = numpy.dot( before,matrot(degrees) )

    # j: temporary variable of the quantidade_movimento() method loop
    for j in range(len(parties)):
        moviment_amount += numpy.sqrt( numpy.dot( before[j,:] - after[j,:],  before[j,:] - \
                                     after[j,:] ) ) * annual_list[index+1].tamanho_partido[j]
    return moviment_amount

def matematic_rotation(graus):
<<<<<<< HEAD
   """Returns 2x2 rotation that rotates the axes in degrees (0-360) in
   counterclockwise array (as if the points spun clockwise around fixed axes)."""
=======
   """ Returns 2x2 rotation that rotates the axes in degrees (0-360) in
   counterclockwise array (as if the points spun clockwise around fixed axes)."""

>>>>>>> estilo-e-design

   # Receives the value of the angle in degrees to make the rotation in the graphic
   # data
   degrees = float(degrees)

   # Receives the value in radians calculated starting from the value of the angle in
   # degrees
   radian = numpy.pi * degrees/180.

   # Receives the value of cosine of angle in rad
   cosine_of_radian = numpy.cos(radian)

   # Receives the value of sin of angle in rad
   sin_of_radian = numpy.sin(radian)

   return numpy.array([[cosine_of_radian,-sin_of_radian],
                       [sin_of_radian,cosine_of_radian]])


print ' '
print 'Espelhando e rotacionando...'


# Indices of years, backwards:
for index in range(len(years)-2,-1,-1):
    print years[index]

    # Minimizing the amount of motion
    # Receiving the minimum value of the amount of movement equal to 1000000
    minimum_quantity_amount = 1000000

    # Mirror, degrees:
    champion = (0,0)

    for espelhar in [0,1]:
        for degrees in [0,45,90,135,180,225,270,315]:
            current_moviment_amount = quantidade_movimento(index,degrees,espelhar)

            #print '%d, %d, %f' % (espelhar,graus,qm_agora )
            if current_moviment_amount < minimum_quantity_amount:
                champion = (espelhar, degrees)
                minimum_quantity_amount = current_moviment_amount

    print champion

    if champion[0] == 1:

        # Mirror:
        data[index] = numpy.dot( data[index], numpy.array([[-1.,0.],[0.,1.]]) )

    if champion[1] != 0:

        # Rotate:
        data[index] = numpy.dot( data[index], matrot(champion[1]) )

print 'Fim'

# Writing file
# Receives opening of the output file
open_file = open(output_file,'w')
open_file.write("""<script type="text/javascript" src="http://www.google.com/jsapi">
    </script><script type="text/javascript">
    google.load('visualization', '1', {packages: ['motionchart']});

    function drawVisualization() { """)

open_file.write('var data = new google.visualization.DataTable();\n')
open_file.write("data.addColumn('string', 'PoliticalParty');\n")
open_file.write("data.addColumn('date', 'Data');\n")
open_file.write("data.addColumn('number', 'Eixo1');\n")
open_file.write("data.addColumn('number', 'Eixo2');\n")
open_file.write("data.addColumn('number', 'Tamanho');\n")
open_file.write("data.addRows([\n")

for annual_index in range(len(annual_list)):

    # Receives the annual index from the annual list
    annual = annual_list[annual_index]

    # Receives the final year from annual index in annual
    date_year = int(annual.data_final[0:4])

    # Receives the final month from annual index in annual
    date_month = int(annual.data_final[5:7])-1

    # Receives the final day from annual index in annual
    date_day = int(annual.data_final[8:10])

    for party_index in range(len(parties)):
        line = "  ['%s',new Date(%d,%d,%d), %f,%f,%d],\n" % (parties[party_index],date_year,
                                                             date_month,date_day,
                                                              data[annual_index][party_index,0],
                                                              data[annual_index][party_index,1],
                                                              annual.tamanho_partido[party_index])

        open_file.write(line)

open_file.seek(-2,1)
open_file.write("\n]);")
open_file.write("""
      var motionchart = new google.visualization.MotionChart(
          document.getElementById('visualization'));


      var options = {};
      options['state'] = '{"yAxisOption":"3","xLambda":1,"colorOption":"_UNIQUE_COLOR",
      "playDuration":40000,"showTrails":false,"iconKeySettings":[],"xAxisOption":"2",
      "nonSelectedAlpha":0.4,"uniColorForNonSelected":false,"xZoomedDataMax":0.815577,
      "sizeOption":"4","orderedByY":false,"iconType":"BUBBLE","dimensions":{"iconDimensions":
      ["dim0"]},"yZoomedDataMax":0.907421,"orderedByX":false,"xZoomedIn":false,
      "xZoomedDataMin":-0.510363,"time":"2002-12-31","duration":{"timeUnit":"D",
      "multiplier":1},"yLambda":1,"yZoomedIn":false,"yZoomedDataMin":-0.558064}'
      options['width'] = 800;
      options['height'] = 500;


      motionchart.draw(data, options);

    }

    google.setOnLoadCallback(drawVisualization);
  </script>


<div id="visualization" style="width: 800px; height: 400px;"></div> """)




open_file.close_tag()

