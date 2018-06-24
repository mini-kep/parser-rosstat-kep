from xhtml2pdf import pisa             # import python module

# Define your data
sourceHtml = "<html><body><p>To PDF or not to PDF</p></body></html>"
outputFilename = "test.pdf"

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

convertHtmlToPdf(sourceHtml, outputFilename)
