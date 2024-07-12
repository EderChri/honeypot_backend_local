from abc import ABC

from utils.structures import MessengerOptions
from utils.text_utils.text_filter import *
from .gen import gen_text
from constants import MAIL_PROMPT, WA_PROMPT, IG_PROMPT, \
    FB_PROMPT, IO_TYPE
from services.io_utils.factories import LoaderFactory

text_filters = [
    RemoveSymbolLineTextFilter(),
    RemoveInfoLineTextFilter(),
    RemoveSensitiveInfoTextFilter(),
    RemoveSpecialPunctuationTextFilter(),
    RemoveStrangeWord(),
    MultiSymbolIntegrationTextFilter(),
]


class Replier(ABC):
    name = "AbstractReplier"

    def __init__(self, name, prompt_prefix, model_path=None):
        self.name = name
        self.prompt_prefix = prompt_prefix
        self.model_path = model_path
        self.loader = LoaderFactory.get_loader(IO_TYPE)

    def _gen_text(self, prompt) -> str:
        print(f"Generating reply using {self.name}")
        prompt = f"{self.prompt_prefix}\n{prompt}"
        return gen_text(prompt, self.model_path)

    def get_reply(self, content):
        for text_filter in text_filters:
            content = text_filter.filter(content)

        res = self._gen_text(content)

        if "[response_end]" in res:
            res = res.split("[response_end]", 1)[0]

        m = re.match(r"^.*[.?!]", res, re.DOTALL)
        if m:
            res = m.group(0)

        return res

    def get_reply_by_his(self, scam_id, is_unique_id=False):
        loaded_history = self.loader.load_history(scam_id, is_unique_id=is_unique_id)
        return self.get_reply(loaded_history + "\n[response_start]\n")


class MailReplier(Replier):
    def __init__(self):
        super().__init__(MessengerOptions.EMAIL, MAIL_PROMPT)


class WhatsAppReplier(Replier):
    def __init__(self):
        super().__init__(MessengerOptions.WHATSAPP, WA_PROMPT)


class InstagramReplier(Replier):
    def __init__(self):
        super().__init__(MessengerOptions.INSTAGRAM, IG_PROMPT)


class FacebookReplier(Replier):
    def __init__(self):
        super().__init__(MessengerOptions.FACEBOOK, FB_PROMPT)
