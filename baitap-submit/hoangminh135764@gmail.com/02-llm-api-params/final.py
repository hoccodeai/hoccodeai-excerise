
def tower_of_hanoi(n):
    if n == 1:
        print("Move disk 1 from peg 1 to peg 3")
    else:
        tower_of_hanoi(n-1)
        print("Move disk", n, "from peg 1 to peg 2")
        print("Move disk", n-1, "from peg 3 to peg 1")
        print("Move disk", n, "from peg 2 to peg 3")

n = int(input("Enter the number of disks: "))
print("To move", n, "disks from peg 1 to peg 3, the following sequence of moves is:")
tower_of_hanoi(n)
