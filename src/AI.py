from detection.yolov5.ex3_ob import object_detection
from detection.CRAFT.ex_c import craft_crop
from ocr.function import ocr
from detection.CRAFT.craft_coordinate2 import crop_text_areas
import os, sys
import shutil
image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']

def delete_all(directory):
    # 폴더 존재 확인
    if not os.path.exists(directory):
        print("지정한 폴더가 존재하지 않습니다.")
        return

    # 폴더 내의 모든 파일과 하위 디렉토리를 나열하고 삭제
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            os.remove(item_path)  # 파일 삭제
            # print(f"{item} 파일이 삭제되었습니다.")
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)  # 디렉토리와 내부 파일 삭제
            # print(f"{item} 디렉토리가 삭제되었습니다.")

    # print("모든 파일 및 디렉토리가 제거되었습니다.")

image_number = 0
def AI(filename:str, a=0.3, b=0.3, c=0.1):
    global image_number
    
    base_path = os.getcwd()
    target_file = "result.jpg"
    print("filename : ", filename)
    print("hyper : a:",a, "b:",b, "c:",c)
    image_name = filename.split('.')[0]
    postfix = filename.split('.')[1]
    
    print("경로 : ", base_path)
    delete_all(f'{base_path}/result/')
    object_detection(image_path=f'{base_path}/images/{image_name}.{postfix}',output_path=f'{base_path}/result/result_obejct')
    craft_crop(object_image_folder=f'{base_path}/result/result_obejct',crop_result_folder=f'{base_path}/result/result_crop', a=a, b=b, c=c)
    crop_text_areas(img_path=f'{base_path}/result/result_obejct/', txt_path=f'{base_path}/result/result_crop', base_save_dir=f'{base_path}/result/result_crop/crop_image' )
    result = ocr(input_crop_folder = f'{base_path}/result/result_crop/crop_image')
    
    from_file_path = f'{base_path}/result/result_crop/{image_name}.jpg'
    to_file_path = f'{base_path}/images/{image_number}{target_file}'
    shutil.copyfile(from_file_path, to_file_path)
    result["image_path"] = f'/static/{image_number}{target_file}'
    
    image_number = image_number+1
    return result

def AI_TEST():
    base_path = os.getcwd()
    print("경로 : ", base_path)
    delete_all(f'{base_path}/result/')
    object_detection(image_path=f'{base_path}/images/*',output_path=f'{base_path}/result/result_obejct')
    craft_crop(object_image_folder=f'{base_path}/result/result_obejct',crop_result_folder=f'{base_path}/result/result_crop')
    crop_text_areas(img_path=f'{base_path}/result/result_obejct/', txt_path=f'{base_path}/result/result_crop', base_save_dir=f'{base_path}/result/result_crop/crop_image' )
    result = ocr(input_crop_folder = f'{base_path}/result/result_crop/crop_image')
    return result

# a = AI()
# print(a)