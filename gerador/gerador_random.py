import random

size = 25
save = "25x25"
pieces = ['FC','FB','FE','FD','BC','BB','BE','BD','VC','VB','VE','VD','LH','LV']

with open(save + ".txt", 'w') as f:
    for i in range(size*size):
        f.write(pieces[random.randint(0, len(pieces) - 1)])
        if i != 0 and (i+1) % size == 0:
            f.write("\n")
        else:
            f.write("\t")