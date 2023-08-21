import os
import codecs
import zipcodes
import re
import json
import base_parser
import dateutil.parser
from difflib import SequenceMatcher
import sys
import csv
import datetime as dt
from datetime import datetime
import pyap
import dateutil.parser
# sys.setdefaultencoding('utf-8')
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

# id class and DL and valid address, there is a name
class DriverLicense:

    def __init__(self):
        self.date = None
        self.last = []
        self.first = []
        self.dob = None
        self.gender = None
        self.Height = None
        self.photo_id = None
        self.state = []
        self.zipcode = []
        self.full_address = []
        self.street_address = []
        self.city = []
        self.valid_dl = None
        self.exp_date = None
        self.dl_number = None
    
    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def get_date_and_id_from_title(self, title):
        re1 = title.split("@")
        if len(re1) >= 2:
            photo_id = re1[0].split("_")[1]
            date = re1[1].split("_")[0]
            return photo_id, date
        else:
            return None, None
        

    def check_zipcode(self,content):
        result = []
        state_names = {
            "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
            "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
            "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
            "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
            "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
            "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
            "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
            "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
            "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
            "West Virginia": "WV", "Wisconsin": "WI",
        }

        for i in re.finditer(r'(?!\A)\b\d{5}(?:-\d{4})?\b', content):
            if zipcodes.is_real(i.group()):
                state  = zipcodes.matching(i.group())[0]['state']
                if state in content:
                    result.append((i.group(), state))
                    return result
        content = content.lower()
        test = content.split(' ')
        for k, v in state_names.items():
            for i in test:
                if self.similar(k.lower(), i) > .75:
                    result.append((None, v))    
        return result
    

    def extract_first_name(self, content):
        content_lower = content.lower()
        words = content_lower.split()
        name_words = ["1", "fn"]
        for i, word in enumerate(words):
            if word in name_words and i+1 < len(words):
                return words[i+1].capitalize()
        return ' '

    def extract_last_name(self, content): 
        content_lower = content.lower()
        words = content_lower.split()
        name_words = ["2", "ln"]
        for i, word in enumerate(words):
            if word in name_words and i+1 < len(words):
                return words[i+1].capitalize()
        return None
    
    def validate_exp_date(self,content):
        exp_dates = []
        content_lower = content.lower()
        words = content_lower.split()

        for i, word in enumerate(words):
            if word in ["exp", "expires", "5ein"] and i+1 < len(words):
                potential_date = words[i+1]
                if ("/" in potential_date or "-" in potential_date) and "," not in potential_date:
                    exp_dates.append(potential_date)

        valid_dates = []
        for exp_date in exp_dates:
            try:
                dl_date = dateutil.parser.parse(exp_date)
                curr_date = dt.date.today()
                if curr_date <= dl_date.date() <= curr_date + dt.timedelta(days=365):
                    valid_dates.append(dl_date.date().strftime("%m/%d/%Y"))
            except:
                pass

        if valid_dates:
            return valid_dates
        else:
            return None


    def extract_date_of_birth(self, content):
        ex_dob = []
        content_lower = content.lower()
        words = content_lower.split()

        for i, word in enumerate(words):
            if word == "dob"  and i+1 < len(words):
                potential_date = words[i+1]
                if ("/" in potential_date or "-" in potential_date) and "," not in potential_date:
                    ex_dob.append(potential_date)
        dob = []
        for i in ex_dob:
            try:
                dob = dateutil.parser.parse(i).date()
                print("Parsed date:", dob)
                return dob.strftime("%m/%d/%Y")
            except Exception as e:
                print("Error parsing date:", i, e)
                pass

        return None
    
    def extract_gender(self, content):
        content_lower = content.lower()
        words = content_lower.split()
        gender_words = ["male", "female", "man", "woman", "m", "f"]

        for i, word in enumerate(words):
            if word in gender_words:
                # Check for adjacent words that provide more context
                if i+1 < len(words) and words[i+1] in gender_words:
                    continue  # Skip ambiguous words like "man woman"
                if word in ["m", "man", "male"]:
                    return "M"
                elif word in ["f", "woman", "female"]:
                    return "F"

        return None
    

    def extract_height(self, content):
        content_lower = content.lower()
        words = content_lower.split()
        height_words = ["height", "ht", "hgt"]
        feet_words = ["ft", "feet", "'"]
        inches_words = ["in", "inch", "inches", "''"]

        for i, word in enumerate(words):
            if word in height_words and i+1 < len(words):
                next_word = words[i+1]
                if any(char.isdigit() for char in next_word):
                    feet = 0
                    inches = 0
                    height_parts = next_word.split("-")
                    if len(height_parts) == 2:
                        feet_part, inches_part = height_parts
                        try:
                            feet = int(feet_part.replace("'", ""))
                            inches = int(inches_part.replace('"', ''))
                        except ValueError:
                            return None
                    elif len(height_parts) == 1 and any(char.isdigit() for char in height_parts[0]):
                        try:
                            feet = int(height_parts[0].replace("'", ""))
                        except ValueError:
                            return None
    
                    for j in range(i+2, min(i+4, len(words))):
                        next_word = words[j]
                        if any(char.isdigit() for char in next_word):
                            if inches == 0:
                                try:
                                    inches = int(next_word.replace('"', ''))
                                except ValueError:
                                    return None
                            else:
                                break
                        elif next_word in feet_words:
                            continue
                        elif next_word in inches_words:
                            continue
                        else:
                            break
    
                    height_str = f"{feet}ft{inches}in"
                    return height_str

        return None
    
    def validate_full_address(self, content):
        result = []
        address = []
        content_lower = content.lower()
        words = content_lower.split(" ")
        dl_regex_full_address = pyap.parse(content, country='US')
        if len(dl_regex_full_address) > 0:
            for address_obj in dl_regex_full_address:
                address_str = address_obj.full_address
                address.append(address_str)
            return ', '.join(address)
        else:
            return ' '
        
    def validate_street_address(self, content):
        address = []
        content_lower = content.lower()
        words = content_lower.split(" ")
        dl_regex_full_address = pyap.parse(content, country='US')
        if len(dl_regex_full_address) > 0:
            for address_obj in dl_regex_full_address:
                address_str = address_obj.full_address
                address_dict = address_obj.as_dict()
                if 'city' in address_dict:
                    city = address_dict['city']
                else:
                    city = ' '
                street_address = address_str.split(city)[0].strip(',')
                address.append(street_address)  
            return ' '.join(address)  
        else:
            return ' '

    
        
    def validate_dl_number(self,content):
        dl_regex_usa_states = ["[A-Z]\d{6}[A-Z0-9]{2,5}", "[a-zA-Z]\d{7}", "[a-zA-Z]\d{3}-\d{3}-\d{2}-\d{3}-\d",              
                      "\d{7}", "[a-zA-Z]\d{3}\d{3}\d{3}\d{3}", "[a-zA-Z]\d{12}", "[a-zA-Z]\d{8}",              
                      "\d{9}", "9\d{8}", "[a-zA-Z]\d{7}", "\d{2}-\d{3}-\d{4}", "[a-zA-Z]\d{8}",              
                      "[a-zA-Z]{2}\d{8}[a-zA-Z]", "[a-zA-Z]\d{3}-\d{4}-\d{4}", "[a-zA-Z]\d{11}", "\d{4}-\d{2}-\d{4}",              
                      "\d{3}[a-zA-Z]{2}\d{4}", "[a-zA-Z]\d{2}-\d{2}-\d{4}", "[a-zA-Z]\d{2}-\d{3}-\d{3}",              
                      "[a-zA-Z]-\d{3}-\d{3}-\d{3}-\d{3}", "[a-zA-Z]\d{12}", "[a-zA-Z]\d{9}",              
                      "[a-zA-Z]\s\d{3}\s\d{3}\s\d{3}\s\d{3}", "\d{3}-\d{2}-\d{4}", "\d{10}",              
                      "([0][1-9]|[1][0-2])[a-zA-Z]{3}\d{2}(0[1-9]|[1-2][0-9]|3[0-1])\d", "[a-zA-Z]\d{4} \d{5} \d{5}",              
                      "[a-zA-Z]\\d{14}", "\d{3} \d{3} \d{3}", "\d{12}", "[a-zA-Z]{3}-\d{2}-\d{4}",              
                      "[a-zA-Z]{1}[0-9]{4,8}", "[a-zA-Z]{2}[0-9]{3,7}", "[0-9]{8}", "\d{7,9}", "\d{7}[a-zA-Z]",              
                      "[a-zA-Z]\d{2}-\d{2}-\d{4}", "[a-zA-Z]{3}\*\*[a-zA-Z]{2}\d{3}[a-zA-Z]\d", "[a-zA-Z]\d{8}",              
                      "[a-zA-Z]\d{3}-\d{4}-\d{4}-\d{2}", "\d{6}-\d{3}", "[A-Z]{1,2}[0-9]{2,6}",              
                      "^[A-Z]\d{3}-\d{3}-\d{2}-\d{3}-\d$", "\d{3}-\d{3}-\d{3}", "\d{3}\s\d{3}\s\d{3}",              
                      "((0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(19|20)\d{2})", "\d{9}"]

        content_lower = content.lower()
        words = content_lower.split()
        dl_words = ["dl", "dl no", "4d dln", "4d dl no", "id"]
        for i, word in enumerate(words):
            if word in dl_words and i+1 < len(words):
                for r in dl_regex_usa_states:
                    dl_num = re.findall(r, words[i+1])
                    if dl_num:
                        return dl_num[0].upper()
            else:
                for r in dl_regex_usa_states:
                    dl_num = re.findall(r, content)
                    if dl_num:
                        return dl_num[0].upper()
        return ''
    
    def validate_city(self,content):
        city = ''
        dl_regex_full_address = pyap.parse(content, country='US')
        if len(dl_regex_full_address) > 0:
            address_dict = dl_regex_full_address[0].as_dict()
            if 'city' in address_dict:
                city = address_dict['city']
        return city


    # def data_assign_rowby(self, photo_id, date, victimname, zipcodes, states, valid_dl, dl_number, full_address, writer):
    def data_assign_rowby(self, photo_id, date, FN, LN, DOB, dl_number, exp_date, Gender, Height, street_address, validate_city, states, zipcodes, full_address, writer):
        num_zip = len(zipcodes)
        num_states = len(states)
        
        if num_zip == 0 and num_states == 0:
            print("im here")
            writer.writerow([photo_id, date, FN, LN, DOB, dl_number, exp_date, Gender, Height, street_address, validate_city, "", "", full_address])
        
        for i in range(len(zipcodes)):
            if len(zipcodes) > 0:
                zipcode = zipcodes.pop(0)
                state = states.pop(0)
                num_zip -= 1
            else:
                zipcode = ""
                state = ""
            writer.writerow([photo_id, date, FN, LN, DOB,  dl_number, exp_date, Gender, Height, street_address, validate_city, state, zipcode, full_address])

    

if __name__ == '__main__':
    folder_textdoc_path = "/Users/iamns45/Desktop/Drivers_Licenses_Parser-main/copy"
    textdoc_paths = base_parser.get_textdoc_paths(folder_textdoc_path)
    headerList = ['Pic Id', 'Date', 'FN', 'LN', 'DOB', 'DL Number', 'Exp Date', 'Gender', 'Height', 'Street', 'City', 'State', 'Zipcode', 'Full Address']
    with open('driver_licenses_ns'+'.csv','w', newline='', encoding='utf-8') as f1:
        dw = csv.DictWriter(f1, delimiter=',', fieldnames=headerList)
        dw.writeheader()
        writer=csv.writer(f1, delimiter=',')
  
        for text_doc in textdoc_paths:
            writer=csv.writer(f1, delimiter=',')
            dl = DriverLicense()
            file_name = os.path.basename(text_doc)

            #### parse photo id and date
            photo_id, date = dl.get_date_and_id_from_title(file_name)
            if photo_id:
                dl.photo_id = photo_id
            if date:
                dl.date = date

            ### parse zipcode and state
            with open(text_doc, encoding = "utf-8") as f:
                if text_doc== '/Users/iamns45/Desktop/Drivers_Licenses_Parser-main/cpy/.DS_Store':
                    continue
                print(text_doc)
                content = f.readlines()
            if content:
                text_des = ' '.join(content[0:len(content)-1])
            else:
                writer.writerow([dl.photo_id, dl.date, "", "", "", ""])
                continue

            if content:
                info_zipcode = dl.check_zipcode(text_des)
                dl.zipcode.extend([i[0] for i in info_zipcode])
                dl.state.extend([i[1] for i in info_zipcode])

                ## First name
                First_name = dl.extract_first_name(text_des)
                dl.first = First_name

                # Last Name
                Last_name = dl.extract_last_name(text_des)
                dl.last = Last_name
                
                ### validate date
                valid_date = dl.validate_exp_date(text_des)
                dl.exp_date = valid_date

                # extract Date_of_birth
                valid_dob = dl.extract_date_of_birth(text_des)
                dl.dob = valid_dob

                #extract gender
                valid_gender = dl.extract_gender(text_des)
                dl.gender = valid_gender

                #extract Height
                
                hgt = dl.extract_height(text_des)
                dl.Height = hgt

                ##Validate full address
                valid_full_address = dl.validate_full_address(text_des)
                dl.full_address = valid_full_address
                # print(dl.full_address)

                valid_city = dl.validate_city(text_des)
                dl.city = valid_city

                valid_street_address = dl.validate_street_address(text_des)
                dl.street_address = valid_street_address

                ## validate drivers lience number
                license_nums = dl.validate_dl_number(text_des)
                if license_nums:
                    dl.dl_number = ''.join(license_nums)
                else:
                    dl.dl_number = ' '

                print("--------------------------------------------------")

            dl.data_assign_rowby(dl.photo_id, dl.date, dl.first, dl.last, dl.dob, dl.dl_number, dl.exp_date, dl.gender, dl.Height, dl.street_address, dl.city, dl.state, dl.zipcode, dl.full_address, writer)
