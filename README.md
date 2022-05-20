# Read, store and analyze NFHS-5 data from district-level summaries

1. [Download State and District-level PDFs](https://nbviewer.org/github/kalyaninagaraj/NFHS5/blob/main/DownloadPDFs.ipynb)  
   Download PDF reports of key indicators for each state/UT and each of their districts from [http://rchiips.org/nfhs/](http://rchiips.org/nfhs/)
   
2. [Pickle the Indicators](https://nbviewer.org/github/kalyaninagaraj/NFHS5/blob/main/PickleIndicators.ipynb)  
   Save indicators, names of states/UTs and their respective districts in dictionary format for easy "pickling" (serializing)  
   
3. [Save district-level statistics to DataFrame](https://nbviewer.org/github/kalyaninagaraj/NFHS5/blob/main/WriteToDataFrame.ipynb)  
   Read the PDF reports sequentially and store 104 indicator values for all 704 districts in a CSV file.
   
4. [Perform PCA on the reported NFHS-5 data]()  
   Perform PCA to (1) reduce dimensionality for plotting, and to (2) impute missing (unavailable) values in the dataset. 
   
5. [Display NFHS-5 data on maps using GeoPandas]()

## Code Credit
[@kalyaninagaraj](https://github.com/kalyaninagaraj/)

## Resources
1. [National Family Health Survey of India](http://rchiips.org/nfhs/factsheet_NFHS-5.shtml) (official website)
2. [fitz, or PyMuPDF](https://pymupdf.readthedocs.io/en/latest/intro.html) (documentation)
3. [pickle](https://docs.python.org/3/library/pickle.html) (documentaion)
4. [GeoPandas](https://geopandas.org) (documenatation)
