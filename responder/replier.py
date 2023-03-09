import os.path
import random
import re
from abc import ABC, abstractmethod

from text_utils.text_filter import *
from .gen import gen_text
from .classifier import classify
from solution_manager.storer import get_stored_info, update_used_templates
from secret import NEO_ENRON_PATH, NEO_RAW_PATH, MAIL_ARCHIVE_DIR, TEMPLATES_DIR, PERSONALITY_TEMPLATES_DIR


text_filters = [
    RemoveSymbolLineTextFilter(),
    RemoveInfoLineTextFilter(),
    RemoveSensitiveInfoTextFilter(),
    RemoveSpecialPunctuationTextFilter(),
    RemoveStrangeWord(),
    MultiSymbolIntegrationTextFilter(),
]

grooming_stage_indicators = [" LOVE", " TRUST", " NEED YOU", " PRESENT", " GIFT", " SECRET",
                            " CONFIDE", " HEART", " SEX", " SATISFY", " MASTURBATE"]

ranting_indicators = [" STUPID", " IDIOT", " MORON", " FUCKER", " CUNT", " SHITHEAD", " HATE", "JUST SEND MONEY ", 
                      " ANGRY", " FRUSTRATED", " UPSET", " ANNOYED" , " DISAPPOINTED",
                      " UNHAPPY", " FED UP", " KILL"]


send_money_indicators = ["SEND MONEY", "GBP ", "USD ", " EUR ", "£", "$", "€", "WESTERN UNION ", "TRANSFER ", "BANK",
                         "WORLD REMIT", "MONEY GRAM ", "MONEY-GRAM", "PAYPAL ", "BITCOIN ", " BTC ", "STEAM CARD ", "STEAM GIFT CARD ",
                         " WIRE", " FEE.", "FEE,", " FEE ", " DOLLAR", " EURO ", " POUND ",
                         "RELEASE FUNDS", "RELEASE THE FUNDS"]

move_off_email_indicators = ["SEND NUMBER", "SEND PHONE NUMBER", "YOUR PHONE NUMBER", " SKYPE", "VIDEO CALL",
                             "YOUR ADDRESS", "YOUR FACEBOOK", "DO YOU HAVE FACEBOOK" ]

urgency_indicators = [" SEND MONEY NOW", " URGENT", " NO TIME ", " LITTLE TIME", " ACT NOW",
                      " LIMITED TIME ", " HURRY ", " QUICKLY", " ACT FAST", " FINAL NOTICE",
                       " TIME IS RUNNING OUT", "RIGHT NOW" ]

list_email_sign_offs = ["YOURS SINCERELY", "SINCERELY", "FAITHFULLY", "YOURS FAITHFULLY", 
                        "BEST,", "KIND REGARDS", "KINDEST REGARDS", "REGARDS,", "BEST WISHES",
                        "YOURS,\n", "THANK YOU,\n", "THANKS,\n", "BEST REGARDS", "THANKS\n",]


monetary_reward_indicators = [" MILLION", " THOUSAND", " WON", " CONGRATULATION", "000",
                               "SEND TO YOU"," DISPATCH TO YOU", " RELEASED", " WELL DONE", 
                               " INTO YOUR BANK", "YOUR PAYMENT WILL ", " TRANSFER YOUR", 
                               "DECEASED FOREIGNER"," COMPENSATION PAYMENT", " INHERITANCE", 
                               "DEAD FAMILY MEMBER", "DECEASED FAMILY MEMBER","PROFIT", 
                               "SPLIT", "SHARE THE ", "BUSINESS DEAL"," LOAN", " INTEREST RATE"]

inheritance_indicators = ["INHERITANCE", "DECEASED FOREIGNER", "DEAD FOREIGNER",
                          "DEAD FAMILY MEMBER", "DECEASED FAMILY MEMBER"]

personal_convince_travel = [" PLANE TICKET", " AIRPLANE", " AEROPLANE", " FLIGHT", " ACCOMODATION"]

business_deal_indicators = ["PROFIT", "SPLIT", "SHARE THE ", "BUSINESS DEAL"]

loan_indicators = [" LOAN", "INTEREST RATE"]


dream_job_indicators = ["WORK FROM HOME" , "NO EXPERIENCE", "GET RICH QUICK", "EASY MONEY",
                        "MAKE MONEY FAST", "UNLIMITED INCOME", "DREAM JOB" 
                        "LIMITED POSITIONS AVAILABLE", "JOB VACANCIES", "ANTI-TERRORISM"]


eliciting_sympathy_indicators = ["PLEASE HELP", " DIED", "STUCK IN", " IM STUCK", "I AM STUCK", " DYING ",
                       "STRUGGLING", " STRANDED", " URGENT", " DESPERATE", "FINANCIAL HARDSHIP",
                        " SICK ", " ORPHAN", " TRAGEDY", " HOMELESS", " FIRED", " LOST MY JOB",
                         "MUGGED", "ATTACKED" ]

eliciting_fear_indicators = [" POLICE", " ARREST", " LEGAL ACTION", " TAKE YOU TO COURT",
                             " CRIME", " CONSEQUENCES", " CRIMINAL", " DETENTION",
                             " INVESTIGATION" , " JAIL", " PRISON", " KILL YOU", "HUNT YOU",
                             " HURT YOU", " FIND YOU"]



class Replier(ABC):
    name = "AbstractReplier"

    @abstractmethod
    def _gen_text(self, prompt, addr, bait_email) -> str:
        print(f"Generating reply using {self.name}")
        return prompt

    def get_reply(self, content, addr, bait_email):
        for text_filter in text_filters:
            content = text_filter.filter(content)

        res = self._gen_text(content, addr, bait_email)

        if "[bait_end]" in res:
            res = res.split("[bait_end]", 1)[0]
           
        m = re.match(r"^.*[.?!]", res, re.DOTALL)
        if m:
            res = m.group(0)

        return res

    def get_reply_by_his(self, addr, bait_email):
        print("THIS IS NAME HERE" + str(addr))
        with open(os.path.join(MAIL_ARCHIVE_DIR, addr + ".his"), "r", encoding="utf8") as f:
            content = f.read()
        return self.get_reply(content + "\n[bait_start]\n",addr, bait_email)


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


def append_dir_find_file(used_templates, sol_name, addr, specific_struct_dir):
    template_dir = os.path.join(os.path.join(PERSONALITY_TEMPLATES_DIR, sol_name), specific_struct_dir)
    target_filename = random.choice(os.listdir(template_dir)) 
    res = choose_and_add_template(target_filename, used_templates, template_dir, addr)
    return res


#chooses a random template until one is found that hasn't already been used (if cant find one after)
#25 attempts then it just reuses a template rather than be stuck in a while loop
def choose_and_add_template(target_filename, used_templates, template_dir, addr):
    target_file_path = os.path.join(template_dir, target_filename)
    loop_counter = 0
    if target_file_path in used_templates:
        while (target_file_path in used_templates) and (loop_counter <=25):
            target_filename = random.choice(os.listdir(template_dir))
            target_file_path = os.path.join(template_dir, target_filename)
            loop_counter +=1        
    with open(target_file_path, "r", encoding="utf8") as f:
        res = f.read()
    update_used_templates(target_file_path, addr)
    return res

#find the pcnt of capitalised chars
def find_capitalised_percent(prompt):
    cap_count = 0
    for char in prompt:
        if char.isupper():
            cap_count += 1
    return(cap_count/len(prompt))

def LoveStructure(used_templates, addr, sol_name, prompt):
    capitalised_prompt = prompt.upper()
    #check if grooming_stage has previously been entered
    grooming_stage_bool = False
    pcnt_cap = find_capitalised_percent(prompt)
    for template_used in used_templates:
            print("this is template used " + str(template_used))
            if ("grooming_stage" in template_used):
                grooming_stage_bool = True
    if (used_templates == []):
        res = append_dir_find_file(used_templates, sol_name, addr, "LOVE/first_response")
    # rant if there are any ranting word indicators, or there is an excessive use of exclamation marks
    # or if over 35% of the email is capitalised
    elif (any(word in capitalised_prompt for word in move_off_email_indicators)):
        res = append_dir_find_file(used_templates, sol_name, addr, "move_off_email")
    elif ((any(word in capitalised_prompt for word in ranting_indicators) or (prompt.count("!") >=5)) or (pcnt_cap >=0.35)): 
        res = append_dir_find_file(used_templates, sol_name, addr, "rant_response")
    elif (any(word in capitalised_prompt for word in send_money_indicators)):
        res = append_dir_find_file(used_templates, sol_name, addr, "LOVE/send_money")
    elif (((any(word in capitalised_prompt for word in grooming_stage_indicators)) or (grooming_stage_bool == True)) or len(used_templates) > 5):
        # grooming stage find if already confessed secret and/or confessed love
        lovey_emails_count = 0
        confess_secret_bool = False
        for template_used in used_templates:
            if ("lovey_emails" in template_used):
                lovey_emails_count +=1
            elif ("confess_secret" in template_used):
                confess_secret_bool = True
        # if you've sent all the lovey emails and not confessed your secret, confess
        if ((lovey_emails_count >=2) and (confess_secret_bool == False)):
            res = append_dir_find_file(used_templates, sol_name, addr, "LOVE/grooming_stage/confess_secret")
            #confess secret 
        elif (lovey_emails_count<2):
            res = append_dir_find_file(used_templates, sol_name, addr, "LOVE/grooming_stage/lovey_emails")
            #send a lovey_email
        else: 
            #send a miscellaneous email
            res = append_dir_find_file(used_templates, sol_name, addr, "LOVE/grooming_stage/misc_love")
    else:
        #if its early days ... i.e. less than 5 responses -> if 5 or more we force the grooming stage 
        res = append_dir_find_file(used_templates, sol_name, addr, "LOVE/early_days_response")   
    return res

#structure for an email of transactional nature
def TransStructure(used_templates, addr, sol_name, prompt):
    capitalised_prompt = prompt.upper()
   
    pcnt_cap = find_capitalised_percent(prompt)
    sub_structure = ""
    reward_sub_structure = ""
    question_category = ""

    if (used_templates == []):
        # categorise into dream job,  monetary reward, threat, sympathy (if "generic" just choose any)
        if(any(word in capitalised_prompt for word in dream_job_indicators)):    
            res = append_dir_find_file(used_templates, sol_name, addr, "TRANS/first_response_solicitation/dream_job_based")
        elif(any(word in capitalised_prompt for word in eliciting_sympathy_indicators)):    
            res = append_dir_find_file(used_templates, sol_name, addr, "TRANS/first_response_solicitation/sympathy_based")
        elif(any(word in capitalised_prompt for word in eliciting_fear_indicators)):    
            res = append_dir_find_file(used_templates, sol_name, addr, "TRANS/first_response_solicitation/threat_based")
        elif(any(word in capitalised_prompt for word in monetary_reward_indicators)):  
            sub_structure = "/reward_based"
            if(any(word in capitalised_prompt for word in inheritance_indicators)):
                reward_sub_structure = "/inheritance"
            elif(any(word in capitalised_prompt for word in loan_indicators)):
                reward_sub_structure = "/loan"
            elif(any(word in capitalised_prompt for word in business_deal_indicators)):
                reward_sub_structure = "/business_deal"
            else:
                reward_sub_structure = "/win"  
            res = append_dir_find_file(used_templates, sol_name, addr, "TRANS/first_response_solicitation/reward_based"+reward_sub_structure)
        else:
            res = append_dir_find_file(used_templates, sol_name, addr, "TRANS/first_response_solicitation/generic")
    else:
        # rant if there are any ranting word indicators, or there is an excessive use of exclamation marks
        # or if over 35% of the email is capitalised
        if (any(word in capitalised_prompt for word in personal_convince_travel)):
            res = append_dir_find_file(used_templates, sol_name, addr, "TRANS/personal_convince_travel")
        elif (any(word in capitalised_prompt for word in move_off_email_indicators)):
            res = append_dir_find_file(used_templates, sol_name, addr, "move_off_email")
        elif ((any(word in capitalised_prompt for word in ranting_indicators) or (prompt.count("!") >=5)) or (pcnt_cap >=0.35)): 
            res = append_dir_find_file(used_templates, sol_name, addr, "rant_response")
        else:
            # if none of the above templates, then follow substructure
            for template_used in used_templates:
                if ("threat_based" in template_used):
                    sub_structure = "/threat_based"
                elif ("/reward_based" in template_used):
                    sub_structure = "/reward_based"
                    if("inheritance" in template_used ):
                        reward_sub_structure = "/questions_inheritance"
                    elif("loan" in template_used):
                        reward_sub_structure = "/questions_loan"
                    elif("business_deal" in template_used):
                        reward_sub_structure = "/questions_business_deal"
                    else:
                        reward_sub_structure = "/questions_win"
                elif ("sympathy_based" in template_used):
                    sub_structure = "/sympathy_based"
                elif ("dream_job_based" in template_used):
                    sub_structure = "/dream_job_based"
                #generic
                else:
                    sub_structure = "/generic_questions"
            # "near win", every three emails, if their email mentions money, ask about the fee
            # only every 3 so not stuck in loop, and suspicious to mention money if their prev email didnt
            # otherwise, continually ask questions pertaining to the situation 
            if ((len(used_templates) % 3 == 0) and any(word in capitalised_prompt for word in send_money_indicators)):
                question_category = "/fee_qs"
            else:
                question_category = "/situation_qs"
                
            if (sub_structure=="/reward_based"):
                res = append_dir_find_file(used_templates, sol_name, addr, "TRANS" +sub_structure+ reward_sub_structure + question_category)
            elif (sub_structure=="/generic_questions"):
                res = append_dir_find_file(used_templates, sol_name, addr, "TRANS" + sub_structure)
            else:
                res = append_dir_find_file(used_templates, sol_name, addr, "TRANS" + sub_structure + question_category)
              
    return res



#structure for an email with lottery classification
def LotteryStructure(used_templates, addr, sol_name, prompt):
    capitalised_prompt = prompt.upper()
   
    pcnt_cap = find_capitalised_percent(prompt)

    pretended_to_send = False
    irritation_stage_reached = False

    if (used_templates == []):  
        res = append_dir_find_file(used_templates, sol_name, addr, "LOTTERY/first_response")
    # rant if there are any ranting word indicators, or there is an excessive use of exclamation marks
    # or if over 35% of the email is capitalised
    else:
        for template_used in used_templates:
            if ("pretend_sent" in template_used):
                pretended_to_send = True
            if ("rant_response" in template_used):
                irritation_stage_reached = True
        if (any(word in capitalised_prompt for word in move_off_email_indicators)):
            res = append_dir_find_file(used_templates, sol_name, addr, "move_off_email")
        elif ((any(word in capitalised_prompt for word in ranting_indicators) or (prompt.count("!") >=5)) or (pcnt_cap >=0.35)): 
            res = append_dir_find_file(used_templates, sol_name, addr, "rant_response")
            irritation_stage_reached = True
    
        # "near win", every three emails, if their email mentions money, ask about the fee
        # only every 3 so not stuck in loop, and suspicious to mention money if their prev email didnt
        # otherwise, 2 qs about situ then 1 sceptical/ excited email depending on person
        elif ((len(used_templates) % 4 == 0) and any(word in capitalised_prompt for word in send_money_indicators) and (irritation_stage_reached == True)):
            if (pretended_to_send == True):
                res = append_dir_find_file(used_templates, sol_name, addr, "LOTTERY/transaction_reply")
            else:
                res = append_dir_find_file(used_templates, sol_name, addr, "LOTTERY/pretend_sent")
        elif ((len(used_templates) % 4 == 3)):
            res = append_dir_find_file(used_templates, sol_name, addr, "LOTTERY/exci_scep_resp")
        else:
            res = append_dir_find_file(used_templates, sol_name, addr, "LOTTERY/questions")
                     
    return res



def NonTransStructure(used_templates, addr, sol_name, prompt):
    capitalised_prompt = prompt.upper() 
    pcnt_cap = find_capitalised_percent(prompt)

    substructure = ""

    if (used_templates == []):  
        if (any(word in capitalised_prompt for word in eliciting_fear_indicators)):
            res = append_dir_find_file(used_templates, sol_name, addr, "NONTRANS/first_response/scared_first")
        elif (any(word in capitalised_prompt for word in eliciting_sympathy_indicators)):
            res = append_dir_find_file(used_templates, sol_name, addr, "NONTRANS/first_response/sympathy_first")
        else:
            res = append_dir_find_file(used_templates, sol_name, addr, "NONTRANS/first_response/generic_first")
    else:
        for template_used in used_templates:
            if ("scared" in template_used):
                substructure = "scared_response"
            elif ("sympathy" in template_used):
                substructure = "sympathy_response"

        if ((any(word in capitalised_prompt for word in ranting_indicators) or (prompt.count("!") >=5)) or (pcnt_cap >=0.35)): 
            res = append_dir_find_file(used_templates, sol_name, addr, "rant_response")
        elif (any(word in capitalised_prompt for word in move_off_email_indicators)):
            res = append_dir_find_file(used_templates, sol_name, addr, "move_off_email")
        elif (any(word in capitalised_prompt for word in urgency_indicators)):
            res = append_dir_find_file(used_templates, sol_name, addr, "NONTRANS/urgent_response")
        elif (substructure != ""):
            res = append_dir_find_file(used_templates, sol_name, addr, "NONTRANS/"+substructure)
        else:
            res = append_dir_find_file(used_templates, sol_name, addr, "NONTRANS/generic_response")

    return res


class OldWomanReplier(Replier):
    name = "OldWoman"

    def _gen_text(self, prompt, addr, bait_email) -> str:
        index_to_cut_before = (prompt.upper()).rfind("[SCAM_START]")

        prompt_only_contain_last_email =  prompt[index_to_cut_before:]

        stored_info = get_stored_info(bait_email, addr)
        scam_type = stored_info.classification
        used_templates = stored_info.used_templates
        addr = stored_info.addr

        if (scam_type == "LOTTERY"):
            res = LotteryStructure(used_templates, addr, self.name, prompt_only_contain_last_email)
        elif (scam_type == "LOVE"):
            print(self.name)
            res = LoveStructure(used_templates, addr, self.name, prompt_only_contain_last_email)
        elif (scam_type == "NONTRANS") or (scam_type == "OTHERS"):
            res = NonTransStructure(used_templates, addr, self.name, prompt_only_contain_last_email)
        elif (scam_type == "TRANS"):
            res = TransStructure(used_templates, addr, self.name, prompt_only_contain_last_email)
     
        scammer_name = find_name_of_sender(prompt[index_to_cut_before:])        
        if (scammer_name!=0):
            res = "Dear " + scammer_name +", \n" + res 
        else:
            res = "Hi, \n" + res 
        return  res + "[bait_end]"

    
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

