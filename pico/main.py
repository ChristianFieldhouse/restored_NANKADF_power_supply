from machine import Pin, PWM, Timer, ADC
import utime, time

clk = Pin(1, Pin.OUT)
cs = Pin(2, Pin.OUT)

class Buzzer():
    def __init__(self, pin, pip_length=100, enabled=False):
        self.pin = Pin(pin, Pin.OUT)
        self.pip_length = pip_length
        self.enabled = enabled
        self.tim_off = Timer(period=self.pip_length, mode=Timer.PERIODIC, callback=lambda t: self.pin.off())
    def pip(self, t=None):
        self.pin.value(self.enabled)
        #self.tim_really_off = Timer(period=200, mode=Timer.ONE_SHOT, callback=lambda t: self.pin.off())
    def really_pip(self):
        self.pin.on()
    def __repr__(self):
        return f"Buzzer, {self.pin}, {self.pip_length}, {self.tim_off}"

buzzer = Buzzer(pin=20, pip_length=30, enabled=False)

voltage_set = PWM(Pin(15))
voltage_set.freq(1000)
voltage_set.duty_u16(0)

current_set = PWM(Pin(14))
current_set.freq(1000)
current_set.duty_u16(0)

current_get = ADC(27)
voltage_get = ADC(26)
current_limited = ADC(28)

class RotaryEncoder():
    def __init__(self, step, step_min, step_max, pin_a, pin_b, on_update, limits, filename):
        self.a = Pin(pin_a, Pin.IN, Pin.PULL_UP)
        self.b = Pin(pin_b, Pin.IN, Pin.PULL_UP)
        self.a.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=lambda x: self.a_change())
        self.b.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=lambda x: self.b_change())
        #self.a.irq(trigger=, handler=lambda x: self.check_done())
        #self.b.irq(trigger=Pin.IRQ_RISING, handler=lambda x: self.check_done())
        self.transitioning = False
        self.transition_start = 0
        with open(filename, "rt") as f:
            line = f.readline()
            print(line)
            self.value = int(line)
        self.step = step
        self.step_min = step_min
        self.step_max = step_max
        self.step_change_time = 0
        self.on_update = on_update
        self.min = limits[0]
        self.max = limits[1]
        self.filename = filename
    def step_step(self):
        t = time.ticks_ms()
        if t - self.step_change_time > 1500:
            self.step_change_time = t
            return
        self.step = self.step + 1
        self.step_change_time = t
        if self.step > self.step_max:
            self.step = self.step_min
    def step_value(self, sign):
        self.value = self.value + sign*10**self.step
        print(buzzer)
        if self.value < self.min:
            self.value = self.min
            buzzer.pip(10) # shorter pip
        if self.value > self.max:
            self.value = self.max
            buzzer.pip(10)
        else:
            buzzer.pip()
        # todo : this doesn't work? (ENODEV)
        with open(self.filename, "wt") as f:
            f.write(str(self.value))
        print(self.value)
        self.on_update()
    def a_change(self):
        if self.a.value():
            self.check_done()
        else:
            self.a_down()
    def b_change(self):
        if self.b.value():
            self.check_done()
        else:
            self.b_down()
    def a_down(self):
        #print("a down")
        if not self.transitioning:
            self.transitioning = "from a"
            self.transition_start = time.ticks_ms()
        elif self.transitioning == "from b": # b already down
            self.transitioning = "ab"
            self.step_value(1)
    def b_down(self):
        #print("b down")
        if not self.transitioning:
            self.transitioning = "from b"
            self.transition_start = time.ticks_ms()
        elif self.transitioning == "from a": # a already down
            self.transitioning = "ba"
            self.step_value(-1)
    def check_done(self):
        """check if we're done transitioning"""
        if (
            (self.a.value() and self.b.value()) and
            time.ticks_ms() - self.transition_start > 1
        ):
            self.transitioning = False

def set_voltage(v):
    """zero intercept + linear"""
    intercept = 900
    gradient = 3.7273 / (8400 - intercept)
    if v <= 0:
        voltage_set.duty_u16(0)
    else:
        voltage_set.duty_u16(intercept + int(round(v/gradient)))

def set_current(a):
    """zero-intercept at 1960, linear from there"""
    intercept = 1960
    gradient = 0.32728/(4700 - intercept)
    if a <= 0:
        current_set.duty_u16(0)
    else:
        current_set.duty_u16(min(intercept + int(a/gradient), 2**16 - 1))

def get_current_limited_signal():
    return current_limited.read_u16() / (2**16 - 1)

def get_current(n=10):
    """linear with intercept"""
    intercept = 694
    gradient = 0.32728 / (2546 - intercept)
    return sum([
        gradient * (current_get.read_u16() - intercept)
        for _ in range(n)
    ])/n

def get_voltage(n=10):
    """linear with intercept"""
    intercept = 435
    gradient = 3.7273 / (1590 - intercept)
    return sum([
        gradient * (voltage_get.read_u16() - intercept)
        for _ in range(n)
    ])/n

def set_va():
    out = keyscan_buttons.output.value
    cc = get_current_limited_signal() > 0.5
    cv = not cc
    v = mv.value/1000
    a = ma.value/1000
    t = time.ticks_ms()
    time_since_update = min(t - ma.transition_start, t - mv.transition_start)
    display_target = (time_since_update < 250) or not out
    display_v = v if display_target else (v if cv else get_voltage(200))
    display_a = a if display_target else (a if cc else get_current(200))
    display_w = display_v*display_a
    text = (
        format_voltage(display_v) +
        format_current(display_a) +
        (format_current(display_w) if display_w < 0.1 else format_voltage(display_w))
    )

    cursors = []
    #print(t - mv.step_change_time)
    if t - mv.step_change_time < 1000:
        if (t - mv.step_change_time) % 200 < 100:
            cursors.append(mv.step_max - mv.step)
    if t - ma.step_change_time < 1000:
        if (t - ma.step_change_time) % 200 < 100:
            cursors.append(4 + ma.step_max - ma.step)

    #print(cursors)
    #print(text)
    update_display(
        text,
        dots=(1, 4, 8 if display_w < 0.1 else (9 if display_w < 100 else 10)),
        out=out, cc=cc*out, cv=cv*out,
        cursors=cursors,
    )
    set_voltage(v*out)
    set_current(a*out)

cs.on() # go low for instruction

# start from lowest bits
data = [0, 1, 0, 0, 0, 0, 0, 0][::-1] + [1,]*16

segments = {
    "0": (0, 1, 2, 3, 5, 7),
    "1": (3, 5),
    "2": (1, 3, 4, 0, 7),
    "3": (1, 3, 4, 5, 7),
    "4": (2, 3, 4, 5),
    "5": (1, 2, 4, 5, 7),
    "6": (0, 1, 2, 4, 5, 7),
    "7": (1, 2, 3, 5),
    "8": (0, 1, 2, 3, 4, 5, 7),
    "9": (1, 2, 3, 4, 5, 7),
    "*": (0, 1, 2, 3, 4, 5, 6, 7),
    "A": (0, 1, 2, 3, 4, 5),
    "C": (0, 1, 2, 7),
    "H": (0, 2, 3, 4, 5),
    "V": (0, 2, 3, 5, 7),
    "E": (0, 1, 2, 4, 7),
    "F": (0, 1, 2, 4),
    "U": (0, 2, 3, 5, 7),
    "N": (0, 1, 2, 3, 5),
    "h": (0, 2, 4, 5),
    "r": (0, 4),
    "i": (0,),
    "s": (1, 2, 4, 5, 7),
    "t": (0, 2, 4, 7),
    "a": (0, 4, 5, 6, 7),
    "n": (0, 4, 5),
    "e": (0, 1, 2, 3, 4, 7),
    "o": (0, 4, 5, 7),
    "u": (0, 5, 7),
    "v": (0, 5, 7),
    "*": (1, 2, 3, 4),
    "!": (3, 5, 6),
    ".": (6,),
    " ": (),
}

def read_keyscan(tick = 0.0001):
    read_command = [0, 1, 0, 0, 0, 0, 1, 0]
    cs.off()
    clk.off()
    utime.sleep(tick)
    dio = Pin(3, Pin.OUT)
    for d in read_command:
        #print(d)
        clk.off()
        utime.sleep(tick)
        dio.value(d)
        utime.sleep(tick)
        clk.on()
        utime.sleep(tick)
    utime.sleep(0.001) # "at least 1us"
    dio = Pin(3, Pin.IN)
    vals = []
    for i in range(8):
        for k in range(4):
            clk.off()
            utime.sleep(tick)
            if k == 3:
                vals.append(dio.value())
            utime.sleep(tick)
            clk.on()
            utime.sleep(tick)
    clk.off()
    cs.on()
    return vals

def write_serial(data, tick = 0.0001):
    cs.off()
    clk.off()
    utime.sleep(tick)
    dio = Pin(3, Pin.OUT)
    for d in data:
        #print(d)
        clk.off()
        utime.sleep(tick)
        dio.value(d)
        utime.sleep(tick)
        clk.on()
        utime.sleep(tick)
    clk.off()
    cs.on()

def turn_display_on():
    # works!!!
    data = [1, 0, 0, 0, 1, 0, 0, 0][::-1]
    write_serial(data)

def set_display_pwm(n=2):
    # n in 0-7
    data = [1, 0, 0, 0, 1] + [1*(c=="1") for c in '{0:03b}'.format(n)]
    print(data)
    write_serial(data[::-1])

def set_address(addr=0):
    data = ([1, 1, 0, 0] + [c=="1" for c in '{0:04b}'.format(addr)])[::-1]
    write_serial(data)

def update_memory(n, addr=0):
    set_address(addr)
    data = [0, 1, 0, 0, 0, 0, 0, 0][::-1]
    nbits = [c=="1" for c in '{0:016b}'.format(n)]
    bit_data = nbits[:8][::-1] + nbits[8:16][::-1]
    write_serial(data+bit_data)

def update_display(digits=None, dots=(), cursors=(), ocp=False, cc=False, cv=False, out=False):
    new_memory = [0 for _ in range(8)] #2-byte words
    remap = [4, 5, 6, 7, 13, 12, 11, 14, 1, 0, 15, 2] #3 is the colour leds
    for i, d in enumerate(digits[:12]):
        for segment in range(8):
            if segment in segments[d]:
                new_memory[segment] += 2**(15-remap[i])
    # add dots
    for dot in dots:
        new_memory[6] += 2**(15-remap[dot])
    lights = [ocp*1, out*2, cv*5, cc*7]
    for light in lights:
        if light != 0:
            new_memory[light] += 2**(15 - 3)
    for cursor in cursors:
        new_memory[7] = new_memory[7] ^ 2**(15-remap[cursor])
    for addr, word in zip(range(0, 16, 2), new_memory):
        update_memory(word, addr)

def format_voltage(v):
    if v >= 10:
        return f"{round(v*100)}"
    if v > 1:
        return f"{round(v*100): 4d}"
    if v <= 0:
        v = 0
    return " " + f"{round(v*100):03d}"

def format_current(a):
    if a <= 0:
        a = 0
    return f"{round(a*1000):04d}"

class Button():
    """Keeps track of the state of a toggle button"""
    def __init__(self, value=False, debounce_ms=100):
        self.state = False # whether being pressed or not
        self.value = value
        self.debounce_ms = debounce_ms
        self.state_change_time = time.ticks_ms()
    def update(self, state):
        if self.state == state:
            return False # no state change
        t = time.ticks_ms()
        if (t - self.state_change_time) <= self.debounce_ms:
            return False # too fast a state change
        # accept state change
        self.state = state
        self.state_change_time = t
        if self.state: # transition low to high
            self.value = not self.value
            buzzer.pip()
            return True
        return False # transitioned high to low

class KeyscanButtons():
    def __init__(self, on_update):
        self.output = Button()
        self.voltage = Button()
        self.current = Button()
        self.on_update = on_update
        self.update_anyway_after = 1
        self.update_anyway_count = 0

    def keyscan_update(self):
        k = read_keyscan()
        if self.output.update(k[0]):
            self.on_update()
        if self.voltage.update(k[1]):
            mv.step_step()
        if self.current.update(k[2]):
            ma.step_step()
        #print(self.output, self.voltage, self.current)
        self.update_anyway_count += 1
        if self.update_anyway_count == self.update_anyway_after:
            self.update_anyway_count = 0
            self.on_update()

turn_display_on()
set_display_pwm()
update_display("HAVEFUN o*o*")
for _ in range(2):
    buzzer.really_pip()
    utime.sleep(0.1)
for _ in range(4):
    update_display("HAVEFUN *o*o")
    utime.sleep(0.1)
    update_display("HAVEFUN o*o*")
    utime.sleep(0.1)

#with open("mv.txt") as f:
#    f.write("3000")
#with open("ma.txt") as f:
#    f.write("300")

mv = RotaryEncoder(step=2, step_min=1, step_max=4, pin_a=16, pin_b=17, on_update=set_va, limits=(0, 30_000), filename="mv.txt")
ma = RotaryEncoder(step=1, step_min=0, step_max=3, pin_a=19, pin_b=18, on_update=set_va, limits=(0, 5_000), filename="ma.txt")
keyscan_buttons = KeyscanButtons(on_update=set_va)
tim = Timer(period=100, mode=Timer.PERIODIC, callback=lambda t: keyscan_buttons.keyscan_update())

