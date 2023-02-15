import smtplib, ssl, getpass
from secretforlocalsetup import APP_PASSWORD, SENDER_EMAIL, RECEIVER_EMAIL
 

port = 465  # For SSL
password = APP_PASSWORD

# Create a secure SSL context
context = ssl.create_default_context()

with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
	server.login("icrabmeats19@gmail.com", password)
	# TODO: Send email here
	message = "Subject: test \n\n watch out"

	server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message)