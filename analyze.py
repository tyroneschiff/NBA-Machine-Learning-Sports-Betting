import re
def run():
    with open('/home/admin_/NBA-Machine-Learning-Sports-Betting/output.txt') as fp:
        x = fp.readlines()
        for i in x:
            # Philadelphia 76ers (90.8%) vs Orlando Magic: UNDER 214.5 (54.2%)
            # Washington Wizards vs Brooklyn Nets (52.2%): UNDER 234.5 (56.0%)
            j = re.search("(.*?) \((.*?\))", i.strip())
            x = re.search("[.*?]+ vs (.*?) \((.*?\))", i.strip())
            if x is None:
                print('nope')
            else:
                #print(j.group(0))
                print(x.group(0))
            if j is None:
                print('nope')
            else:
                print(j.group(0))

if __name__ == "__main__":
    run()