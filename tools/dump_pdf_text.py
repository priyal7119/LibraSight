from pypdf import PdfReader
p='reports/generated/data_quality.pdf'
try:
    r=PdfReader(p)
    txt='\n'.join([page.extract_text() or '' for page in r.pages])
    print(txt)
except Exception as e:
    print('ERR',e)
