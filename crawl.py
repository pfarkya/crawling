from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import base64
from PyPDF2 import PdfFileMerger, PdfFileReader
import os
 
# Install Webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# service = Service(ChromeDriverManager().install())

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

### input section
main_url = '<>'
allowed_url_base = [ "<>"]
depth = 3
css_selector_page = '<>'
css_selector_page_loaded = '<>'
css_selector_main_contain = '<>'
css_selector_expander = '<>'
main_pdf_file = 'merged.pdf'
pdf_folder = 'pdfs/'
html_folder = "html/"
txt_folder = "txt/"
maincontain_folder = "maincontent/"
ontheflymergepdf = False
### End of input section

mergedObject = PdfFileMerger()

def check_existance(name):
    if not os.path.exists(name):
        raise Exception(f"{name} not exists")

check_existance(pdf_folder)
check_existance(html_folder)
check_existance(txt_folder)
check_existance(maincontain_folder)



def writeToFile(filename, content, binary=False):
    mode = 'w'
    if binary:
        mode = 'wb'
    try:
        f = open(filename, mode)
    except Exception as error:
        print('Failed to open operation', error)
    else:
        try:
            f.write(content)
        except Exception as error:
            print('Failed to write operation', error)
        f.close()

def save_pdf_file(d):
    t = d.title
    # print(f'Title: {t}')
    pdf = d.print_page()
    filename = pdf_folder + t.replace('/', '_') + ".pdf"
    writeToFile(filename, base64.b64decode(pdf), True)
    if ontheflymergepdf:
        merge_to_mainfile(filename)

def merge_to_mainfile(filename):
    mergedObject.append(PdfFileReader(filename, 'rb'))

def save_html_file(d):
    t = d.title
    # print(f'Title: {t}')
    html = d.page_source
    filename = html_folder + t.replace('/', '_') + ".html"
    writeToFile(filename, html)

def save_maincontain_file(d):
    t = d.title
    # print(f'Title: {t}')
    maincontain = d.find_element(By.CSS_SELECTOR, css_selector_main_contain)
    filename = maincontain_folder + t.replace('/', '_') + ".html"
    writeToFile(filename, 'Title: ' + t+ '\nLink: '+ d.current_url + '\nTag:\n' + maincontain.get_property('outerHTML'))

def save_txt_file(d):
    t = d.title
    # print(f'Title: {t}')
    maincontain = d.find_element(By.CSS_SELECTOR, css_selector_main_contain)
    filename = txt_folder + t.replace('/', '_') + ".txt"
    writeToFile(filename, 'Title: ' + t+ '\nLink: '+ d.current_url + '\nText:\n' + maincontain.get_property('outerText'))

def all_image_to_loaded():

    def _predicate(d):
        return d.execute_script('let x = ()=>{ans = true;document?.images?.forEach && document.images.forEach((i)=> {ans = ans && i.complete}); return ans};return x();')

    return _predicate

def visit_page(d, url, dep, mxdep, aurl, visited, existingSet):
    if dep > mxdep: 
        print("reached to max depth:", dep)
        return
    notAllow = True
    for bu in aurl:
        if url.startswith(bu):
            notAllow = False
    if notAllow:
        print("url not allowed:", url)
        return
    if visited.get(url) != None :
        print("Already visited url:", visited.get(url))
        return
    start = time.time()
    d.get(url)
    try:
        WebDriverWait(d, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector_page)))
        WebDriverWait(d, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector_page_loaded)))
        WebDriverWait(d, 5).until(all_image_to_loaded())
        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")
    except Exception as error:
        print("failed webdriver wait", error)
    
    e1 = time.time()
    print(f"Page Load time\tTime taken: {(e1-start):.03f}ms")
    # time.sleep(5)
    # /html/body/div/div/article/div/div/div/div[2]/div/div/div/div[1]/div/div
    # .accordion-widget__expand-toggle
    expand_all_eles = d.find_elements(By.CSS_SELECTOR, css_selector_expander)
    for expand_all_ele in expand_all_eles:
        expand_all_ele.click()
    t = d.title
    print(f'Title: {t}')
    save_pdf_file(d)
    save_html_file(d)
    save_maincontain_file(d)
    save_txt_file(d)
    e2 = time.time()
    print(f"Save Page\tTime taken: {(e1-e2):.03f}s")
    links = d.find_elements(By.XPATH, '//a[@href]')
    hrefs = []
    visited[url] = True
    for link in links:
        try: 
            href = link.get_attribute('href')
            hrefs.append(href)
        except:
            print("Some Href is missed", link)
    hrefsSet = set(hrefs)
    hrefsSet.difference_update(existingSet)
    existingSet.update(hrefsSet)
    e3 = time.time()
    print(f"Page Task completed\tTotal Time taken: {(e3-start):.03f}s")
    for href in hrefsSet:
        print("Visiting level:", dep+1, " url:", href)
        visit_page(d, href, dep+1, mxdep, aurl, visited, existingSet)

def merge_pdf(inputFolder, outputFile):
    # Call the PdfFileMerger
    mergedObject = PdfFileMerger()
    
    # I had 116 files in the folder that had to be merged into a single document
    # Loop through all of them and append their pages
    dir_list = os.listdir(inputFolder)

    for fileName in dir_list:
        if fileName.endswith('.pdf'):
            mergedObject.append(PdfFileReader(inputFolder +'/' + fileName, 'rb'))
    
    # Write all the files into a file which is named as shown below
    mergedObject.write(outputFile)

def scrapper():
    service = Service(GeckoDriverManager().install())

    map_visited = {}
    
    options = Options()
    # options.headless = True
    # options.add_argument("--window-size=1920,1200")
    # driver = webdriver.Chrome(options=options,service=service)
    driver = webdriver.Firefox(options=options,service=service)
    try:
        driver.get(main_url)
        time.sleep(55)
        visit_page(driver, main_url, 0, depth, allowed_url_base, map_visited, set())
    finally:
        driver.quit()
        mergedObject.write(main_pdf_file)

def merge_pdf_v2(inputFolder):
    dir_list = os.listdir(inputFolder)
    for fileName in dir_list:
        if fileName.endswith('.pdf'):
            merge_to_mainfile(inputFolder + fileName)
            print("complete one merge")
    mergedObject.write(main_pdf_file)

if os.path.exists(main_pdf_file):
        merge_to_mainfile(main_pdf_file)


#### Srapper to run
scrapper()
if not ontheflymergepdf:
    merge_pdf_v2(pdf_folder)