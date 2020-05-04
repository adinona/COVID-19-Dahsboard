from __future__ import print_function
import geopandas as gpd
import pandas as pd
import json
from bokeh.io import output_notebook, show, output_file, save
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer
from bokeh.io import curdoc, output_notebook
from bokeh.models import Slider, HoverTool,TableColumn, DataTable, Slider,ColumnDataSource,CustomJS
from bokeh.layouts import widgetbox, row, column
from bokeh.plotting import figure
from bokeh.models.widgets import Select

from bokeh.embed import components

from bokeh.embed import json_item
from bokeh.resources import CDN as CDN
from bokeh.sampledata.iris import flowers
import copy
from flask import Flask, render_template, request

from jinja2 import Template
from flask_bootstrap import Bootstrap







app = Flask(__name__)

dashboard = "/Users/Aditya/Desktop/project/"






def createDataTables():
	pd.options.display.float_format = '{:,.0f}'.format

	datafile = '/Users/Aditya/Desktop/project/output.csv'

	dfDataTable = pd.read_csv(datafile, names = ['Country','Deaths','Deaths /1M pop','New Deaths','Tests','EstimatedCases','Confirmed Cases',
		'Confirmed Case/Fatality Rate','Confirmed Cases/1M pop','Seasonal Flu Deaths (CDC/WHO 2017)'], skiprows = 2)

	dfDataTable.fillna('No data', inplace = True)


	table1 = dfDataTable[["Country","Tests","Confirmed Cases"]].copy()
	table2 = dfDataTable[["Country","Deaths","Seasonal Flu Deaths (CDC/WHO 2017)"]].copy()
	table1Html = table1.to_html(index = False, justify = 'center', classes ="table")
	table2Html = table2.to_html(index = False, justify = 'center', classes ="table")
	

	return table1Html,table2Html








def createMap():

	shapefile = '/Users/Aditya/Desktop/project/ne_110m_admin_0_countries.shp'
	datafile = '/Users/Aditya/Desktop/project/output.csv'



	#Read shapefile using Geopandas
	gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
	#Rename columns.
	gdf.columns = ['country', 'country_code', 'geometry']
	#Drop row corresponding to 'Antarctica'
	gdf.at[43, 'country'] = "French Guiana"

	#drop antartica, takes too much space
	gdf = gdf.drop(gdf.index[159])



	#Read csv file using pandas

	


	df = pd.read_csv(datafile, names = ['Country','Deaths','Deaths /1M pop','New Deaths','Tests','Confirmed Cases','Confirmed Case/Fatality Rate',
		'Confirmed Cases/1M pop','EstimatedCases','Seasonal Flu Deaths1(CDC/WHO 2017)'], skiprows = 2)
	merged = gdf.merge(df, left_on = 'country', right_on = 'Country', how = 'left')
	merged.fillna('No data', inplace = True)


	#Read data to json.
	merged_json = json.loads(merged.to_json())
	#Convert to String like object.
	json_data = json.dumps(merged_json)


	#Input GeoJSON source that contains features for plotting.
	geosource = GeoJSONDataSource(geojson = json_data)

	#Define a sequential multi-hue color palette.
	palette = brewer['YlOrRd'][7]

	#Reverse color order so that dark blue is highest obesity.
	palette = palette[::-1]

	#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
	color_mapper = LinearColorMapper(palette = palette, low = 0, high = 350, nan_color = '#d9d9d9')

	#Define custom tick labels for color bar.
	tick_labels = {'0': '0', '50': '50', '100':'100', '150':'150', '200':'200', '250':'250', '300':'300','350':'>350'}

	#Add hover tool
	hover = HoverTool(tooltips = [ ('Country','@country'),('Deaths /1M pop', '@{Deaths /1M pop}')])

	#Create color bar. 
	color_bar = ColorBar(color_mapper=color_mapper, label_standoff=9,width = 20, height = 500,
	border_line_color=None,location = (0,0), orientation = 'vertical', major_label_overrides = tick_labels, background_fill_color = "#1e1e2f" ,
	major_label_text_color = "white")

	#Create figure object.
	p = figure(title = 'Deaths per Million', plot_height = 550 , plot_width = 950, toolbar_location = None, tools = [hover])
	p.title.text_color = "white"
	p.xgrid.grid_line_color = None
	p.ygrid.grid_line_color = None
	p.background_fill_color = "#3690c0"
	p.border_fill_color = "#1e1e2f"
	p.axis.visible = False

	#Add patch renderer to figure. 
	p.patches('xs','ys', source = geosource,fill_color = {'field' :'Deaths /1M pop', 'transform' : color_mapper},
	          line_color = 'black', line_width = 0.25, fill_alpha = 1)

	#Specify figure layout.
	p.add_layout(color_bar, 'right')

	script, div = components(p)

	#Display figure.
	save(p)
	return p

def getGlobalNums(datafile):

	globalDF = pd.read_csv(datafile, names = ['Country','Deaths','Deaths /1M pop','New Deaths','Tests','Confirmed Cases',
		'Confirmed Case/Fatality Rate','Confirmed Cases/1M pop','EstimatedCases','Seasonal Flu Deaths1(CDC/WHO 2017)'],nrows=2)
	globalDF.fillna('No data', inplace = True)
	data = globalDF.iloc[1]
	globalNums = []
	for x in data:
		if x != "No data" and (x != 'Total Global Deaths'):
			globalNums.append(int(float((x))))
	return globalNums

@app.route('/')
def index():

	datafile = '/Users/Aditya/Desktop/project/output.csv'

	plot = createMap()
	table1, table2  = createDataTables()
	script, div = components(plot)
	globalNums = getGlobalNums(datafile)

	

	return render_template("index.html", script=script, div=div,globalD=globalNums[0],globalC = globalNums[1],
		table1 = table1, table2=table2)

if __name__== "__main__":

	app.run()


