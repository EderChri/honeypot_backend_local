import os.path
import random
import re
from abc import ABC, abstractmethod

from text_utils.text_filter import *
from .gen import gen_text
from .classifier import classify
from secret import NEO_ENRON_PATH, NEO_RAW_PATH, MAIL_ARCHIVE_DIR, TEMPLATES_DIR, PERSONALITY_TEMPLATES_DIR


text_filters = [
    RemoveSymbolLineTextFilter(),
    RemoveInfoLineTextFilter(),
    RemoveSensitiveInfoTextFilter(),
    RemoveSpecialPunctuationTextFilter(),
    RemoveStrangeWord(),
    MultiSymbolIntegrationTextFilter(),
]


list_email_sign_offs = ["YOURS SINCERELY", "SINCERELY", "FAITHFULLY", "YOURS FAITHFULLY", 
                        "BEST,", "KIND REGARDS", "KINDEST REGARDS", "REGARDS,", "BEST WISHES",
                        "YOURS,\n", "THANK YOU,\n", "THANKS,\n", "BEST REGARDS", "THANKS\n",
                        ]

class Replier(ABC):
    name = "AbstractReplier"

    @abstractmethod
    def _gen_text(self, prompt) -> str:
        print(f"Generating reply using {self.name}")
        return prompt

    def get_reply(self, content):
        for text_filter in text_filters:
            content = text_filter.filter(content)

        print("I AM INSIDE GET_REPLY")
        print("THIS IS CONTENT " + str(content) )
    #print("I am TRYING TO CLASSIFY IT HERE " + str(classify(content)))

        res = self._gen_text(content)

        if "[bait_end]" in res:
            res = res.split("[bait_end]", 1)[0]
           
        m = re.match(r"^.*[.?!]", res, re.DOTALL)
        print("THIS IS M " + str(m))
        if m:
            print("this is m " + str(m.groups))
            res = m.group(0)

        return res

    def get_reply_by_his(self, addr):
        with open(os.path.join(MAIL_ARCHIVE_DIR, addr + ".his"), "r", encoding="utf8") as f:
            content = f.read()
        return self.get_reply(content + "\n[bait_start]\n")


def find_sign_off(prompt):
    line_array = prompt.split("\n")
    sign_off_found = False
    line_num_sign_off = -1
    for line_num, line in enumerate(line_array):
        for sign_off in list_email_sign_offs:
            if (line_num_sign_off == -1):
                if sign_off in line.upper():
                    print("sign_off found + " + str(sign_off))
                    sign_off_found = True
                    line_num_sign_off = line_num
                    break
        if sign_off_found:
            break
    return [sign_off_found, line_num, line_array]



def find_name_of_sender(prompt):
    name = 0
    sign_off_info = find_sign_off(prompt)
    sign_off_found = sign_off_info[0]
    line_num = sign_off_info[1]
    line_array = sign_off_info[2] 
    if sign_off_found:
        #line_num indexed from 1 i think
        possible_name = line_array[line_num + 1]
        valid_name_pattern = re.compile(r"^[a-zA-Z'\-\s.]+$")
        if valid_name_pattern.match(possible_name):
            print("this might be a name " + possible_name)
            if (possible_name == ""):
                possible_name = line_array[line_num+2]
            possible_name_array = possible_name.split(" ")
            first_elem = possible_name_array[0].upper()
            if (("MR" in first_elem) or("MRS" in first_elem) or ("MS" in first_elem) or ("THE" in first_elem)):
                name = possible_name_array[1]
            else:
                name = first_elem
        if (name == 0):
            print("no valid name found")
    
        name = name.capitalize()
    return name


def LotteryStructure():
    #keep a log of what templates have been sent!, add to the storer?
    print("poop")


class OldWomanReplier(Replier):
    name = "OldWoman"
    def _gen_text(self, prompt) -> str:
        scam_type = classify(prompt)
        if (scam_type == "LOTTERY"):
            print("lottery")
        elif (scam_type == "LOVE"):
            print("love")
        elif (scam_type == "NONTRANS"):
            print("nontrans")
        elif (scam_type == "OTHERS"):
            print("others")
        elif (scam_type == "TRANS"):
            print("trans")
        return "teehee "+ "[bait_end]"


        """
        scam_type = "LOTTERY"
        personality_template_dir = PERSONALITY_TEMPLATES_DIR + "/OldWoman"
        
        template_dir = os.path.join(personality_template_dir, scam_type)#, random.choice(os.listdir(personality_template_dir)))
        template_dir = template_dir + "/first_response"
        print("this is the template directory" + str(template_dir))
        target_filename = random.choice(os.listdir(template_dir))
        with open(os.path.join(template_dir, target_filename), "r", encoding="utf8") as f:
            res = f.read()
        scammer_name = find_name_of_sender(prompt)
        if (scammer_name!=0):
            res = "Dear " + scammer_name +", \n" + res 
        else:
            res = "Hi, \n" + res 
        """
        return res + "[bait_end]"
    
class BusinessPersonReplier(Replier):
    name = "BusinessPerson"

    def _gen_text(self, prompt) -> str:
        scam_type = classify(prompt)
        personality_template_dir = PERSONALITY_TEMPLATES_DIR + "/BusinessPerson"
        print(scam_type)
        template_dir = os.path.join(personality_template_dir, scam_type)
        target_filename = random.choice(os.listdir(template_dir))

        with open(os.path.join(template_dir, target_filename), "r", encoding="utf8") as f:
            res = f.read()
            
        return res + "[bait_end]"
    

class ProfitFocusedManReplier(Replier):
    name = "ProfitFocusedMan"

    def _gen_text(self, prompt) -> str:
        scam_type = classify(prompt)
        personality_template_dir = PERSONALITY_TEMPLATES_DIR + "/ProfitFocusedMan"
        print(scam_type)
        template_dir = os.path.join(personality_template_dir, scam_type)
        target_filename = random.choice(os.listdir(template_dir))

        with open(os.path.join(template_dir, target_filename), "r", encoding="utf8") as f:
            res = f.read()
            
        return res + "[bait_end]"
    

class NaiveYouthReplier(Replier):
    name = "NaiveYouth"

    def _gen_text(self, prompt) -> str:
        scam_type = classify(prompt)
        personality_template_dir = PERSONALITY_TEMPLATES_DIR + "/NaiveYouth"
        print(scam_type)
        template_dir = os.path.join(personality_template_dir, scam_type)
        target_filename = random.choice(os.listdir(template_dir))

        with open(os.path.join(template_dir, target_filename), "r", encoding="utf8") as f:
            res = f.read()
            
        return res + "[bait_end]"

"""
class NeoEnronReplier(Replier):
    name = "NeoEnron"

    def _gen_text(self, prompt) -> str:
        print(f"Generating reply using {self.name}")
        return gen_text(NEO_ENRON_PATH, prompt)


class NeoRawReplier(Replier):
    name = "NeoRaw"

    def _gen_text(self, prompt) -> str:
        print(f"Generating reply using {self.name}")
        return gen_text(NEO_RAW_PATH, prompt)
"""

class ClassifierReplier(Replier):
    name = "Classifier"

    def _gen_text(self, prompt):
        scam_type = classify(prompt)
        template_dir = os.path.join(TEMPLATES_DIR, scam_type)
        target_filename = random.choice(os.listdir(template_dir))

        with open(os.path.join(template_dir, target_filename), "r", encoding="utf8") as f:
            res = f.read()

        return res + "[bait_end]"


class TemplateReplier(Replier):
    name = "Template"

    def _gen_text(self, prompt) -> str:
        template_dir = os.path.join(TEMPLATES_DIR, random.choice(os.listdir(TEMPLATES_DIR)))
        target_filename = random.choice(os.listdir(template_dir))

        with open(os.path.join(template_dir, target_filename), "r", encoding="utf8") as f:
            res = f.read()

        return res + "[bait_end]"

