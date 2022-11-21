'''
This script use for pdf page spliting each of pdf page and image to pdf converstion [batch processing]
@ Author      : Md. Saiful Islam
@ Email       : Saifulbrur9379@gmail.com
@ Date        : 27/02/2022
@ Copyright   :
@ license     : MIT
'''
import os
import glob
import time
import fitz
import math
from termcolor import colored
from pdf2image import convert_from_path
from PyPDF2 import PdfFileWriter, PdfFileReader

DPI = 300
batch_size = 100
DEBUG = True


def pdf_to_image_conversion(
    pdf_file_path:str, DPI:int, logs_dir:str="logs")-> str:
    """
    Discription: this function use pdf to image conversion
    Parameters:
        pdf_file_path {str} : input pdf file path
        logs_dir{dir}       : log path directory
        image_name {str}    : image name from pdf file
    Returns: None
    
    """
    # convert each pdf page to image
    for pdf_name in pdf_file_path:
        print(f"pdf name :{pdf_name}")
        
        pages = convert_from_path(pdf_name, DPI)
        for page in pages:
            img_path = os.path.join(logs_dir, os.path.basename(pdf_name)[:-4]+".png")
            page.save(img_path, "JPEG", DPI=DPI)

def pdf_error_solver(pdf_file_path:str, error_solved_pdf_path:str)->None:
    """
    Discription: this function use for only read an write using fitz
    Parameters:
        pdf_file_path {str}        : input pdf file path
        error_solve_pdf_path {str} : pdf path of modification pdf path
    Returns: None
    """
    # read pdf file using fitz
    src = fitz.open(pdf_file_path)
    doc = fitz.open()
    # rect_width = 612.0
    for ipage in src:
        rect_height = ipage.rect.height
        rect_width = ipage.rect.width
        page = doc.newPage(width = rect_width, height = rect_height)
        page.showPDFpage(page.rect, src, ipage.number)
    doc.save(error_solved_pdf_path)

def batch_processing(page_list, inputpdf, output_dir=""):
    split_pdf = []
    for i in page_list:
        # print(i)
        output = PdfFileWriter()
        output.addPage(inputpdf.getPage(i))
        page_name = os.path.join(output_dir, pdf_name+"_"+str(i)+".pdf")
        with open(page_name, "wb") as outputStream:
            output.write(outputStream)
        split_pdf.append(page_name)
    return split_pdf

def pdf_page_spliter(
    pdf_file_path:str, DPI:int = 300, DEBUG:bool = False, logs_dir:str="logs", pdf_name:str="unkown")->str:
    """
    Discription : This function use for split each of pdf page from pdf file
    Parameters:
        pdf_file_path {str} : input pdf file path
        logs_dir {dir}      : log path directory
        pdf_name {str}      : image name from pdf file
    Returns: None
    """
    # get base name without extention
    
    error_solved_pdf_path = os.path.join(logs_dir, pdf_name+".pdf")
    # solve pdf file issue if this pdf can not read by pypdf2
    print("PDF Error Solve Process          : ",end='', flush= True)
    pdf_error_solver(pdf_file_path, error_solved_pdf_path)
    print(colored("Done", 'green'))

    print("PDF to PDF page Spliting Process : ",end='', flush= True)
    # define log directory
    split_pdf_page_dir = os.path.join(logs_dir, "pdf")
    os.makedirs(split_pdf_page_dir, exist_ok=True)
    # read pdf file 
    inputpdf = PdfFileReader(open(error_solved_pdf_path, "rb"))
    print(inputpdf.numPages)
    number_of_page = inputpdf.numPages
    batch = math.ceil(number_of_page/batch_size)
    start , ending = 0, batch_size
    # for i in range(0, number_of_page, batch_size):
    # page_index = 0
    pdf_names_list = []
    for _ in range(batch):
        if ending > number_of_page:
            ending = number_of_page
        page_list = [i for i in range(start, ending)]
        pdf_names = batch_processing(page_list, inputpdf, output_dir = split_pdf_page_dir)
        print(f" Processed {ending}/ {number_of_page}")
        pdf_names_list.extend(pdf_names)
        # print(page_list)
        # print(start, ending)
        start = ending
        ending = start + batch_size
    # if DEBUG:
        # define log image directory
    image_path = os.path.join(logs_dir,"images")
    os.makedirs(image_path, exist_ok=True)
    print("PDF to Image conversion Process  : ",end='', flush= True)
    # print(pdf_names_list)
    pdf_to_image_conversion(pdf_names_list, DPI, logs_dir = image_path)
    print(colored("Done", 'green'))
    # get base name without extention
    # return split_pdf

if __name__ =="__main__":
    
    pdf_file_path = "data/client"
    logs_dir = "logs"
    pdf_files = glob.glob(pdf_file_path+"/*.pdf")
    cnt = 0
    for pdf_file in pdf_files:
        # try:
        pdf_name = os.path.basename(pdf_file)[:-4]
        print("\n")
        print("-----------------------------------------------")
        start_time = time.time()
        pdf_page_spliter(
            pdf_file, 
            DPI=DPI, 
            DEBUG = DEBUG, 
            logs_dir = logs_dir, 
            pdf_name = pdf_name
            )
        print("-----------------------------------------------")
        print(f"Total Processing Time         {cnt}/{len(pdf_files)}: ",time.time()-start_time)
        print("\n")
        cnt+=1


