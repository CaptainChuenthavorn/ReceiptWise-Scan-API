import pandas as pd
import os
import re
from re import search

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

def extract_bank_account(data):
    return [item[0] for item in data]

def extract_dates(data):
    dates = []
    for item in data:
        thai_word = re.findall(pattern_only_Thai, item[1])
        if len(thai_word) == 1:
            item.pop(1)
        dates.extend(re.findall(pattern_start_Num, item[1]))
    return dates
    
def extract_reference(data):
    references = []
    for item in data:
        ref = re.findall(pattern_start_EngNumSpecial, item[2])
        new_ref = ''.join(ref)
        references.append(new_ref)
    return references

def extract_sender_name(data):
    sender_names = [re.findall(pattern_only_Thai_dot, item[4]) for item in data]
    return sender_names

def extract_sender_account(data):
    sender_account_numbers = [re.findall(pattern_accountNumber, item[4]) for item in data]
    return sender_account_numbers

def extract_receiver_info(data):
    receiptent_name = []
    receiptent_info = []
    receiver_realname = []
    receive_accountNumber = []
    shop_realname = []
    shop_name = []
    biller_id = []

    big_pop=[]
    for items in data:
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
            # print('this is normal',item)
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

    with open('1bigpop.txt','w',encoding='utf-8') as file:
        for i in big_pop:
            print(i)
            file.write(str(i)+'\n')
    return big_pop


def extract_amount(data):
    amount = []
    for items in data:
        amount_idx = [i for i, item in enumerate(items) if re.search('.*จำนวนเงิน.*', item) or re.search('.*amount.*', item)]
        amount_temp = ''.join(items[amount_idx[0]+1:amount_idx[0]+2])
        if re.search(r'[^0-9,.]', amount_temp):
            if re.search(r'.*o.*', amount_temp):
                modified_text = re.sub('o', '0', amount_temp)
                amount.append(modified_text)
        amount.append(amount_temp)

    return amount

def extract_other(data):
    other = []
    for items in data:
        if re.search(pattern_only_EngNum,items[-1]):
            items.pop(-1)
        amount_idx = [i for i, item in enumerate(items) if re.search('.*จำนวนเงิน.*', item) or re.search('.*amount.*', item)]
        other.append(''.join(items[amount_idx[0]+2:-1]))
    return other

if __name__ == "__main__":
    text_files_directory = 'NewOCR'

    # Read and process text files
    list_data = read_text_files(text_files_directory)
    
    # Extract data
    bank_accounts = extract_bank_account(list_data)
    dates = extract_dates(list_data)
    references = extract_reference(list_data)
    sender_names = extract_sender_name(list_data)
    sender_account_numbers = extract_sender_account(list_data)
    receiver_realname = extract_receiver_info(list_data)
    amount = extract_amount(list_data)
    other = extract_other(list_data)

    print()
    print(len(bank_accounts))
    print()
    print(len(dates))
    print()
    print(len(references))
    print()
    print(len(sender_names))
    print()
    print(len(sender_account_numbers))
    print(receiver_realname,len(receiver_realname))
    print()
    print(len(amount))
    print()
    print(len(other))
    list_file_name = read_text_files_name(text_files_directory)
    with open('4overallCheck.txt','w',encoding='utf-8') as file:
        for i in range(165):
            # print(i)
            file.write('FileName:'+str(list_file_name[i])+'\n\n')
            file.write(str(bank_accounts[i])+'\n')
            file.write(str(dates[i])+'\n')
            file.write(str(references[i])+'\n')
            file.write(str(sender_names[i])+'\n')
            file.write(str(sender_account_numbers[i])+'\n')
            file.write(str(receiver_realname[i])+'\n')
            file.write(str(amount[i])+'\n')
            file.write(str(other[i])+'\n===========================\n\n')