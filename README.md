Blackcoffer Data Extraction and Text Analysis
---------------------------------------------
1. Objective
---------------------------------------------
The objective of this assignment is to extract textual data (article titles and article body) from the URLs provided in "Input.xlsx" and perform sentiment and readability analysis to generate variables defined in "Output Data Structure.xlsx".

---------------------------------------------
2. Approach Overview
---------------------------------------------
The project is divided into two main phases:

PHASE 1: Data Extraction
- Read URLs from Input.xlsx.
- Use BeautifulSoup to scrape the article title and content.
- Remove unwanted elements like headers, footers, and navigation menus.
- Save cleaned article text as a .txt file named by URL_ID.

PHASE 2: Text Analysis
- Clean and tokenize text using StopWords from the StopWords folder.
- Use the MasterDictionary to calculate sentiment metrics.
- Compute readability and structural metrics as per “Text Analysis.docx”.

---------------------------------------------
3. Folder Structure
---------------------------------------------
Blackcoffer_Assignment/
│
├── data/
│   ├── Input.xlsx
│   ├── Output Data Structure.xlsx
│   ├── output.xlsx
│   ├── MasterDictionary/
│   │   ├── positive-words.txt
│   │   └── negative-words.txt
│   └── StopWords/
│       └── stopwords.txt   
│
├── main.py
├── README.txt
└── venv/ (optional virtual environment folder)

---------------------------------------------
4. How to Run the Code
---------------------------------------------
1. Open terminal / PowerShell inside the project folder.
2. (Optional) Activate virtual environment:
   `venv\Scripts\activate`
3. Install dependencies:
   `pip install pandas openpyxl nltk beautifulsoup4 requests selenium`
4. Run the Python script:
   `python main.py`
5. The script will:
   - Extract and clean articles.
   - Perform sentiment & readability analysis.
   - Generate `output.xlsx` in the `data/` folder.

---------------------------------------------
5. Dependencies
---------------------------------------------
- Python 3.9 or above
- pandas
- openpyxl
- nltk
- beautifulsoup4
- requests
- selenium

---------------------------------------------
6. Output Description
---------------------------------------------
The final output file (`output.xlsx`) includes:
- All columns from Input.xlsx
- Plus 13 derived columns:
  POSITIVE SCORE  
  NEGATIVE SCORE  
  POLARITY SCORE  
  SUBJECTIVITY SCORE  
  AVG SENTENCE LENGTH  
  PERCENTAGE OF COMPLEX WORDS  
  FOG INDEX  
  AVG NUMBER OF WORDS PER SENTENCE  
  COMPLEX WORD COUNT  
  WORD COUNT  
  SYLLABLE PER WORD  
  PERSONAL PRONOUNS  
  AVG WORD LENGTH  

