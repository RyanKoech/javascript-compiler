import main

while True:
    text = input("myjs > ")
    if text.strip() == "": continue
    result, error = main.run('<stdin>', text)

    if error: print(error.as_string())
    else: print(result)