"""
Plots the survey response to a given question (indicator) number
on a map of India

REQUIRES:
    ../DATA/NFHS5.csv          : see NFHS5.py


EXAMPLE USAGE:
Plot the survey response to Question 57 for each district
on a map of India
> python3 plotMap 57


AUTHOR
Kalyani Nagaraj
May 2022
"""


import geopandas
import folium
import pickle
import sys

nfhs5_districts=geopandas.read_file("../DATA/nfhs5_districts.shp")
with open('../DATA/questions.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    questions = pickle.load(f)

with open('../DATA/is_bigger_greener.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    is_bigger_greener = pickle.load(f)

colormaps = ['YlOrBr', 'YlGn']

# Statistics (or, questions) to map
q2m = [int(i) for i in sys.argv[1:]]

for i in q2m:
    qlabel = questions[i]
    qcolname = 'Q'+str(i)+'_NFHS5'
    if qcolname in nfhs5_districts.columns:
        print("Generating map for Q", str(i))
        tfcolname = 'TF_'+'Q'+str(i)
        fname = 'Q'+str(i)+'.html'
   
        m = nfhs5_districts.explore(
               column=qcolname, 
               cmap=colormaps[is_bigger_greener[i]],
               tooltip = False, #or same as popup
               popup = ["State", "District", qcolname, tfcolname],
               legend_kwds = dict(caption=qlabel),
               popup_kwds = dict(aliases = ["State", "District", qlabel, "From NFHS-5 Report?"],\
                                          style=("background-color: grey; color: white; font-family: courier new; font-size: 14px; padding: 10px;")), # pass a string to style; string uses HTML syntax 
               style_kwds=dict(stroke=False) # use no outline
        )  
        folium.LayerControl().add_to(m)
        m.save("../MAPS/"+fname)


