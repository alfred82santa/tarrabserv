import random
import string

__author__ = 'alfred'


def create_code(length=18, prefix=""):
    length -= len(prefix) + 1  # Prefix + Checksum digit
    code = str(prefix) + ''.join(random.choice(string.digits) for x in range(length - 1))
    return code + luhn_digit(code)


def luhn_digit(code):
    it = 0
    for letter in list(string.ascii_letters):
        subs = str(it % 10)
        code = code.replace(letter, subs)
        it += 1
    num = list(map(int, str(code)))
    check_digit = 10 - sum(num[-2::-2] + [sum(divmod(d * 2, 10)) for d in num[::-2]]) % 10
    if check_digit == 10:
        return '0'
    else:
        return str(check_digit)
