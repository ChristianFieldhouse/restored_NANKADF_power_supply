import numpy as np
import time
from tqdm import tqdm
#import usbtmc
#instr = usbtmc.Instrument("USB::6833::1303::INSTR")
import pyvisa as visa
#Create a resource manager
resources = visa.ResourceManager('@py')
instr = resources.open_resource('USB0::6833::1303::DS1ZE243207729::0::INSTR')
#Return the Rigol's ID string to tell us it's there
print(instr.query('*IDN?'))

instr.ask = instr.query
print(instr.ask("*IDN?"))
import pyboard
pyb = pyboard.Pyboard('/dev/ttyACM0')
pyb.enter_raw_repl()
pyb.exec("from main import *")

def get_preamble():
    # https://beyondmeasure.rigoltech.com/acton/attachment/1579/f-af444326-0551-4fd5-a277-bf8fff6f53cb/1/-/-/-/-/DS1000Z-E_ProgrammingGuide_EN.pdf
    # ^ documentation doesn't get this right
    read = instr.ask(":wav:pre?")
    #print(read)
    return {
        key: float(value)
        for key, value in zip(
            [
                "format",
                "type",
                "points",
                "count",
                #"xincrement",
                #"xorigin",
                #"xreference",
                #"yincrement",
                #"yorigin",
                #"yreference",
            ],
            read.split(",")
        )    
    }

def read(start=1, stop=None, form="byte", step=40):
    preamble = get_preamble()
    #print(preamble)
    if stop is None:
        stop = int(preamble["points"])
    for command in [
        #":stop",
        ":wav:mode norm", #raw
        ":wav:sour chan2",
        f":wav:form {form}",
        #":wav:data?",
    ]:
        instr.write(command)
    
    if stop is None:  
        stop = int(preamble["points"])
    
    if form == "asc": # this works but is slooooowww
        all_data = []
        step=3
        for i in tqdm(range(1, stop+1, step)):
            for command in [
                f":wav:star {i}",
                f":wav:stop {min(stop, i+step-1)}",
                ":wav:data?",
            ]:
                #print(command)
                instr.write(command)
            new_read = instr.read()
            #print("new read : ", new_read)
            all_data += [float(f) for f in new_read[11:].split(",")]
        return all_data
    elif form == "byte":
        all_data = []
        yorigin = float(instr.ask(":wav:yor?"))
        yreference = float(instr.ask(":wav:yref?"))
        yincrement = float(instr.ask(":wav:yinc?"))
        for i in range(1, stop+1, step):
            for command in [
                f":wav:star {i}",
                f":wav:stop {min(stop, i+step-1)}",
                ":wav:data?",
            ]:
                #print(command)
                instr.write(command)
            new_read = instr.read_raw()
            #print("new read : ", new_read)
            all_data += [yincrement*(float(f)-yorigin-yreference) for f in new_read[11:-1]]
        return all_data

#data = read(start=1, stop=200, form="byte")

pyb.exec(f"set_va(3, 0.5)")
for dc in range(5000, 0, -100):
    #pyb.exec(f"set_va(3, {a})")
    pyb.exec(f"current_set.duty_u16({dc})")
    #print(ser.readline(100))
    time.sleep(0.1)
    #print(dc, np.mean(read(start=1, stop=200, form="byte")), np.mean([int(pyb.exec("print(voltage_get.read_u16())").decode()[:-2]) for _ in range(200)]))
    print(dc, np.mean(read(start=1, stop=200, form="byte")), np.mean([int(pyb.exec("print(current_get.read_u16())").decode()[:-2]) for _ in range(200)]))
    #print(dc, np.mean(read(start=1, stop=200, form="byte")), pyb.exec("print(get_voltage())").decode()[:-2])


