import hello
import time

if __name__ =='__main__':
    start = time.time()
    hello.MAIN('bff')
    end = time.time()
    print('Total run time is %0.2f Seconds' % (end - start))