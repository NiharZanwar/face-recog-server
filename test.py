def make_log(string):
    string += '\n'
    with open('transaction_log.txt', 'a+') as log:
        log.write(string)


make_log('hello')
make_log('world')