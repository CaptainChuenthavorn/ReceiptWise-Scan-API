from flask import Flask, request, jsonify
import easyocr
import torch
import cv2
import re
import numpy as np
import requests
import os
import datetime
# Regular expression patterns
pattern_only_Thai = r'[ก-๛]+'
pattern_only_Thai_dot = r'[ก-๛.]+'
pattern_start_Num = r'\d.*'
pattern_start_EngNumSpecial = r'[a-zA-Z0-9\\\/]+'
pattern_only_EngNum = r'[a-zA-Z0-9-.()]+'
pattern_accountNumber = r'[a-zA-Z0-9-]+'
pattern_only_ThaiEngNum = r'[ก-๛a-zA-Z0-9-.()]+'
pattern_only_ThaiEng_dot = r'[ก-๛a-zA-Z.()]+'
pattern_realname = r'[ก-๛a-wy-z.]+'


def read_text_files(text_files_directory):
    list_data = []
    for filename in os.listdir(text_files_directory):
        if filename.endswith('.txt'):
            with open(os.path.join(text_files_directory, filename), 'r', encoding='utf-8') as file:
                content = file.read()
                # Define a regular expression pattern to capture data within single quotes
                pattern = r"'(.*?)'"
                # Find all matches of the pattern in the content
                matches = re.findall(pattern, content)
                # Append the matches to the 'list_data' list
                list_data.append(matches)
    return list_data
def read_text_files_name(text_files_directory):
    list_file_name = []
    for filename in os.listdir(text_files_directory):
        if filename.endswith('.txt'):
            with open(os.path.join(text_files_directory, filename), 'r', encoding='utf-8') as file:
                list_file_name.append(os.path.join(text_files_directory, filename))
    return list_file_name

def extract_bank_account(item):
    return item[0]

def extract_dates(item):
    thai_month_names = {
    'ม.ค.': 'Jan',
    'ก.พ.': 'Feb',
    'มี.ค.': 'Mar',
    'เม.ย.': 'Apr',
    'พ.ค.': 'May',
    'มิ.ย.': 'Jun',
    'ก.ค.': 'Jul',
    'ส.ค.': 'Aug',
    'ก.ย.': 'Sep',
    'ต.ค.': 'Oct',
    'พ.ย.': 'Nov',
    'ธ.ค.': 'Dec',
}
    dates = []
    thai_word = re.findall(pattern_only_Thai, item[1])
    if len(thai_word) == 1:
        item.pop(1)
    thai_date = re.findall(pattern_start_Num, item[1])
    words = thai_date[0].split(' ')
    day = words[0]
    month = thai_month_names[words[1]]
    year = int(words[2])-543
    time = words[3]
    date_object = datetime.datetime(year, datetime.datetime.strptime(month, "%b").month, int(day), int(time.split(":")[0]), int(time.split(":")[1]))
    date_with_timezone = date_object.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
    iso_8601_date = date_with_timezone.isoformat()
    dates.append(iso_8601_date)
   
    return dates
    
def extract_reference(item):
    references = []
    # for item in data:
    ref = re.findall(pattern_start_EngNumSpecial, item[2])
    new_ref = ''.join(ref)
    references.append(new_ref)
    return references

def extract_sender_name(item):

    sender_names = re.findall(pattern_only_Thai_dot, item[4]) 
    # sender_names = [re.findall(pattern_only_Thai_dot, item[4]) for item in data]
    return sender_names

def extract_sender_account(item):
    sender_account_numbers = re.findall(pattern_accountNumber, item[4]) 
    # sender_account_numbers = [re.findall(pattern_accountNumber, item[4]) for item in data]
    return sender_account_numbers

def extract_receiver_info(items):
    receiptent_name = []
    receiptent_info = []
    receiver_realname = []
    receive_accountNumber = []
    shop_realname = []
    shop_name = []
    biller_id = []

    big_pop=[]

    if not re.search(pattern_start_Num, items[6]) and len(items[6]) <= 8:
        items.pop(6)
    receiptent_name.append(re.findall(pattern_only_ThaiEngNum, items[6]))
    amount_idx = [i for i, item in enumerate(items) if re.search('.*จำนวนเงิน.*', item) or re.search('.*amount.*', item)]
    # print(amount_idx,items)
    receiptent_info.append(''.join(items[6:amount_idx[0]]))
    for i, item in enumerate(receiptent_info):
        if re.search('.*biller.*', item) or re.search('.*comp.*', item) or re.search('.*บัญชีรับชำระ.*', item):
            # print('this is shop',item)
            if re.search('.*ชื่อบัญชี.*', item):
                shopRealName = re.search('(?<=ชื่อบัญชี:\s).*(?=\sbiller)', item)
                shop_realname.append(shopRealName.group(0))
                # big_pop.append(shopRealName.group(0))
                shopName = re.search('.*(?=\sชื่อบัญชี)', item)
                shop_name.append(shopName.group(0))
                # big_pop.append(shopName.group(0))
                big_pop.append([shopRealName.group(0),shopName.group(0)])
            elif re.search('.*biller.*', item):
                    shopName = re.search('.*(?=\sbiller| comp| บัญชีรับชำระ)', item)
                    shop_name.append(shopName.group(0))
                    # big_pop.append(shopName.group(0))
                    billerId = re.search('(?<=ld\s|id\s)[0-9]+', item)
                    if billerId is not None:
                    # print(billerId)
                        biller_id.append(billerId.group(0))
                        # big_pop.append(billerId.group(0))
                        big_pop.append([shopName.group(0),billerId.group(0)])
                    else:
                        big_pop.extend([shopName.group(0)])
            elif re.search('.*comp.*', item):
                    shopName = re.search('.*(?=\scomp)', item)
                    shop_name.append(shopName.group(0))
                    # big_pop.append(shopName.group(0))
                    big_pop.extend([shopName.group(0)])

            elif re.search('.*บัญชีรับชำระ.*', item):
                    shopName = re.search('.*(?=\sบัญชีรับชำระ)', item)
                    shop_name.append(shopName.group(0))
                    # big_pop.append(shopName.group(0))
                    big_pop.extend([shopName.group(0)])          

        else: 
            modified_text = ''
            realname = re.search('.+?(?= x| [0-9])', item)
            if len(re.findall('[ก-๙]', realname[0])) > len(re.findall('[a-zA-Z]', realname[0])):
                if re.search(r'.*s.*', realname[0]):
                    modified_text = re.sub('s', 'ร', realname.group(0))
                    receiver_realname.append(modified_text)

                elif re.search(r'.*w.*', realname[0]):
                    modified_text = re.sub('w', 'พ', realname.group(0))
                    receiver_realname.append(modified_text)

                else:
                    receiver_realname.append(realname.group(0))

            else:
                receiver_realname.append(realname.group(0))
            

            accountNumber = re.search('(?= x| [0-9]).*', item)
            receive_accountNumber.append(accountNumber.group(0))
            if modified_text == '':
                big_pop.append([realname.group(0),accountNumber.group(0)])
            else:
                big_pop.append([modified_text,accountNumber.group(0)])
    return big_pop


def extract_amount(items):
    amount = []
    # for items in data:
    amount_idx = [i for i, item in enumerate(items) if re.search('.*จำนวนเงิน.*', item) or re.search('.*amount.*', item)]
    amount_temp = ''.join(items[amount_idx[0]+1:amount_idx[0]+2])
    if re.search(r'[^0-9,.]', amount_temp):
        if re.search(r'.*o.*', amount_temp):
            modified_text = re.sub('o', '0', amount_temp)
            amount.append(modified_text)
    amount.append(amount_temp)

    return amount

def extract_other(items):
    other = []
    # for items in data:
    if re.search(pattern_only_EngNum,items[-1]):
        items.pop(-1)
    amount_idx = [i for i, item in enumerate(items) if re.search('.*จำนวนเงิน.*', item) or re.search('.*amount.*', item)]
    other.append(''.join(items[amount_idx[0]+2:-1]))
    return other


app = Flask(__name__)

# Load the Thai model from the thai.pth file
model_path = 'thai.pth'  # Replace 'path_to_thai.pth' with the actual path to your thai.pth file
model = torch.load(model_path, map_location='cpu')

# Create an EasyOCR reader instance with the loaded model
reader = easyocr.Reader(lang_list=['th', 'en'], model_storage_directory='.')

def get_request_header(request):
    header_data = []
    for header in request.headers:
        header_data.append(" : ".join(header))
    return header_data

@app.route('/process_image', methods=['POST'])
def process_image():
    print(get_request_header(request))
    try:

        if 'file' not in request.files:
            return jsonify({"error": "No file provided in the request"})

        image_file = request.files['file']

        # Read the image using OpenCV
        image = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)
        print('image Shape:',image.shape)

        # Perform OCR on the image
        results = reader.readtext(image, paragraph=True, detail=1, add_margin=0.148,
                                  blocklist='๐๑๒๓๔๕๖๗๘๙¥¢¤£*!@$^+|?><', min_size=30)
        
        tempdata=[]
        for item in results:
            tempdata.append(item[1])


        # Read and process text files
        list_data = tempdata
        bank_accounts = extract_bank_account(list_data)
        dates = extract_dates(list_data)
        references = extract_reference(list_data)
        sender_names = extract_sender_name(list_data)
        sender_account_numbers = extract_sender_account(list_data)
        receiver_realname = extract_receiver_info(list_data)
        amount = extract_amount(list_data)
        other = extract_other(list_data)
        print('date1:',dates)
        dates = dates[0]
        references = ' '.join(references)
        sender_names = ' '.join(sender_names)
        sender_account_numbers = ''.join(sender_account_numbers)
        receiver_account_numbers = receiver_realname[0][1]
        receiver_realname = receiver_realname[0][0]
        amount = ''.join(amount)
        other = ''.join(other)
        print('date2:',dates)
        if "ข้อมูลเพิ่มเติมจากผู้ไห้บริการ " in other:
            other=other.split("ข้อมูลเพิ่มเติมจากผู้ไห้บริการ ",1)[1]
            print('other new',other)
        # Create a JSON response
        response_data = {
            "bank_accounts":bank_accounts,
            "date": dates,
            "reference_number": references,
            "sender_name": sender_names,
            "sender_account_number": sender_account_numbers,
            "recipient_name": receiver_realname,
            "recipient_account_number": receiver_account_numbers,
            "amount": amount ,
            "memo": other,


        }


        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": "welcome to receiptwise-scan-api",
        "header": get_request_header(request)
    })


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0",port=80)
