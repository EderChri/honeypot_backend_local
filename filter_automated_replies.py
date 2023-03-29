import re 
import shutil
import os


# check per address if there are any duplicate emails. then flag as bot. then check if all responses are duplicate

#for each file ending in .his in archive:
import os
path = "/mnt/c/Users/Jemim/Documents/DISSERTATION/scambaiter_backend/emails/archive/"

def find_set_list_ind_emails(filename):
    with open(path + filename, "r", encoding="utf8") as f:
        arch_content = f.read()

    arch_content = arch_content.replace("\n", "")
    arch_content = arch_content.replace("\r", "")
    #find number of occurrences of [scam_start]
    count = 0
    for word in arch_content.split():
        if "[scam_start]" in word:
            count+=1

    list_of_ind_emails = []


    for i in range(count):
        start = arch_content.find('[scam_start]') + len('[scam_start]')
        end = arch_content.find('[scam_end]', start)
        list_of_ind_emails.append(arch_content[start:end])
        arch_content = arch_content[end:]

    #check if there are any duplicate emails -> see if set=list
    set_ind_emails = set(list_of_ind_emails)
    return [set_ind_emails, list_of_ind_emails]

def separate_and_find_dupes(filename):
    set_ind_emails = find_set_list_ind_emails(filename)[0]
    list_of_ind_emails = find_set_list_ind_emails(filename)[1]
    
    src = path + filename
    dst_dupe = "/mnt/c/Users/Jemim/Documents/DISSERTATION/scambaiter_backend/bot_archives/possible_bot_archives/" + filename
    dst_normal = "/mnt/c/Users/Jemim/Documents/DISSERTATION/scambaiter_backend/bot_archives/probable_not_bot_archives/" +filename
    #COULD BE A BOT
    if not(len(set_ind_emails) == len(list_of_ind_emails)):
        #copy to another folder for inspection        
        shutil.copyfile(src, dst_dupe)
        print("dupes exist :(")
    else:
        shutil.copyfile(src, dst_normal)


for file in os.listdir(path):
    if file.endswith(".his"):
        separate_and_find_dupes(file)



def only_dupes_checker(filename):
    set_ind_emails = find_set_list_ind_emails(filename)[0]
    list_of_ind_emails = find_set_list_ind_emails(filename)[1]
    
    src = possibot_path + filename
    defo_bot_dst =  "/mnt/c/Users/Jemim/Documents/DISSERTATION/scambaiter_backend/bot_archives/definite_bot_archives/" + filename
    prob_not_bot_dst = "/mnt/c/Users/Jemim/Documents/DISSERTATION/scambaiter_backend/bot_archives/probable_not_bot_archives/" + filename

    #almost definitely a bot if true
    if abs(len(list_of_ind_emails) - len(set_ind_emails)) <3:
        print("THIS IS 100% a bot uh oh")
        shutil.move(src, defo_bot_dst)
    else:
        shutil.copyfile(src, prob_not_bot_dst)
    


    
# now check if basically all the emails are dupes?
possibot_path = "/mnt/c/Users/Jemim/Documents/DISSERTATION/scambaiter_backend/bot_archives/possible_bot_archives/"
for file in os.listdir(possibot_path):
    only_dupes_checker(file)