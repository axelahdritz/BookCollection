import pytesseract
from pytesseract import Output
import pandas as pd
from PIL import Image, ImageOps
import numpy as np
import cv2
import os

def ocr(img, lang, left, top, right, bottom):
    # open image, crop image, and split the image
    options = "--oem 1 --psm 6 -l {}".format(lang)
    image=Image.open(img)
    image=image.crop((left,top,right,bottom))
    image.save(img)
    image=image.convert('L')
    text = pytesseract.image_to_string(image, config=options)
    #os.remove(img)
    return text

def ocr_data_eng(img, lang, left, top, right, bottom):
    options = "-c preserve_interword_spaces=1 --oem 1 -l {}".format(lang)
    image=Image.open(img)
    image=image.crop((left,top,right,bottom))
    imageBox = image.getbbox()
    image = image.crop(imageBox)
    image.save('temp.png')
    filename1, filename2 = split_image('temp.png')
    os.remove('temp.png')
    image1 = Image.open(filename1)
    image2 = Image.open(filename2)
    image1=image1.convert('L')
    image2=image2.convert('L')
    text1 = pytesseract.image_to_data(image1, config=options, output_type=Output.DICT)
    text2 = pytesseract.image_to_data(image2, config=options, output_type=Output.DICT)
    image_data = [text1,text2]
    return image_data, filename1, filename2

def ocr_data_swe(img, lang, left, top, right, bottom, is_white=False, is_pdf=True):
    # open image, crop image, and split the image
    options = "-c preserve_interword_spaces=1 --oem 1 -l {}".format(lang)
    filename = 'temp_swe.png'
    image=Image.open(img)
    image=image.crop((left,top,right,bottom))
    if is_white:
        image=image.convert('L')
        invert_im = ImageOps.invert(image)
        imageBox = invert_im.getbbox()
        if not is_pdf:
            imageBox = (imageBox[0]-25, imageBox[1]-25, imageBox[2]+25, imageBox[3]+25)
    else:
        imageBox = image.getbbox()
    image = image.crop(imageBox)
    image_data = pytesseract.image_to_data(image, config=options, output_type=Output.DICT)
    image.save(filename)
    return image_data, filename

def add_spaces(df):
    df1 = df[(df.conf != '-1')&(df.text!=' ')&(df.text!='')]
    # sort blocks vertically
    sorted_blocks = df1.groupby('block_num').first().sort_values('top').index.tolist()
    for block in sorted_blocks:
        curr = df1[df1['block_num']==block]
        sel = curr[curr.text.str.len()>3]
        char_w = (sel.width/sel.text.str.len()).mean()
        prev_par, prev_line, prev_left = 0, 0, 0
        text = ''
        for ix, ln in curr.iterrows():
            # add new line when necessary
            if prev_par != ln['par_num']:
                text += '\n'
                prev_par = ln['par_num']
                prev_line = ln['line_num']
                prev_left = 0
            elif prev_line != ln['line_num']:
                text += '\n'
                prev_line = ln['line_num']
                prev_left = 0
            added = 0  # num of spaces that should be added
            if ln['left']/char_w > prev_left + 1:
                added = int((ln['left'])/char_w) - prev_left
                text += ' ' * added 
            text += ln['text'] + ' '
            prev_left += len(ln['text']) + added + 1
        text += '\n'
        print(text)

def get_bounds(image_data, is_swe_pdf=True):
    is_empty = False
    # convert to dataframe and remove frames
    df = pd.DataFrame(image_data)
    df = df[(df.conf !='-1')&(df.text!=' ')&(df.text!='')]

    if df.empty:
        is_empty = True
        return 0, 0, 0, 0, is_empty

    # extract all first words in sentence sequences
    df_first_word = df[df['word_num'] == 1].sort_values('top')

    # extract top_bound
    top = df_first_word['top'].tolist()
    non_zero_top = [int(i) for i in top if int(i) != 0]
    top_bound =  min(non_zero_top) - 25
    while top_bound < 0:
        top_bound += 1
    
    # get average character height
    height_lst = df_first_word['height'].tolist()
    height_adj = df[df['height'] <= np.average(height_lst)]
    height = height_adj['height'].tolist()
    avg_height = np.average(height)
    adjusted_for_height = [i + avg_height for i in non_zero_top]

    # extract bottom_bound
    bottom_bound = max(adjusted_for_height) + 25

    # extract left_bound
    left = df_first_word['left'].tolist()
    non_zero_left = [int(i) for i in left if int(i) != 0]
    leftmost = min(non_zero_left)
    left_bound = leftmost - 25
    while left_bound < 0:
        left_bound += 1

    '''
    # find indented paragraph lines
    text = df_first_word['text'].tolist()
    non_zero_indices = [i for i in range(len(left)) if int(left[i]) !=0]
    text_alt = [text[i] for i in non_zero_indices]
    ind_am = []
    indented_text = []
    threshold1 = leftmost + 30
    threshold2 = leftmost + 100
    for i, num in enumerate(non_zero_left):
        if threshold1 <= num <= threshold2:
            ind_am.append(num - leftmost)
            indented_text.append(text_alt[i])
    '''
    # generate last word list and extract right_bound
    last_words = []
    if not is_swe_pdf:
        sorted_df = df.sort_values(by=['block_num', 'par_num', 'line_num', 'word_num'])
        prev_block, prev_par, prev_line, prev_word = 1, 1, 1, 0
        for ix, ln in sorted_df.iterrows():
            if prev_block != ln['block_num']:
                prev_block = ln['block_num']
                prev_par = ln['par_num']
                prev_line = ln['line_num']
                last_words.append(prev_word)
            elif prev_par != ln['par_num']:
                prev_par = ln['par_num']
                prev_line = ln['line_num']
                last_words.append(prev_word)
            elif prev_line != ln['line_num']:
                prev_line = ln['line_num']
                last_words.append(prev_word)
            prev_word = int(ln['left']) + int(ln['width'])
    else:
        sorted_blocks = df.groupby('block_num').first().sort_values('top').index.tolist()
        for block in sorted_blocks:
            curr = df[df['block_num']==block]
            prev_par, prev_line, prev_word = 1, 1, 0
            for ix, ln in curr.iterrows():
                if prev_par != ln['par_num']:
                    prev_par = ln['par_num']
                    prev_line = ln['line_num']
                    last_words.append(prev_word)
                elif prev_line != ln['line_num']:
                    prev_line = ln['line_num']
                    last_words.append(prev_word)
                prev_word = int(ln['left']) + int(ln['width'])
    if len(last_words) == 0:
        last_words.append(prev_word)
    right_bound = max(last_words) + 25
    return left_bound, top_bound, right_bound, bottom_bound, is_empty

def split_image(img_file):
    img = cv2.imread(img_file)
    width = img.shape[1]
    width_cutoff = width // 2
    s1 = img[:, :width_cutoff]
    s2 = img[:, width_cutoff:]
    filename1 = 'half1.png'
    filename2 = 'half2.png'
    cv2.imwrite(filename1, s1)
    cv2.imwrite(filename2, s2)
    return filename1, filename2

def run_OCR(img, lang, left, top, right, bottom, is_white=False, is_pdf=False, litbank=False):
    if litbank:
        image_data, filename = ocr_data_swe(img, lang, left, top, right, bottom, is_white=is_white, is_pdf=is_pdf)
        left_bound, top_bound, right_bound, bottom_bound, is_empty = get_bounds(image_data, is_swe_pdf=is_pdf)
        if is_empty:
            text = ''
        else:
            text = ocr(filename, 'swe', left_bound, top_bound, right_bound, bottom_bound)
        return text
    else:
        image_data, filename1, filename2 = ocr_data_eng(img, lang, left, top, right, bottom)
        left_bound, top_bound, right_bound, bottom_bound, is_empty= get_bounds(image_data[0])
        if is_empty:
            text1 = ''
        else:
            text1 = ocr(filename1, 'eng', left_bound, top_bound, right_bound, bottom_bound)
        left_bound, top_bound, right_bound, bottom_bound, is_empty = get_bounds(image_data[1])
        if is_empty:
            text2 = ''
        else:
            text2 = ocr(filename2, 'eng', left_bound, top_bound, right_bound, bottom_bound)
        return [text1, text2]