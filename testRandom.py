
L = [1, 2, 3, 4, 5]

try :
    L.remove(3)
    L.remove(6)
except ValueError as e:
    print("ValueError:", e)

print(L)