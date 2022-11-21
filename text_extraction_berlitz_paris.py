"""
Berlitz Paris Pocket Guide (Guides, Insight) (z-lib.org)
Berlitz Paris 29
Rick Steves Paris: 48

"""



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

Berlitz_Paris = 29 
Rick_Steves_Paris = 48

def draw_img(image, text, p_block_bbox):
    bx1, by1, bx2, by2 = p_block_bbox
    cv2.putText(image, str(text), (bx1, by1), cv2.FONT_HERSHEY_SIMPLEX, 3, (0,0,255), 2, cv2.LINE_AA)
    cv2.rectangle(image, pt1=(bx1, by1),pt2=(bx2, by2),color= (0,0,255),thickness=2)
    return image

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

def block_draw(image, block_data, log_dir="logs", reference = '', color = (0,255,0), image_name="unknown.jpg"):

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
    # print(block_data)
    block_bbox = AdjustTextbbox(block_data["bbox"])
    px1, py1, px2, py2 = block_bbox
    cv2.rectangle(image, pt1=(px1, py1),pt2=(px2, py2),color= (0,255,0),thickness=2)
    cv2.putText(image, block_data["status"], (px1, py1), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 2, cv2.LINE_AA)
    return image

def coordinate_preration(filtered_list):

    x1 = min([i[0] for i in filtered_list])
    y1 = min([i[1] for i in filtered_list])
    x2 = max([i[2] for i in filtered_list])
    y2 = max([i[3] for i in filtered_list])
    return (x1, y1, x2, y2)

def get_single_word_status(block):
    text_word = block["lines"][0]["spans"][0]["text"]
    print(text_word)
    if len(text_word)==1:
        return True
    return False

def small_font_size_bbox(block):
    aver_font_size = 0
    if "lines" in block:
        font_size = 0
        for line in block["lines"]:
            font_size+= line["spans"][0]["size"]
        aver_font_size = int(font_size/len(block["lines"]))
    return aver_font_size

def check_header(block, page_dim):
    width = page_dim[0]//4
    block_bbox = AdjustTextbbox(block["bbox"])
    total_font_size = 0
    for line in block["lines"]:
        font_size = line["spans"][0]["size"]
        total_font_size+=font_size
    average_font_size = total_font_size/ len(block["lines"])
    if average_font_size > 21:
        return "Prompt"
    elif width < block_bbox[0]:
        return "Prompt"
    return "completion"

def get_header_font_status(block):
    header_font_status = False
    for i in block["lines"]:
        if i["spans"][0]["size"] > 21:
            header_font_status = True
            break
    return header_font_status

def header_spliting(block, block_index, page_dim, page_number):
    
    if "lines" not in block:
        return None, block_index

    if len(block["lines"])==1:
        single_word_status = get_single_word_status(block)
        if single_word_status:
            return None, block_index
        comment = check_header(block, page_dim)
        block["status"] = comment
        block["page_number"] = page_number
        return block, block_index

    header_font_status = get_header_font_status(block)
    generated_block = {'type': 0, 'bbox': (), "lines":[]}
    block_list, filtered_list = [], []
    if header_font_status:
        # if len(lines) == 0:
        #     continue
        for line in block["lines"]:
            # print(line)
            font_size = line["spans"][0]["size"]
            # print(font_size)
            if font_size > 21:
                line_generated_block = {'type': 0, 'bbox': line["bbox"], "lines":[line], "status" : "Prompt", "page_number": page_number}
                block_list.append(line_generated_block)
            else:
                filtered_list.append(line["bbox"])
                generated_block["lines"].append(line)
        if len(filtered_list)==0:
            return None, block_index
        bbox_coordiantes = coordinate_preration(filtered_list)
        generated_block["bbox"] = bbox_coordiantes
        generated_block["status"] = "completion"
        generated_block["page_number"] = page_number
        block_list.append(generated_block)
        block_index +=1
        return block_list, block_index
    # print("++++++++++++++++++", block+++++++++++++++++++++++)
    # if block["lines"][0]["spans"][0]["flags"] ==16:
        
    #     line_generated_block = {'type': 0, 'bbox': block["lines"][0]["bbox"], "lines":[block["lines"][0]], "status" : "Prompt"}
    #     # prompt =  block["lines"][0]
    #     #  = []
    #     # print(prompt)
    #     print(line_generated_block)

    #     line_competion = block["lines"][1:]
    #     filtered_data= [line["bbox"] for line in line_competion]
    #         # filtered_data.append[]
    #     bbox_coordiantes = coordinate_preration(filtered_data)
    #     # print("bbox_coordiantes", bbox_coordiantes)
    #     # print(line_competion)
    #     c_block = {'type': 0, 'bbox': bbox_coordiantes, 'lines':line_competion, "status" :"completion"}
    #     # block["status"] = "completion"
    #     block = [line_generated_block, c_block]
    # else:
    block["status"] = "completion"
    block["page_number"] = page_number
    return block, block_index
    
def block_operations(text_extracted_data:dict, page_list:list, images, page_dim):
    cnt = 0
    prompt_completion, unique_page_list = [], []
    for key, value in text_extracted_data.items():
        # print(key)
        # print(key, "block lengt", len(value['blocks']))
        block_index = 0
        block_list = []
        for block in value['blocks']:
            # print(block)
            average_font_size = small_font_size_bbox(block)
            # print(f"Average font size : {average_font_size}")
            # print(block)
            if average_font_size < 12:
                continue
            elif average_font_size > 20 and len(block["lines"]) > 1:
                # print("block:", block)
                block["status"] = "Prompt"
                block["page_number"] = key
                block_list.append(block)
                # pass
            else:
                if "lines" in block:
                    if len(block["lines"]) == 0:
                        block_index+=1
                        continue
                new_block, block_index = header_spliting(block, block_index, page_dim, key)
                if new_block==None:
                    continue
                if isinstance(new_block, list):
                    block_list.extend(new_block)
                else:
                    block_list.append(new_block)
            block_index += 1
        unique_page_list.append(key)
        prompt_completion.extend(block_list)
        # for i in block_list:
        #     print(i)
        # for i, n_block in enumerate(block_list):
        #     image = block_draw(images[cnt], n_block)
        #     images[cnt] = image

        # cv2.imwrite("logs/draw_logs/"+str(page_list[cnt])+".jpg", images[cnt])
        # cnt+=1
    
    return prompt_completion, unique_page_list

def text_region_extraction(pdf_files:list, page_list:list)->dict:

    """
    Discription : This function use for extraction textual information(text line, text line coordinate, block box) from pdf file
    Parameters:
        pdf_file_path {str} : input pdf file path
    Returns:
        text_extracted_data {dictonary} : dictonary of textual data information
    """
    text_extracted_data = {}
    page_width , page_height = 0, 0
    cnt = 0
    for pdf_path in pdf_files:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                page_width, page_height = int(page.rect.width), int(page.rect.height)
                if DEBUG_DPI_BOX_ADJUST:
                    ajusted_height_width = AdjustTextbbox([page_width, page_height])
                    page_width, page_height = ajusted_height_width
                # print("Page Height and width : ",page.rect.width, page.rect.height)
                # page_dic = page.getText('dict')
                data = page.getText('dict')
                text_extracted_data[page_list[cnt]] = data
                cnt+=1      
    return text_extracted_data, (page_width , page_height)

def process_prompt(data):

    text_list = []
    for line in data["lines"]:
        # print(line["spans"][0]["text"])
        for span in line["spans"]:
            t_text = span["text"]
            text_list.append(t_text)
        # text+= " "+line["spans"][0]["text"]
    # print(text.strip())
    # print(text_list)
    text = " ".join(i for i in text_list)
    # print(text)
    return text.strip()

def process_complemtion(data):
    text_list = []
    for block in data:
        for line in block["lines"]:
            line_text = []
            for span in line["spans"]:
                t_text = span["text"]
                line_text.append(t_text)
            l_text = "\n".join(i for i in line_text)
            print(l_text)
            text_list.append(l_text)
    text = "\n".join(i for i in text_list)
    return text.strip()


def prompt_complemtion_json_formate(prompt_:dict={}, completion_:dict={}):
    # print(prompt_)
    # text = ""
    # for line in prompt_["lines"]:
    #     # print(line["spans"][0]["text"])
    #     text+= " "+line["spans"][0]["text"]
    # print(text.strip())
    prompt_text = process_prompt(prompt_)
    # print(prompt_text)
    # print(completion_)
    completion_text = process_complemtion(completion_)
    # print(completion_text)
    prompt_completion_process_data = {"prompt":"Article Title:"+prompt_text+"\nArticle:", "completion":completion_text}
    return prompt_completion_process_data


if __name__ == "__main__":
    pdf_path ="logs/pdf"
    img_path ="logs/images"
    output_draw = "logs/draw_logs/"
    os.makedirs(output_draw, exist_ok=True)
    pdf_files = glob.glob(pdf_path+"/*.pdf")
    data_dict = {}
    cnt = 0
    pdf_files, images = [], []
    # page_list = [186, 187]
    page_list = [i for i in range(Rick_Steves_Paris, 1300)]
    for i in page_list:
        # pdf_name = f"Berlitz Paris Pocket Guide (Guides, Insight) (z-lib.org)_{i}.pdf"
        pdf_name = f"Rick Steves Paris 2019 (Rick Steves, Steve Smith, Gene Openshaw),.pdf (z-lib.org)_{i}.pdf"
        pdf_file = os.path.join(pdf_path, pdf_name) 
        # print(pdf_file)
        pdf_files.append(pdf_file)
        image_name = (pdf_name[:-4]+".png")
        image_file_path = os.path.join(img_path,pdf_name[:-4]+".png")
        image = cv2.imread(image_file_path)
        images.append(image)
        print(f'Processed file :{cnt}/{len(pdf_files)}')
        cnt+=1

    text_extracted_data, page_dim = text_region_extraction(pdf_files, page_list)
    prompt_completion, unique_page = block_operations(text_extracted_data, page_list, images, page_dim)
    # cnt= 0
    # print(unique_page)
    prompt_index, prompt_index_list = 0, []
    for p_m in prompt_completion:
        status = p_m["status"]
        if status=="Prompt":
            prompt_index_list.append(prompt_index)
        page_number = p_m["page_number"]
        page_index = unique_page.index(page_number)
        # print(p_m["page_number"], page_index)
        image = block_draw(images[page_index], p_m)
        images[page_index] = image
        prompt_index+=1
    for i in range(len(page_list)):
        print(i)
        cv2.imwrite(output_draw+str(page_list[i])+".jpg", images[i])
    # print(prompt_index_list)
    # print(len(prompt_index_list))
    # print(len(prompt_index_list)-1)
    prompt_complention_json = []
    for i in range(len(prompt_index_list)-1):
        current_prompt_index = prompt_index_list[i]
        next_prompt_index = prompt_index_list[i+1]
        # print(current_prompt_index, next_prompt_index)
        # print("============================== prompt =====================================")
        # print(prompt_completion[current_prompt_index])
        # print("================================= completion ========================================")
        # print(prompt_completion[current_prompt_index+1:next_prompt_index])
        # print("==================== end prompt ======================================================")

        prompt_completion_dict = prompt_complemtion_json_formate(
            prompt_ = prompt_completion[current_prompt_index],
            completion_ = prompt_completion[current_prompt_index+1:next_prompt_index]
            )
        prompt_complention_json.append(prompt_completion_dict)
    # print("last prompt : ", prompt_completion[prompt_index_list[-1]])
    # print("last completion : ", prompt_completion[prompt_index_list[-1]+1:])
    prompt_completion_dict = prompt_complemtion_json_formate(
            prompt_ = prompt_completion[prompt_index_list[-1]],
            completion_ = prompt_completion[prompt_index_list[-1]+1:]
            )
    prompt_complention_json.append(prompt_completion_dict)
    # print(dict(prompt_complention_json))  

        # print(text_extracted_data)
    # DrawTextAndOval(image, text_extracted_data, image_name= pdf_name[:-4]+".jpg") 
        # print(text_extracted_data)
    # data_dict[image_name] = text_extracted_data
    
        
    
    with open('logs/Rick_Steves_Paris.json', 'w', encoding ='utf8') as json_file:
        json.dump(prompt_complention_json, json_file, ensure_ascii = False, indent=4)