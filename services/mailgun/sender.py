import os
import requests
from constants import API_KEY, API_BASE_URL, MAIL_TEMPLATE, RECEIVER_EMAIL

with open(MAIL_TEMPLATE, "r") as f:
    template = f.read()


def send_email(username, address, target, subject, text):
    if type(target) == str:
        target = [target]

    print(f"Trying to send an email from {address} to {target}")

    res = requests.post(
        f"https://api.mailgun.net/v3/{API_BASE_URL}/messages",
        auth=("api", API_KEY),
        data={"from": f"{username} <{address}>",
              "to": target,
              "subject": str(subject),
              "html": template.replace("{{{content}}}", text).replace("\n", "<br>")})
    if not ("Queued." in res.text):
        print(f"Failed to send, {res.text}")
        return False
    return True


if __name__ == '__main__':
    print(send_email("Tester", "00o00@mail.sdchaos.top", f"{RECEIVER_EMAIL}", "==Test==",
                     "Tvarov has received your email. We must ensure no third parties are required to open the sent to you, so we cannot predict the later of releasing the requested funds over there. Here are the details police state the ount should pay to the account outage.STILL WAITING FOR YOUR REPLY AS SOON AS WE GET TO IT.TRAGUANTEBROZI SNIP INTO REPUSING FOR MONEY WITH IN LAGOS LOYAL.\nBest,\nTester"))
