import time

import tm1637

tm = tm1637.TM1637(clk=5, dio=4)

for i in range(99):
    tm.temperature(i)
    time.sleep(1)
