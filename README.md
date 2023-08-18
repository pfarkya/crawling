# crawling

This is a crawing python script that helps you to create PDF for a site using selenium.

### uses 

#### install required module

```sh
conda install -c conda-forge PyPDF2
conda install -c conda-forge selenium
conda install -c conda-forge webdriver-manager
```


#### setup some variable before running script

in crawl.py file there is input section `### input section` where you need to fill the detail before running the script.

| variable | uses |
| --- | --- |
| main_url | the URL from where the crawling starts |
| allowed_url_base | Is a array of the href that needs to go inside |
| depth | level of the depth to be crawled |
| css_selector_page | '<>' |
| css_selector_page_loaded | '<>' |
| css_selector_main_contain | '<>' |
| css_selector_expander | '<>' |
| main_pdf_file | 'merged.pdf' |
| pdf_folder | 'pdfs/' |
| html_folder | "html/" |
| txt_folder | "txt/" |
| maincontain_folder | "maincontent/" |
| ontheflymergepdf | False |


#### running the script

```sh
python crawl.py
```
