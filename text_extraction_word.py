

import os
import cv2
import fitz
import glob
import json

DPI = 300
UNIT_CONSTANT = 72

def draw_region(text_data, image, file_name, output_dir = "logs/word_logs"):
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
    cv2.imwrite(os.path.join(output_dir, file_name), image)



def data_formate(bbox, text):
    x, y, w, h = bbox[0], bbox[1], abs(bbox[2]-bbox[0]), abs(bbox[3]-bbox[1]) 
    block= {
            "type": "block",
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "page": 1,
            "lines": [
                {
                    "type": "line",
                    "x": x,
                    "y": y,
                    "w": w,
                    "h": h,
                    "page": 1,
                    "text": text
                }
            ]
        }
    return block

def textWordRegionExtraction(pdf_file_path):
    data_list = []
    with fitz.open(pdf_file_path) as document:
        for page_number, page in enumerate(document):
            print(page)
            words = page.getText("words")
            for word in words:
                if len(word)< 5:
                    continue
                bbox =[round((i/UNIT_CONSTANT)*DPI) for i in word[:4]]
                text = word[4].replace(u'\xa0', ' ')
                formated_data = data_formate(bbox, text)
                data_list.append(formated_data)
    return data_list

if __name__ =="__main__":
    # path_to_pdf_file = "logs/pdf/5e1dcd34f9e9df6b22000284.pdf_1.pdf"
    # img_path = "logs/images/5e1dcd34f9e9df6b22000284.pdf_1.png"
    pdf_path ="logs/pdf"
    img_path ="logs/images"
    output_dir = "logs/word_logs"
    os.makedirs(output_dir, exist_ok=True)

    pdf_files = glob.glob(pdf_path+"/*.pdf")
    data_dict = {}
    image = cv2.imread(img_path)
    cnt = 0
    for pdf_file in pdf_files:
        pdf_name = os.path.basename(pdf_file)
        if pdf_name !="Berlitz Paris Pocket Guide (Guides, Insight) (z-lib.org)_150.pdf":
            continue
        image_name = (pdf_name[:-4]+".png")
        image_file_path = os.path.join(img_path,pdf_name[:-4]+".png")
        image = cv2.imread(image_file_path)
        data_list = textWordRegionExtraction(pdf_file)
        data_dict[image_name] = data_list
        draw_region(data_list, image, image_name, output_dir = output_dir)
        print(f'{cnt}/{len(pdf_files)}')
        cnt+=1

    with open('logs/word_extracted.json', 'w', encoding ='utf8') as json_file:
        json.dump(data_dict, json_file, ensure_ascii = False, indent=4)
