url = "https://mausam.imd.gov.in/thiruvananthapuram/mcdata/iadp%20rainfall.pdf"

from pdfminer.high_level import extract_text
text = extract_text('simple1.pdf')
#print(repr(text))
line = text.strip('\n')
line = line.strip('\t')
f = open("demo.txt", "a")

s =""
flag = 0
count = 0
for i in line:
    s += i
    if i=='\n':
        flag += 1
        if flag==1:
            count += 1
            print(count)
            s = s + "count = "+str(count)+" | "
            f.write(s)
            
        print("----++++\n")

        s=""
    else:
        flag=0
f.close()

#print(line)