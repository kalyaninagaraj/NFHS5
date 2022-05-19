# Read and store NFHS-5 data (district-level summaries only) from official pdf documents
I wrote these tutorial-style notebooks when I was learning to use the `fitz` module (in `PyMuPDF`) for reading text from PDFs.

1. [Download State and District-level PDFs](https://nbviewer.org/github/kalyaninagaraj/NFHS5/blob/main/DownloadPDFs.ipynb)
   Download PDF reports of key indicators for each state/UT and each of their districts. 
2. [Pickle the Indicators](https://nbviewer.org/github/kalyaninagaraj/NFHS5/blob/main/PickleIndicators.ipynb) 
   Save indicators, names of states/UTs and their respective districts in dictionary format for easy "pickling" (serializing)
3. [Save district-level statistics to DataFrame](https://nbviewer.org/github/kalyaninagaraj/NFHS5/blob/main/WriteToDataFrame.ipynb)
   Read the PDF reports sequentially and store 104 indicator values for all 704 districts in a CSV file.

## Code Credit
[@kalyaninagaraj](https://github.com/kalyaninagaraj/)

## Resources
1. [National Family Health Survey of India](http://rchiips.org/nfhs/factsheet_NFHS-5.shtml) (official website)
2. [fitz, or PyMuPDF](https://pymupdf.readthedocs.io/en/latest/intro.html) (documentation)
3. [pickle](https://docs.python.org/3/library/pickle.html) (documentaion)
