



def x():
    print("z")

x()
stringa_di_codice="""
print('x')\nprint('y')
          """
x=lambda:(exec(stringa_di_codice))

x()