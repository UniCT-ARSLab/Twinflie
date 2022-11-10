import json

test="(0.128788, -6.592324, 0.242426)".replace("(","").replace(")","").replace(" ","").split(",")
test2="(0.128788, -6.592324, 0.242426)"

#dict=(0.128788, -6.592324, 0.242426)
exec("dict="+test2)

for x in dict:
    print(float(x))