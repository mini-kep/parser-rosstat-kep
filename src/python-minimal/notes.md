DONE
====
- [x] repair sphynx docs
- [x] value check procedure (now has all/any check) 


NOT TODO
========
- more tests
- interface levels - all funcs accept strings 
- check coverage report 
- compeltion metrics: how many variables are parsed
- relative imports in package
- add CPI_yoy variable


OUTSTANDING
===========
- replicate NY FED databook
- make Excel file
- variable name descriptions
- add new sheet with variable name descriptions to Excel
- variable grouping
- concat INDPRO from two series
- accumulate CPI_rog to yoy
- MA(12) smoothing 
 % of GDP (annual)

Plotting
--------
  - place charts on one A4 sheet and make PDF via html (Jinja/Weasyprint)

    
# NOT TODO NOW:
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
  
  
  
Deliverables
------------
- data revisions case
- presentation with text

Topics
------  

For grouping of variables/story:

 - output: 
   - industrial production and other busness activity
   - corp profits
 - housing construction
 - retail sales and household incomes    
 - budget expenditure and revenues
 - export and import
 - prices, inflation, interest rates
 - exchange rate
 - Q:GDP
 - Q:investment (unrelaible)
 - targets/forecasts   


DOI/citation
------------

- https://zenodo.org/record/534875 
- PyCon lecture on licensing


Generate PDF report
-------------------

- https://www.reportlab.com/docs/reportlab-userguide.pdf
- http://mpastell.com/pweave/docs.html
- https://edinburgh-genome-foundry.github.io/pdf_reports/
- jinja + https://weasyprint.org/ 

See also [talk about PDF](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=0ahUKEwjDwvOtkYXbAhUDBiwKHZq6CPgQtwIIKzAA&url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3Dv8W-LxzZ9yo&usg=AOvVaw39aMRZTcXyYPlTxzcOTLPi)






