import os
import cv2
import fitz
# Extracted json save
import glob
import json

DPI = 300
UNIT_CONSTANT = 72
DEBUG_DPI_BOX_ADJUST = True
# Set true exclude small block wich have no line
DEBUG_SMALL_BLOCK = False


def DrawTextAndOval(image, text_data, log_dir="logs", color = (0,255,0), image_name="unknown.jpg"):

    """
    Discription:  This function use for draw text, block and oval into image 
    it solve depend on page layout height and width count character.
    Parameters:
        image {numpy}       : numpy image
        data_dic {dictonary}: extracted data dictonary
        color(tupple)       : tupple of color range 
        image_name          : image name
    Returns:
       image {numpy}        : numpy image
    """
    for page in text_data:
        # print(page)
        px1, py1, px2, py2 = page["x"], page["y"], page["x"]+page["w"], page["y"]+page["h"]
        lines = page["lines"]
            # print(page)
        if len(lines):
            for line in lines:
                lx1, ly1, lx2, ly2, text = line["x"], line["y"], line["x"]+line["w"], line["y"]+line["h"], line["text"]
                cv2.putText(image, str(text), (lx1, ly1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
                cv2.rectangle(image, pt1=(lx1, ly1),pt2=(lx2, ly2),color= (0,0,255),thickness=2)

            # cv2.putText(image, "block", (bx1, by1), cv2.FONT_HERSHEY_SIMPLEX, 1, ClassAndColorMap["block"], 1, cv2.LINE_AA)
        # cv2.rectangle(image, pt1=(px1, py1),pt2=(px2, py2),color= (0,255,0),thickness=2)
    cnt = 0
    # for shape in oval_data:
    #     sx1, sy1, sx2, sy2, shape_name =shape['x'], shape['y'], shape['x']+shape['w'], shape['y']+shape['h'], shape["shape_name"]
    #     # print(cnt, [sx1, sy1, sx2, sy2])
    #     if DEBUG_OVAL:
    #         cv2.putText(image, str(sx1)+","+str(sy1), (sx1-50, sy1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, ClassAndColorMap["oval"], 1, cv2.LINE_AA)
    #         cv2.rectangle(image, pt1=(sx1, sy1),pt2=(sx2, sy2),color= ClassAndColorMap["oval"],thickness=2)
    #         cnt+=1
    # print(image.shape)
    # print(image_name)
    cv2.imwrite("logs/"+image_name, image)
    # print("image save done")




def AdjustTextbbox(bbox):

    """
    Discription:  Here lpy2(layout pdf y2 coordinate)
    layout pdf coordinate starting from buttom left side but image 
    coordinate star from top left, so we need to inverse of y asix value.
    Parameters:
        bbox {list} : extractd coordiante
        
    Returns:
       bbox {list}  : update extractd coordiante
    """
    # bbox = bbox[0], bbox[1], bbox[2], bbox[3]
    # pdf coordiante convert this unit of pdf standard like as 1 inch = 72 DPI
    # Here pdf coordinate update for 300 DPI image
    # bbox =[int((i/UNIT_CONSTANT)*DPI) for i in bbox]
    # points = pixels * 72 / dpi
    # bbox =[int((i*UNIT_CONSTANT)/DPI) for i in bbox]
    bbox =[round((i/UNIT_CONSTANT)*DPI) for i in bbox]

    return bbox

def BoxAdjectforimage(box_coordiante, lpy2):
    """
    Discription : This function use for adjust coordinate for extracted image .
    Here lpy2(layout pdf y2 coordinate) layout pdf coordinate starting from buttom left side but image 
    coordinate star from top left, so we need to inverse of y asix value.
    Parameters:
        box_coordiante {list} : coordiante of box
        lpy2 {int}            : layout page y2 coordinate
    Returns:
        box_coordiante {list} : updated coordiante of box
    """

    box_coordiante = box_coordiante[0], abs(lpy2 - box_coordiante[3]), box_coordiante[2], abs(lpy2 -  box_coordiante[1])
    # box_coordiante = box_coordiante[0], box_coordiante[1], box_coordiante[2], box_coordiante[3]
    # pdf coordiante convert this unit of pdf standard like as 1 inch = 72 DPI
    # Here pdf coordinate update for 300 DPI image
    box_coordiante =[int((i/UNIT_CONSTANT)*DPI) for i in box_coordiante]
    return box_coordiante

def BoxErrorSolver(box_coordiante, BoxErrorSolver_thes):
    """
    Discription: This function use if got any error coordinate like three point(125,125362,25) then 
    it solve depend on page layout height and width count character.
    Parameters:
        box_coordiante {list}      : coordiante of box
        BoxErrorSolver_thes {list} : if layout page height and width 
    Returns:
        box_coordiante {list}      : updated coordiante of box
    """

    width_character_lenght = BoxErrorSolver_thes[0]
    height_character_lenght = BoxErrorSolver_thes[1]
    y_axis = box_coordiante[1]
    y1, x2 = int(str(y_axis)[:height_character_lenght]), int(str(y_axis)[height_character_lenght:])
    box_coordiante = box_coordiante[0], y1, x2, box_coordiante[2] 
    return box_coordiante


def TextRegionExtraction(pdf_file_path, page_number, pdf_name="unknown"):

    """
    Discription : This function use for extraction textual information(text line, text line coordinate, block box) from pdf file
    Parameters:
        pdf_file_path {str} : input pdf file path
        page_number {dir}   : pdf page number
        pdf_name {str}      : image name from pdf file
    Returns:
        text_extracted_data {dictonary} : dictonary of textual data information
    """
    text_extracted_data = []
    page_width , page_height = 0, 0
    with fitz.open(pdf_file_path) as doc:
        # i = 0
        for page in doc:
            page_width, page_height = int(page.rect.width), int(page.rect.height)
            if DEBUG_DPI_BOX_ADJUST:
                ajusted_height_width = AdjustTextbbox([page_width, page_height])
                page_width, page_height = ajusted_height_width
            # print("Page Height and width : ",page.rect.width, page.rect.height)
            # page_dic = page.getText('dict')
            data = page.getText('dict')
            # print(data)
            block_list = []
            for block in data['blocks']:
                # print(block)
                block_bbox = block["bbox"]
                # print(block_bbox)
                if DEBUG_DPI_BOX_ADJUST:
                    block_bbox = AdjustTextbbox(block_bbox)
                bx1, by1, bx2, by2 = block_bbox
                bw, bh = abs(bx2-bx1), abs(by2-by1)
                if DPI != 300:
                    bh_thres = (10*DPI)/300
                    bw_thres = (10*DPI)/300
                # if cfg.VENDOR_NAME !="ES&S" and DEBUG_SMALL_BLOCK:
                #         if bh< 10 or bw < 10:
                #             continue
                block_structrue = {"type" : "block", "x":bx1, "y":by1, "w":bw, "h":bh, "page":page_number, "lines":[]}
                if "lines" in block:
                    lines =  block["lines"]
                    if len(lines) ==0:
                        continue
                    for line in lines:
                        # print(line)
                        spans = line['spans']
                        for span in line['spans']:
                            text = span['text'].replace(u'\xa0', ' ')
                            if len(text.strip())== 0:
                                continue
                            spans_bbox = span['bbox']
                            if DEBUG_DPI_BOX_ADJUST:
                                spans_bbox = AdjustTextbbox(spans_bbox)
                            # print(spans_bbox)
                            x, y, w, h = int(spans_bbox[0]), int(spans_bbox[1]), int(abs(spans_bbox[2]- spans_bbox[0])),\
                                 int(abs(spans_bbox[3]- spans_bbox[1]))
                            line_data = {'type':"line", 'x': x, 'y': y, 'w': w, 'h': h, 'page': page_number, 'text': text}
                            block_structrue["lines"].append(line_data)
                            # text_extracted_data["text"].append(line_data)
                        line_bbox = line['bbox']
                
                block_list.append(block_structrue)
        text_extracted_data.extend(block_list)    
    return text_extracted_data, (page_width , page_height)

if __name__ == "__main__":
    pdf_path ="logs/pdf"
    img_path ="logs/images"
    pdf_files = glob.glob(pdf_path+"/*.pdf")
    data_dict = {}
    cnt = 0
    for pdf_file in pdf_files:
        pdf_name = os.path.basename(pdf_file)
        image_name = (pdf_name[:-4]+".png")
        image_file_path = os.path.join(img_path,pdf_name[:-4]+".png")
        image = cv2.imread(image_file_path)
        print(image_file_path)
        
        text_extracted_data, page_dim = TextRegionExtraction(pdf_file,1, pdf_name)
        # print(text_extracted_data)
        DrawTextAndOval(image, text_extracted_data, image_name= pdf_name[:-4]+".jpg") 
        # print(text_extracted_data)
        data_dict[image_name] = text_extracted_data
        print(f'Processed file :{cnt}/{len(pdf_file)}')
        cnt+=1
    
    with open('logs/extracted.json', 'w', encoding ='utf8') as json_file:
        json.dump(data_dict, json_file, ensure_ascii = False, indent=4)