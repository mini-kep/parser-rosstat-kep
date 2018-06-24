from collections import namedtuple

from pathlib import Path
from jinja2 import Environment, FileSystemLoader
#from weasyprint import HTML, CSS

import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as dates
matplotlib.style.use('ggplot')

import access    

def plot(df, title: str, minor_ticks, major_ticks):
    """
    Plot dataframe using title and ticks specification.
    """
    ax = df.plot(x_compat=True)           
    # set ticks
    ax.set_xticks(minor_ticks, minor=True)
    ax.xaxis.set_ticks(major_ticks, minor=False)
    ax.xaxis.set_major_formatter(dates.DateFormatter('%Y'))
    plt.gcf().autofmt_xdate(rotation=0, ha="center") 
    # other formatting
    plt.legend(loc="lower left")
    ax.set_title(title, loc='left', fontdict = {'fontsize': 11})
    return ax    


def plot_long(df, title, start=2005, end=2020, left_offset=1):
    df = df[df.index>=str(start)]
    minor_ticks = pd.date_range(str(start-left_offset), str(end), freq='YS')
    major_ticks = pd.date_range(str(start), str(end), freq='5YS') 
    return plot(df, title, minor_ticks, major_ticks)




# TODO: 
"""
  Plotting
  --------
  #a4: place charts on one A4 sheet and make PDF via html (Jinja/Weasyprint) see code below'

  #vt: variable transforms
  ---------------
  - accumulate CPI_rog to yoy
  - MA(12) smoothing 
  - % of GDP (at least annual)
    
"""

# NOT TODO NOW:
"""
  New charts
  ----------
  - seasonal adjustment/detrending 
  - additional 'latest value' chart
  - add comments/annoatations under header
  
  New data
  --------
  - add oil prices
  - parsing defintions
  
  Formatting
  -------------  
  - light blue background aka Seaborn
  - names in legend
  - same height on Y axis
"""


from ruamel.yaml import YAML
yaml = YAML()

doc = """
Валовый внутренний продукт (ВВП):    
   comment:       
       Comment text
       on 2 lines       
   charts:      
       - title: ВВП, темп прироста за 12 мес.
         names: GDP_yoy
       - title: Инвестиции, темп прироста за 12 мес.
         names: INVESTMENT_yoy

Выпуск:     
   comment:       
       Comment text
       on 2 lines       
   charts:    
       - title: Промышленное производство, темп прироста за 12 мес.
         names: INDPRO_yoy
       - title: Сельское хозяйство, темп прироста за 12 мес.
         names: AGROPROD_yoy

Цены:
   charts: 
       - names: CPI_rog
         title: Индекс потребительских цен (ИПЦ), в % пред.периоду
       - names: CPI_FOOD_rog, CPI_NONFOOD_rog, CPI_SERVICES_rog
         title: ИПЦ по компонентам, в % пред.периоду    
       

Дефицит(-)/профицит бюджета:    
   charts:     
       - names: GOV_SURPLUS_FEDERAL_bln_rub
         title: Федеральный бюджет, млрд.руб.
       - names: GOV_SURPLUS_SUBFEDERAL_bln_rub
         title: Региональные бюджеты, млрд.руб.

Внешняя торговля:    
   charts:     
       - names: EXPORT_GOODS_bln_usd, IMPORT_GOODS_bln_usd
         title: Экспорт и импорт товаров, млрд.долл.
       - names: TRADE_SURPLUS_bln_usd
         title: Сальдо торгового баланса, млрд.долл.
     
     
"""

Chart = namedtuple('Chart', 'names title')

def as_chart(d):
        title = d['title']
        names = [s.strip() for s in d['names'].split(',')]
        return Chart(names, title)

dfa, dfq, dfm = (access.get_dataframe(freq) for freq in 'aqm')
z = yaml.load(doc)   
rows_dict = {k: list(map(as_chart, v['charts'])) for k,v in z.items()}
print (rows_dict)
    
df = dfq
df['TRADE_SURPLUS_bln_usd'] = (df['EXPORT_GOODS_bln_usd'] 
                             - df['IMPORT_GOODS_bln_usd'])  
 

def filename(names):
    return f"{'_'.join(names)}.png"

def get_filename(chart: Chart):
    path = 'file:///C:/Users/%D0%95%D0%B2%D0%B3%D0%B5%D0%BD%D0%B8%D0%B9/Documents/GitHub/mini-kep/notebook/current/'
    return path + filename(chart.names)

# create png files
for header, charts in rows_dict.items():
    for chart in charts:
        plot_long(df[chart.names],
                  title=chart.title, 
                  start=2005)
        figname = filename(chart.names)
        plt.savefig(figname)

# create template parameters
plot_dicts = [dict(header=header,
              filenames=list(get_filename(c) for c in charts))    
              for header, charts in rows_dict.items()]

table_doc = """
{% for plot in plot_dicts %}

<div id="section_header">
{{plot['header']}}
</div>

<div id="images">
<img class="image" src="{{plot['filenames'][0]}}"></img>
<img class="image" src="{{plot['filenames'][1]}}"></img>
</div>

{% endfor %}
""" 

# DELETE: very sloppy code, dont do it this way
#<<<<<<< HEAD
#=======
#{% for topic in items.keys() %}
#{% set image0 = items[topic]['plot_0'] %}
#{% set image1 = items[topic]['plot_1'] %}
#{% if loop.index == 4 %}
#<div style="page-break-before: always" id="imageswithheader">
#{% else %}
#<div id="imageswithheader">
#{% endif %}
#{{topic}}
#<div id="images">
#<img class="rowimage" src="{{image0}}"></img>
#<img class="rowimage" src="{{image1}}"></img>
#>>>>>>> origin/dev-jinja




# NOT TODO: put me back

#{% if loop.index == 4 %}
#<div style="page-break-before: always" id="plot">
#{% else %}

 
template_doc = """<html>
<head lang="ru">
    <title>{{ page_header }}</title>
<style>
.rowimage {
    display: inline-block;
    margin-left: auto;
    margin-right: auto;
    height: 260px; 
}
  </style>
</head>
<body>
     %s
</body>
</html>""" % table_doc

Path('template.html').write_text(template_doc, encoding='utf-8')

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('template.html')

template_vars = {"page_header" : "Macroeconomic Charts",
                 "plot_dicts": plot_dicts
                 }

html_out = template.render(template_vars)
print(html_out)
Path('listing.html').write_text(html_out)
# FIXME: index.html not legible in firefox due to encoding issues  


# NOTE: weasyprint is not windows-compatible. msu yuse different pdf renderer
#HTML(string=html_out, base_url=os.path.dirname(os.path.abspath(__file__))).write_pdf("ts.pdf", stylesheets=[CSS(string='@page {size: Letter;  margin: 0.3in 0.3in 0.3in 0.3in;}')])


# alternatives documented at https://gist.github.com/philfreo/44e2e26a65820497db234d0c66ed58ae
# python: weasyprint or xhtml2pdf.pisa


from xhtml2pdf import pisa             # import python module

# Utility function
def convertHtmlToPdf(sourceHtml, outputFilename):
    # open output file for writing (truncated binary)
    with open(outputFilename, "w+b") as resultFile:
        # convert HTML to PDF
        pisaStatus = pisa.CreatePDF(
                sourceHtml,                # the HTML to convert
                dest=resultFile)           # file handle to recieve result

    # return True on success and False on errors
    return pisaStatus.err

# ERROR: xhtml2pdf does not show images
convertHtmlToPdf(html_out, 'out.pdf')

k = str(Path(__file__).parent / 'pdf.js')

PATH_PHANTOM_JS = r'C:\Users\Евгений\Desktop\node_modules\phantomjs\lib\phantom\bin\phantomjs.exe'

#def render_pdf_phantomjs(html: str):
#    """mimerender helper to render a PDF from HTML using phantomjs."""
#    # The 'makepdf.js' PhantomJS program takes HTML via stdin and returns PDF binary via stdout
#    # https://gist.github.com/philfreo/5854629
#    # Another approach would be to have PhantomJS do a localhost read of the URL, rather than passing html around.
#    from subprocess import Popen, PIPE, STDOUT, run 
#    p = Popen([PATH_PHANTOM_JS, str(Path(__file__).parent / 'pdf.js')], 
#               stdout=PIPE, stdin=PIPE, stderr=STDOUT)
#    return p.communicate(input=html.encode('utf-8'))[0]
#
#x = render_pdf_phantomjs(html_out)
#with open('ph.pdf', "w+b") as f:
#    f.write(x)
#
#import pathlib
#print(pathlib.Path(__file__).as_uri())
#run('html-pdf')







