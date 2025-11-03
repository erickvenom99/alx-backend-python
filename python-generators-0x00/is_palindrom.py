#!/usr/bin/env python3
"""
Finds palindrome
"""
def is_infinite():
    num = 0
    while True:
        if is_palindrome(num):
            i = (yield num)
            if i is not None:
                num = i
        num += 1

def is_palindrome(num):
    """
    check if a number is palindrom, return num
    or false
    """
    
    if num // 10 == 0:
        return False
    reverse_num = 0
    temp = num
    while temp != 0:
        reverse_num = (reverse_num * 10) + ( temp % 10)
        temp = temp // 10
    if num == reverse_num:
        return True
    else:
        return False

if __name__ == "__main__":
    pals = is_infinite()
    for pal in pals:
        print(pal)
        digit = len(str(pal))
        pal.send(10 ** (digit))
