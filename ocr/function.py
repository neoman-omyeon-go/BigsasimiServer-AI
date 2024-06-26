from ocr.demo import demo
import string
import argparse
import torch
import torch.backends.cudnn as cudnn
import torch.utils.data
import torch.nn.functional as F
import re

import os
from ocr.utils import CTCLabelConverter, AttnLabelConverter
from ocr.dataset import RawDataset, AlignCollate
from ocr.model import Model

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

base_path = os.getcwd()
parser = argparse.ArgumentParser()
parser.add_argument('--image_folder',  help='path to image_folder which contains text images',default=f'{base_path}/result/result_crop/')
parser.add_argument('--workers', type=int, help='number of data loading workers', default=0)
parser.add_argument('--batch_size', type=int, default=192, help='input batch size')
parser.add_argument('--saved_model',  help="path to saved_model to evaluation", default=f'{base_path}/ocr/best_accuracy.pth')
""" Data processing """
parser.add_argument('--batch_max_length', type=int, default=25, help='maximum-label-length')
parser.add_argument('--imgH', type=int, default=32, help='the height of the input image')
parser.add_argument('--imgW', type=int, default=100, help='the width of the input image')
parser.add_argument('--rgb', action='store_true', help='use rgb input')


parser.add_argument('--character', type=str, default='0123456789abcdefghijklmnopqrstuvwxyz가각간갇갈'
                                '감갑값갓강갖같갚갛개객걀걔거걱건걷걸검겁것겉게겨격겪견'
                                '결겹경곁계고곡곤곧골곰곱곳공과관광괜괴굉교구국군굳굴굵'
                                '굶굽궁권귀귓규균귤그극근글긁금급긋긍기긴길김깅깊까깍깎'
                                '깐깔깜깝깡깥깨꺼꺾껌껍껏껑께껴꼬꼭꼴꼼꼽꽂꽃꽉꽤꾸꾼꿀'
                                '꿈뀌끄끈끊끌끓끔끗끝끼낌나낙낚난날낡남납낫낭낮낯낱낳내'
                                '냄냇냉냐냥너넉넌널넓넘넣네넥넷녀녁년념녕노녹논놀놈농높'
                                '놓놔뇌뇨누눈눕뉘뉴늄느늑는늘늙능늦늬니닐님다닥닦단닫달'
                                '닭닮담답닷당닿대댁댐댓더덕던덜덟덤덥덧덩덮데델도독돈돌'
                                '돕돗동돼되된두둑둘둠둡둥뒤뒷드득든듣들듬듭듯등디딩딪따'
                                '딱딴딸땀땅때땜떠떡떤떨떻떼또똑뚜뚫뚱뛰뜨뜩뜯뜰뜻띄라락'
                                '란람랍랑랗래랜램랫략량러럭런럴럼럽럿렁렇레렉렌려력련렬'
                                '렵령례로록론롬롭롯료루룩룹륨룻뤄류륙롤률륭르른름릇릎리릭린'
                                '림립릿링마막만많말맑맘맙맛망맞맡맣매맥맨맵맺머먹먼멀멈'
                                '멋멍멎메멘멩며면멸명몇모목몬몰몸몹못몽묘무묵묶문묻물뭄'
                                '뭇뭐뭘뭣므미민믿밀밉밌및밑바박밖반받발밝밟밤밥방밭배백'
                                '뱀뱃뱉버번벌범법벗베벤벨벼벽변별볍병볕보복볶본볼봄봇봉'
                                '뵈뵙부북분불붉붐붓붕붙뷰브븐블비빌빔빗빚빛빠빡빨빵빼뺏'
                                '뺨뻐뻔뻗뼈뼉뽑뿌뿐쁘쁨사삭산살삶삼삿상새색샌생샤서석섞'
                                '선설섬섭섯성세섹센셈셋셔션소속손솔솜솟송솥쇄쇠쇼수숙순'
                                '숟술숨숫숭숲쉬쉰쉽슈스슨슬슴습슷승시식신싣실싫심십싯싱'
                                '싶싸싹싼쌀쌍쌓써썩썰썹쎄쏘쏟쑤쓰쓴쓸씀씌씨씩씬씹씻아악'
                                '안앉않알앓암압앗앙앞애액앨야약얀얄얇양얕얗얘어억언얹얻'
                                '얼엄업없엇엉엊엌엎에엔엘여역연열엷염엽엿영옆예옛오옥온'
                                '올옮옳옷옹와완왕왜왠외왼요욕용우욱운울움웃웅워원월웨웬'
                                '위윗유육율으윽은을음응의이익인일읽잃임입잇있잊잎자작잔'
                                '잖잘잠잡잣장잦재쟁쟤저적전절젊점접젓정젖제젠젯져조족존'
                                '졸좀좁종좋좌죄주죽준줄줌줍중쥐즈즉즌즐즘증지직진질짐집'
                                '짓징짙짚짜짝짧째쨌쩌쩍쩐쩔쩜쪽쫓쭈쭉찌찍찢차착찬찮찰참'
                                '찻창찾채책챔챙처척천철첩첫청체쳐초촉촌촛총촬최추축춘출'
                                '춤춥춧충취츠측츰층치칙친칠침칫칭카칸칼캄캐캠커컨컬컴컵'
                                '컷케켓켜코콘콜콤콩쾌쿄쿠퀴크큰클큼키킬타탁탄탈탑탓탕태'
                                '택탤터턱턴털텅테텍텔템토톤톨톱통퇴투툴툼퉁튀튜트특튼튿'
                                '틀틈티틱팀팅파팎판팔팝패팩팬퍼퍽페펜펴편펼평폐포폭폰표'
                                '푸푹풀품풍퓨프플픔피픽필핏핑하학한할함합항해핵핸햄햇행'
                                '향허헌험헤헬혀현혈협형혜호혹혼홀홈홉홍화확환활황회획횟'
                                '횡효후훈훌훔훨휘휴흉흐흑흔흘흙흡흥흩희흰히힘?!%.', help='character label')
parser.add_argument('--sensitive', action='store_true', help='for sensitive character mode')
parser.add_argument('--PAD', action='store_true', help='whether to keep ratio then pad for image resize')
""" Model Architecture """
parser.add_argument('--Transformation', type=str,  help='Transformation stage. None|TPS',default = 'TPS')
parser.add_argument('--FeatureExtraction', type=str, help='FeatureExtraction stage. VGG|RCNN|ResNet', default='ResNet')
parser.add_argument('--SequenceModeling', type=str,  help='SequenceModeling stage. None|BiLSTM', default = 'BiLSTM')
parser.add_argument('--Prediction', type=str,  help='Prediction stage. CTC|Attn', default='Attn')
parser.add_argument('--num_fiducial', type=int, default=20, help='number of fiducial points of TPS-STN')
parser.add_argument('--input_channel', type=int, default=1, help='the number of input channel of Feature extractor')
parser.add_argument('--output_channel', type=int, default=512,
                    help='the number of output channel of Feature extractor')
parser.add_argument('--hidden_size', type=int, default=256, help='the size of the LSTM hidden state')

opt = parser.parse_args()

""" vocab / character number configuration """
if opt.sensitive:
    opt.character = string.printable[:-6]  # same with ASTER setting (use 94 char).

cudnn.benchmark = True
cudnn.deterministic = True
opt.num_gpu = torch.cuda.device_count()

base_path = os.getcwd()

# def ocr(input_crop_folder):
#     # input_crop_folder
#     demo(opt)
    
#     with open(f'{base_path}/result/demo.txt', 'r') as file:
#         # 파일의 내용을 읽기
#         data = file.read()
        
#         # 파일 내용 출력
#     words = data.replace('\t',' ').split(' ')  # 탭 문자를 기준으로 분할
#     # words = data.split(' ')
#     possible_misspellings = {
#         '당류': ['당류', '단류', '단유', '당뉴', '당루', '단루', '당누'],
#         '나트륨': ['나트륨', '나튬', '날툼', '남트윰', '남튬', '나트름', '나트융', '나트윰','나트통'],
#         '탄수화물': ['탄수화물', '탄수화무', '탄수화믈', '탄수화몰', '탄수와믈', '탄수와몰', '단수와물', '탄수와물', '단수외울', '단수와몰'],
#         '단백질': ['단백질', '단밴질', '단뱅질', '단백진', '단백지', '단배질', '당백질'],
#         '지방': ['지방', '지빙', '지벙', '지바', '지밤', '지빔'],
#         'kcal': ['kcal', 'kcol', 'koal', 'kool', 'kccl', 'kaal','kca','cal'],
#         '콜레스테롤': ['콜레스테롤', '콜래스테롤', '콜래스태롤', '쿨레스테롤', '쿨레스테룰', '쿨래스테로', '콜레스', '콜레스테루']
#     }

#     nutrition_dict = {}

#     # OCR 데이터 처리 및 값 추출
#     for key, misspellings in possible_misspellings.items():
#         if key in nutrition_dict:
#             continue  # 이미 키 값이 존재하는 경우 건너뜀

#         for misspelling in misspellings:
#             for i, word in enumerate(words):
#                 if key == 'kcal':
#                     # kcal의 경우 숫자가 앞에 위치
#                     if re.match(r'^\d+$', word) and i + 1 < len(words) and words[i + 1] in misspelling:
#                         nutrition_dict[key] = word
#                         break
#                 else:
#                     # 나머지 경우 키워드 뒤에 숫자가 위치
#                     if word in misspelling and i + 1 < len(words):
#                         next_word = words[i + 1]
#                         if re.match(r'^\d+(\.\d+)?$', next_word):  # 숫자 또는 소수 형태
#                             nutrition_dict[key] = next_word
#                             break
#                         elif re.match(r'^\d+(\.\d+)?[a-zA-Z]*$', next_word):  # 숫자와 단위가 함께 있는 형태
#                             match = re.match(r'^(\d+(\.\d+)?)[a-zA-Z]*$', next_word)
#                             if match:
#                                 nutrition_dict[key] = match.group(1)
#                                 break
#                         elif key == '지방' and re.match(r'^\d+\.[a-zA-Z]*$', next_word):  # '지방' 특수 케이스
#                             match = re.match(r'^(\d+)\.[a-zA-Z]*$', next_word)
#                             if match:
#                                 nutrition_dict[key] = match.group(1)
#                                 break
#             if key in nutrition_dict:  # 일치하는 요소를 찾았으면 다음 키워드로 넘어감
#                 break

#     # 키 값에 대한 인식이 없는 경우 0으로 설정
#     for key in possible_misspellings:
#         if key not in nutrition_dict:
#             nutrition_dict[key] = '0'

#     return nutrition_dict

def ocr(input_crop_folder):
    # input_crop_folder
    demo(opt)

    with open(f'{base_path}/result/demo.txt', 'r') as file:
        # 파일의 내용을 읽기
        data = file.read()
        
        # 파일 내용 출력
    words = data.replace('\t', ' ').split(' ')  # 탭 문자를 기준으로 분할

    possible_misspellings = {
        '당류': ['당류', '단류', '단유', '당뉴', '당루', '단루', '당누'],
        '나트륨': ['나트륨', '나트류', '나튬', '날툼', '남트윰', '남튬', '나트름', '나트융', '나트윰', '나트통'],
        '탄수화물': ['탄수화물', '탄수화무', '탄수화믈', '탄수화몰', '탄수와믈', '탄수와몰', '단수와물', '탄수와물', '단수외울', '단수와몰'],
        '단백질': ['단백질', '단밴질', '단뱅질', '단백진', '단백지', '단배질', '당백질'],
        '지방': ['지방', '지빙', '지벙', '지바', '지밤', '지빔'],
        'kcal': ['kcal', 'kcol', 'koal', 'kool', 'kccl', 'kaal', 'kca', 'cal'],
        '콜레스테롤': ['콜레스테롤', '콜래스테롤', '콜래스태롤', '쿨레스테롤', '쿨레스테룰', '쿨래스테로', '콜레스', '콜레스테루','콜레스데콜']
    }

    nutrition_dict = {}

    # OCR 데이터 처리 및 값 추출
    for key, misspellings in possible_misspellings.items():
        for misspelling in misspellings:
            for i, word in enumerate(words):
                if key == 'kcal':
                    # kcal의 경우 숫자가 앞에 위치
                    if re.match(r'^\d+$', word) and i + 1 < len(words) and words[i + 1] == misspelling:
                        nutrition_dict[key] = word
                        break
                else:
                    # 나머지 경우 키워드 뒤에 숫자가 위치
                    if word == misspelling and i + 1 < len(words):
                        next_word = words[i + 1]
                        if re.match(r'^\d+(\.\d+)?$', next_word) or re.match(r'^\d+\.$', next_word):  # 숫자 또는 소수 형태
                            if key not in nutrition_dict:  # 처음 찾은 값만 저장
                                nutrition_dict[key] = next_word.rstrip('.')
                            break
                        elif re.match(r'^\d+(\.\d+)?[a-zA-Z]*$', next_word):  # 숫자와 단위가 함께 있는 형태
                            match = re.match(r'^(\d+(\.\d+)?)[a-zA-Z]*$', next_word)
                            if match and key not in nutrition_dict:  # 처음 찾은 값만 저장
                                nutrition_dict[key] = match.group(1)
                            break
                        elif key == '지방' and re.match(r'^\d+\.[a-zA-Z]*$', next_word):  # '지방' 특수 케이스
                            match = re.match(r'^(\d+)\.[a-zA-Z]*$', next_word)
                            if match and key not in nutrition_dict:  # 처음 찾은 값만 저장
                                nutrition_dict[key] = match.group(1)
                            break

# 키 값에 대한 인식이 없는 경우 0으로 설정
    for key in possible_misspellings:
        if key not in nutrition_dict:
            nutrition_dict[key] = '0'
    return nutrition_dict
