import main , time

def runParser() :
    fileName = 'sample.ourjs'
    text = ""
    with open(fileName, 'r') as file:
        text = file.read()

    if text.strip() == "" : return
    result, error = main.run(fileName, text)

    if error: print(error.as_string())
    else: print(result)

start_time = time.time()
runParser()
#Calculate Run Time
finish_time = time.time()
total_run_time = finish_time - start_time
print("\nTotal Run Time is:", total_run_time, "seconds")