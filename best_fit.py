import cv2
import numpy as np

def fit(img, templates, start_percent, stop_percent, threshold):
    """
    탬플릿이 원본 이미지와 같은 비율의 크기를 가질 수 있도록 계속해서 리사이징하는 함수.

    img = 원본 이미지
    templates = 탬플릿 이미지
    start_percent = 시작 비율
    stop_percent = 끝 비율
    threshold = 임계값.
    """
    #탐색할 이미지 크기 저장
    img_width, img_height = img.shape[::-1]

    best_location_count = -1
    best_locations = []
    best_scale = 1


    x = []
    y = []

    #크기를 1/2에서 3/2까지 키워보기
    #탬플릿 이미지가 악보 이미지에 맞아 탐색이 가능하게 될때 까지 리사이징하는것.
    for scale in [i/100.0 for i in range(start_percent, stop_percent + 1, 3)]:
        locations = []
        location_count = 0
        #샘플리스트를 하나씩 꺼내서
        for template in templates:

            """
            이미지 리사이징 함수

            탬플릿 이미지를 축소or확대 비율만큼 리사이징
            """
            template = cv2.resize(template, None,
                fx = scale, fy = scale, interpolation = cv2.INTER_CUBIC)
    
            """
            탬플릿 매칭 함수

            cv2.matchTemplate(image, templ, method, result=None, mask=None) -> result
            image= 입력 영상
            templ= 탬플릿 영상
            method = 비교 방법
            mask = 입력 영상 전체에서 탬플릿 매칭을 할지, 일부분에서만 탬플릿 매칭을 할지 결정하는 인자
            result = 비교 결과 행렬값을 반환
            """
            result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)

            #결과 행렬에서 임계값을 넘는 인덱스가 있는지 탐색, array 값을 반환함.
            #임계값을 넘긴 결과 행렬값만 담김.
            result = np.where(result >= threshold)

            #결과 행렬에서 임계값보다 큰 값들의 길이를 location_count에 저장.
            location_count += len(result[0])

            #탬플릿과 일치하는 인덱스(임계값을 넘긴 값들)을 loaction에 저장.
            locations += [result]
        
        #scale 정도의 크기로 탬플릿 이미지를 리사이징 했을때 몇개의 객체를 맞추었는지 출력함.
        print("scale: {0}, hits: {1}".format(scale, location_count)) 
        
        #리스트 x에 맞춘 개수, y에 크기를 넣음
        x.append(location_count)
        y.append(scale)

        #만약 현 best_location_count보다 location_count가 크다면
        #best_location_count, best_locations, scale(템플릿의 크기) 업데이트

        if (location_count > best_location_count):
            best_location_count = location_count
            best_locations = locations
            best_scale = scale
   
        elif (location_count < best_location_count):
            pass

    #임계값을 가장 많이 넘겼을때의 값들, 그때의 크기를 리턴. 
    return best_locations, best_scale