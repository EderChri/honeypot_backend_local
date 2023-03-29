import json
from secret import ADDR_SOL_PATH

personality_dict = {
    "OldWoman":0,
    "NaiveYouth":0,
    "BusinessPerson":0,
    "ProfitFocusedMan":0,
    "Classifier":1
}

messages_ignored_personality_dict = {
    "OldWoman":0,
    "NaiveYouth":0,
    "BusinessPerson":0,
    "ProfitFocusedMan":0,
    "Classifier":1
}


avg_convo_length_personality = {
    "OldWoman":0,
    "NaiveYouth":0,
    "BusinessPerson":0,
    "ProfitFocusedMan":0,
    "Classifier":1
}

longest_convo_length_personality = {
    "OldWoman":0,
    "NaiveYouth":0,
    "BusinessPerson":0,
    "ProfitFocusedMan":0,
    "Classifier":1
}


# surely any with more than one response indicates a scammer has replied to the initial email
# updated to also find average convo length
# updated to also find longest conversation per personality
def find_most_convos_initiated():
    with open(ADDR_SOL_PATH, "r", encoding="utf8") as f:
        record_content = json.load(f)

    for record in record_content:
        replies_sent = len(record_content[record]["used_templates"])
        if (replies_sent>1):
            personality_dict[record_content[record]["sol"]] +=1
            avg_convo_length_personality[record_content[record]["sol"]] += replies_sent
            if replies_sent > longest_convo_length_personality[record_content[record]["sol"]]:
                longest_convo_length_personality[record_content[record]["sol"]] = replies_sent
                print("NEW LONGEST FOR " + str(record_content[record]["sol"]) + " " + str(record_content[record]["to"]))
        else:
            messages_ignored_personality_dict[record_content[record]["sol"]] +=1
    
    for personality in personality_dict:
        avg_convo_length_personality[personality] = avg_convo_length_personality[personality]/personality_dict[personality]


    print("replies gotten: " + str(personality_dict))
    print("messages ignored: " + str(messages_ignored_personality_dict))
    print("average replies sent back " + str(avg_convo_length_personality))
    print("longest conversation per personality: " + str(longest_convo_length_personality))


#CANT MEASURE THE CLASSIFIER ONE VIA THIS BECAUSE FORGOT TO ACTUALLY UPDATE USED TEMPLATES 
#IN THAT REPLIER. MAYBE LOOK THROUGH THE ARCHIVE TO SEE IF THERE IS RESPONSES?

find_most_convos_initiated()