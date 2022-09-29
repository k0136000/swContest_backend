# 본 코드는 탬플릿 매칭 기법을 활용한 악보 해석 프로그램이다.

import sys
import subprocess
import cv2
import numpy as np


from rectangle import Rectangle
from best_fit import fit
from note import Note
from random import randint

from PIL import ImageFont, ImageDraw, Image



staff_files = [
        "cv_note/resources/template/staff4.png",
        "cv_note/resources/template/staff3.png",
    "cv_note/resources/template/staff2.png", 
    "cv_note/resources/template/staff.png"]
quarter_files = [
    "cv_note/resources/template/quarter.png", 
    "cv_note/resources/template/solid-note.png"]
sharp_files = [
    "cv_note/resources/template/sharp.png"]
flat_files = [
    "cv_note/resources/template/flat-line2.png",
    "cv_note/resources/template/flat-line.png", 
    "cv_note/resources/template/flat-space.png" ]
half_files = [
    "cv_note/resources/template/half-space.png", 
    "cv_note/resources/template/half-note-line.png",
    "cv_note/resources/template/half-line.png", 
    "cv_note/resources/template/half-note-space.png"]
whole_files = [
    "cv_note/resources/template/whole-space.png", 
    "cv_note/resources/template/whole-note-line.png",
    "cv_note/resources/template/whole-line.png", 
    "cv_note/resources/template/whole-note-space.png"]


#탬플릿 파일을 각 리스트에 저장.
staff_imgs = [cv2.imread(staff_file, 0) for staff_file in staff_files]
quarter_imgs = [cv2.imread(quarter_file, 0) for quarter_file in quarter_files]
sharp_imgs = [cv2.imread(sharp_files, 0) for sharp_files in sharp_files]
flat_imgs = [cv2.imread(flat_file, 0) for flat_file in flat_files]
half_imgs = [cv2.imread(half_file, 0) for half_file in half_files]
whole_imgs = [cv2.imread(whole_file, 0) for whole_file in whole_files]

#각 탬플릿을 리사이징할 상한선. 탬플릿이 일치함의 임계값.
staff_lower, staff_upper, staff_thresh = 50, 150, 0.77
sharp_lower, sharp_upper, sharp_thresh = 50, 150, 0.70
flat_lower, flat_upper, flat_thresh = 50, 150, 0.77
quarter_lower, quarter_upper, quarter_thresh = 50, 150, 0.70
half_lower, half_upper, half_thresh = 50, 150, 0.70
whole_lower, whole_upper, whole_thresh = 50, 150, 0.70

# def put_text(image, text, loc):
def put_text(image, text, loc_x,loc_y):
    """
    이미지와 텍스트, 입력할 좌표를 입력받아 흰색 픽셀로 텍스트를 적어주는 함수
    """
    image = Image.fromarray(image)
    draw = ImageDraw.Draw(image)
    draw.text(loc_x,loc_y,str(text),ImageFont.truetype("font/gulim.ttf", 48))
    #font = cv2.FONT_HERSHEY_SIMPLEX
    #cv2.putText(image, str(text), loc, font, 0.6, (255, 0, 0), 2)
    
    return image
def locate_images(img, templates, start, stop, threshold):
    """
    탬플릿의 최적의 크기와, 탬플릿과 매칭된 객체를 이용해 Rectangle 객체를 생성하여 리스트에 넣은후 반환하는 함수.
    """
    #탬플릿과 일치하는 픽셀의 좌표, 탬플릿의 최적의 크기를 리턴받음.
    locations, scale = fit(img, templates, start, stop, threshold)
    img_locations = []
    
    for i in range(len(templates)):
        #탬플릿의 너비, 높이 정보를 가져옴.
        w, h = templates[i].shape[::-1]
        #최적의 크기만큼 템플릿의 크기를 지정함.
        w *= scale
        h *= scale
        #검출된 객체를 이용하여 Rectangle 클래스에 x좌표,y좌표,너비,높이 값을 넣어 새로운 Rectangle객체를 사용하여 img_location에 append
        img_locations.append([Rectangle(pt[0], pt[1], w, h) for pt in zip(*locations[i][::-1])])
    #객체들을 이용해 형성한 Rectangle 리스트를 리턴.
    return img_locations

def merge_recs(recs, threshold):
    """
    객체들 의 영역을 합치는 함수.
    """
    filtered_recs = []
    while len(recs) > 0:
        r = recs.pop(0)
        recs.sort(key=lambda rec: rec.distance(r))
        merged = True
        while(merged):
            merged = False
            i = 0
            for _ in range(len(recs)):
                if r.overlap(recs[i]) > threshold or recs[i].overlap(r) > threshold:
                    r = r.merge(recs.pop(i))
                    merged = True
                elif recs[i].distance(r) > r.w/2 + recs[i].w/2:
                    break
                else:
                    i += 1
        filtered_recs.append(r)
    return filtered_recs

def open_file(path):
    cmd = {'linux':'eog', 'win32':'explorer', 'darwin':'open'}[sys.platform]
    subprocess.run([cmd, path])

# 경로를 파라미터로 받음
def run(path):
    
    #이미지 불러오기(이진화 과정)
    img_file = path
    img = cv2.imread(img_file, cv2.IMREAD_GRAYSCALE)
    img_gray = img
    img = cv2.cvtColor(img_gray,cv2.COLOR_GRAY2RGB)
    #어짜피 악보는 흑 백이 대부분이므로 오츠 알고리즘 대신 임계값을 127로 지정해 줌.
    ret,img_gray = cv2.threshold(img_gray,127,255,cv2.THRESH_BINARY)
    img_width, img_height = img_gray.shape[::-1]

    #오선 탐색
    print("Matching staff image...")
    #staff_recs에는 staff와 매칭된 객체들로 Rectangle객체들을 만들어 모은 리스트가 저장됨.
    staff_recs = locate_images(img_gray, staff_imgs, staff_lower, staff_upper, staff_thresh)

    #약한 오선? 필터링
    print("Filtering weak staff matches...")

    staff_recs = [j for i in staff_recs for j in i]

    #객체들을 하나씩 가져와서 객체의 높이 값을 모아 리스트를 형성.
    heights = [r.y for r in staff_recs] + [0]
    
    #객체들의 최대 높이
    histo = [heights.count(i) for i in range(0, max(heights) + 1)]
    avg = np.mean(list(set(histo)))
    staff_recs = [r for r in staff_recs if histo[r.y] > avg]

    print("Merging staff image results...")
    staff_recs = merge_recs(staff_recs, 0.01)
    #검출된 객체를 표시하기 위해 원본 이미지에서 복사
    staff_recs_img = img.copy()
    
    #staff_recs안에 있는 객체 모두 사각형 그리기.
    for r in staff_recs:
        r.draw(staff_recs_img, (0, 0, 255), 2)
    #오선의 위치 탐색
    print("Discovering staff locations...")
    #오선 객체들 합치기
    staff_boxes = merge_recs([Rectangle(0, r.y, img_width, r.h) for r in staff_recs], 0.01)
    
    #조표(샵) 탬플릿 매칭
    print("Matching sharp image...")
    sharp_recs = locate_images(img_gray, sharp_imgs, sharp_lower, sharp_upper, sharp_thresh)

    #매칭된 객체 합치기
    print("Merging sharp image results...")
    sharp_recs = merge_recs([j for i in sharp_recs for j in i], 0.5)
    sharp_recs_img = img.copy()
        
    #플랫 탬플릿 매칭
    print("Matching flat image...")
    flat_recs = locate_images(img_gray, flat_imgs, flat_lower, flat_upper, flat_thresh)

    #객체 합치기
    print("Merging flat image results...")
    flat_recs = merge_recs([j for i in flat_recs for j in i], 0.5)

    #4분의 1음표 검출
    print("Matching quarter image...")
    quarter_recs = locate_images(img_gray, quarter_imgs, quarter_lower, quarter_upper, quarter_thresh)

    print("Merging quarter image results...")
    quarter_recs = merge_recs([j for i in quarter_recs for j in i], 0.5)
    
    
    #반음표 검출
    print("Matching half image...")
    half_recs = locate_images(img_gray, half_imgs, half_lower, half_upper, half_thresh)

    print("Merging half image results...")
    half_recs = merge_recs([j for i in half_recs for j in i], 0.5)

    #비어있는 음표 검출
    print("Matching whole image...")
    whole_recs = locate_images(img_gray, whole_imgs, whole_lower, whole_upper, whole_thresh)

    print("Merging whole image results...")
    whole_recs = merge_recs([j for i in whole_recs for j in i], 0.5)

    note_groups = []
    #오선 객체를 둘러싼 박스를 하나씩 넣어
    for box in staff_boxes:
        """
        r = 객체
        sharp = 객체 이름
        """
        staff_sharps = [Note(r, "sharp", box) 
            for r in sharp_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        staff_flats = [Note(r, "flat", box) 
            for r in flat_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        quarter_notes = [Note(r, "4,8", box, staff_sharps, staff_flats) 
            for r in quarter_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        half_notes = [Note(r, "2", box, staff_sharps, staff_flats) 
            for r in half_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        whole_notes = [Note(r, "1", box, staff_sharps, staff_flats) 
            for r in whole_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        staff_notes = quarter_notes + half_notes + whole_notes
        staff_notes.sort(key=lambda n: n.rec.x)
        staffs = [r for r in staff_recs if r.overlap(box) > 0]
        staffs.sort(key=lambda r: r.x)
        note_color = (randint(0, 255), randint(0, 255), randint(0, 255))
        note_group = []
        i = 0; j = 0;
        while(i < len(staff_notes)):
            if (staff_notes[i].rec.x > staffs[j].x and j < len(staffs)):
                r = staffs[j]
                j += 1;
                if len(note_group) > 0:
                    note_groups.append(note_group)
                    note_group = []
                note_color = (randint(0, 255), randint(0, 255), randint(0, 255))
            else:
                note_group.append(staff_notes[i])
                staff_notes[i].rec.draw(img, note_color, 2)
                i += 1
        note_groups.append(note_group)
   
    for note_group in note_groups:
        # 노트 , 객체의 이름 (ex-> 2분음표 : 2, 4,8음표 -> 4,8
        for note in note_group:
            print(str(note.note) + " | "+ str(note.sym) + " | " + str(note.pitch))
            #img=put_text(img, note.note_kor, (note.rec.x,note.rec.y+80))
            img=put_text(img, note.note_kor, note.rec.x,note.rec.y+80)
                    
    return img