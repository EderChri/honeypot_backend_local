# CONF
IO_TYPE = "File"  # used to switch between file and database, currently only file supported
# MAIL
SENDER_EMAIL = "j4759821@gmail.com"
RECEIVER_EMAIL = "ce1@live.de"
# PATH
MAIL_TEMPLATE = 'services/mailgun/template.html'
LOG_PATH = "data/app.log"
ID_PATH = "data/ids.json"
ARCHIVE_DIR = "data/archive"
HANDLED_DIR = "data/handled"
QUEUE_DIR = "data/queued"
MAIL_ADDR_PATH = "data/email_record.json"
## MODEL PATH
MODEL_HISTORY_PATH = "./models/history.json"
NEO_ENRON_PATH = "./models/neo_enron"
NEO_RAW_PATH = "./models/neo_raw"
CLASSIFIER_PATH = "./models/classifier/final-model.pt"
TEMPLATES_DIR = "services/responder/templates"
# CRAWLER CONF
CRAWLER_PROG_DIR = "./cache"
MAX_PAGE = 20

# PROMPTS
MAIL_PROMPT = "This is a custom mail prompt"
WA_PROMPT = "This is a custom WhatsApp prompt"
FB_PROMPT = "This is a custom Facebook prompt"
IG_PROMPT = "This is a custom Instagram prompt"

# MODELS:
SWITCH_DETECTOR_PROMPT_PREFIX = "I will send you a message now, and if you think, this is a request to switch to " \
                                "another messenger application reply with `True:messenger`, where `messenger` is the " \
                                "messenger the message suggests switching to. If you don't think the message is about "\
                                "switching reply with `False:other. The only available messengers are WhatsApp, "\
                                "Instagram, "\
                                "Facebook and Email. If another messenger is suggested, just reply with `other`. Make "\
                                "sure to not confuse call requests and WhatsApp. Here is the message: "

# LOGGING
TRACE = 25