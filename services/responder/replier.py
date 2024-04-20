import os.path
from abc import ABC

from text_utils.text_filter import *
from .gen import gen_text
from constants import MAIL_ARCHIVE_DIR, MAIL_PROMPT, WA_PROMPT, IG_PROMPT, \
    FB_PROMPT

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

    def _gen_text(self, prompt) -> str:
        print(f"Generating reply using {self.name}")
        prompt = f"{self.prompt_prefix}\n{prompt}"
        return gen_text(prompt, self.model_path)

    def get_reply(self, content):
        for text_filter in text_filters:
            content = text_filter.filter(content)

        res = self._gen_text(content)

        if "[bait_end]" in res:
            res = res.split("[bait_end]", 1)[0]

        m = re.match(r"^.*[.?!]", res, re.DOTALL)
        if m:
            res = m.group(0)

        return res

    def get_reply_by_his(self, addr):
        with open(os.path.join(MAIL_ARCHIVE_DIR, addr + ".his"), "r", encoding="utf8") as f:
            content = f.read()
        return self.get_reply(content + "\n[bait_start]\n")


class MailReplier(Replier):
    def __init__(self):
        super().__init__("MailReplier", MAIL_PROMPT)


class WhatsAppReplier(Replier):
    def __init__(self):
        super().__init__("WhatsAppReplier", WA_PROMPT)


class InstagramReplier(Replier):
    def __init__(self):
        super().__init__("InstagramReplier", IG_PROMPT)


class FacebookReplier(Replier):
    def __init__(self):
        super().__init__("FacebookReplier", FB_PROMPT)
