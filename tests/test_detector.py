from services.messenger_switch_detector import MessengerSwitchDetector

detector = MessengerSwitchDetector()
result = detector.predict_switch("I think it is best, if we talk about this, please call +01 123 123 123 ?")
print(result)
