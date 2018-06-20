"""Run full cycle of data processing from download to saving dataframe."""

from kep.download.download import RemoteFile
from kep.word2csv.word import word2csv
from kep.vintage import Vintage

def run(year, month): # pragma: no cover
    #download and unpack
    remote = RemoteFile(year, month)
    remote.download()
    remote.unrar()

    # Word files -> interim csv files
    word2csv(year, month)

    # parse interim csv, validate, save to prcessed foolder
    vint = Vintage(year, month)
    vint.validate()
    vint.save()

if __name__ == '__main__':
    # next call:
    run(2018, 5)

# Workflow
# --------    
#
# 1. what is latest date available? 
# 2. could newer data have come already?
# 3. [+] let's parse the new data 
# 4. [-] commit to repo
# 5. upload to database
# 6. create a PDF handout or other assets

# Something to know:
# ------------------ 
#   
# - output: 
#   - industrial production and other busness activity
#   - corp profits
# - housing construction
# - retail sales and household incomes    
# - budget expenditure and revenues
# - export and import
# - prices, inflation, interest rates
# - exchange rate
# - Q:GDP
# - Q:investment (unrelaible)
# - targets/forecasts   
