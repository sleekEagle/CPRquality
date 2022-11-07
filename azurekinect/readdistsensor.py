import csv
import matplotlib.pyplot as plt

file=r'C:\Users\lahir\Documents\CPR Quality Data\CoolTerm Capture 2022-10-20 15-15-25.txt'
ts,val=[],[]
with open(file, newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in spamreader:
        try:
            splt= (', '.join(row)).split()
            ts_=splt[0]
            val_=int(splt[1])
            ts.append(ts_)
            val.append(val_)
        except Exception as e:
            print(str(e))

plt.plot(val)
plt.show()
