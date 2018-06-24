from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

import access        
import create_png
import definition

dfa, dfq, dfm = (access.get_dataframe(freq) for freq in 'aqm')

# select dataframe    
df = dfq
df['TRADE_SURPLUS_bln_usd'] = (df['EXPORT_GOODS_bln_usd'] 
                             - df['IMPORT_GOODS_bln_usd'])  
 
FOLDER = Path(__file__).parent / 'output'
if not FOLDER.exists():
    FOLDER.mkdir()
             
# filenaming convention
def locate(filename):
    return str(FOLDER / filename)

def as_uri(filename):
    return Path(locate(filename)).as_uri()   

# create png files
for header, charts in definition.CHARTS_DICT.items():
    for chart in charts:
        create_png.plot_long(df[chart.names],
                  title=chart.title, 
                  start=2005)
        figname = locate(chart.filename)
        create_png.save(figname)

# create template parameters
plot_dicts = [dict(
                  header=header,
                  filenames=list(as_uri(c.filename) for c in charts)
              )    
              for header, charts in definition.CHARTS_DICT.items()]

table_doc = """
{% for plot in plot_dicts %}

<div id="section_header">
{{plot['header']}}
</div>
<div id="images">
<img class="image" src="{{plot['filenames'][0]}}">
<img class="image" src="{{plot['filenames'][1]}}">
</div>

{% endfor %}
""" 

# NOT TODO: put me back

#{% if loop.index == 4 %}
#<div style="page-break-before: always" id="plot">
#{% else %}

 
template_doc = """<html>
<head>
    <meta http-equiv="content-type" 
          content="text/html; charset=UTF-8">
    <title>{{ page_header }}</title>
<style type="text/css">
    @page { size: A4; margin: 1cm; }
    @font-face { font-family: Arial; }
</style>
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

Path(locate('template.html')).write_text(template_doc, encoding='utf-8')

env = Environment(loader=FileSystemLoader('output'))
template = env.get_template('template.html')

template_vars = {"page_header" : "Macroeconomic Charts",
                 "plot_dicts": plot_dicts
                 }
html_out = template.render(template_vars)
print(html_out)
Path(locate('listing.html')).write_text(html_out)

# NOTE: weasyprint is not windows-compatible. msu yuse different pdf renderer
#HTML(string=html_out, base_url=os.path.dirname(os.path.abspath(__file__))).write_pdf("ts.pdf", stylesheets=[CSS(string='@page {size: Letter;  margin: 0.3in 0.3in 0.3in 0.3in;}')])

# alternatives documented at https://gist.github.com/philfreo/44e2e26a65820497db234d0c66ed58ae
# python: weasyprint or xhtml2pdf.pisa

def convertHtmlToPdf(sourceHtml, outputFilename):
    # open output file for writing (truncated binary)
    with open(outputFilename, "w+b") as resultFile:
        # convert HTML to PDF
        pisaStatus = pisa.CreatePDF(
                sourceHtml.encode('utf-8'),                # the HTML to convert
                dest=resultFile,           # file handle to recieve result
                encoding='utf-8',
                show_error_as_pdf=True)
    # return True on success and False on errors
    return pisaStatus.err

# ERROR: xhtml2pdf does not show images
convertHtmlToPdf(html_out, locate('out.pdf'))
