from huskylib import HuskyLensLibrary
hl = HuskyLensLibrary("I2C","", address=0x32)

# hl.forget()
# print(hl.learned(),hl.blocks(),hl.count())
# hl.customText('hi',120,120)

try:
    print('try')
    print(hl.learned(),hl.blocks(),hl.count(),hl.learnedObjCount())

    # hl.learn(1)
    hl.forget()
    # print(hl.learned(),hl.blocks(),hl.count(),hl.learnedObjCount())

    # Code that may raise AttributeError
    # bus.flushInput()
except AttributeError:
    # Code to handle the AttributeError
    print("AttributeError: SMBus object has no attribute 'flushInput'")
    print(hl.learned(),hl.blocks(),hl.count(),hl.learnedObjCount())

