import RPi.GPIO as GPIO
import threading
import time

# === Pin definitions ===
RED_PIN = 17
GREEN_PIN = 24
BLUE_PIN = 23

# === Global state ===
# status_code = 0  # 0=blink blue,1=blink red,2=blink green,3=solid green
# status_lock = threading.Lock()
# status_changed = threading.Event()
stop_event = threading.Event()

# === GPIO setup ===
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RED_PIN, GPIO.OUT)
GPIO.setup(GREEN_PIN, GPIO.OUT)
GPIO.setup(BLUE_PIN, GPIO.OUT)

def turn_off_all():
    GPIO.output(RED_PIN, GPIO.HIGH)
    GPIO.output(GREEN_PIN, GPIO.HIGH)
    GPIO.output(BLUE_PIN, GPIO.HIGH)

def set_solid(pin):
    turn_off_all()
    GPIO.output(pin, GPIO.LOW)  # ON for common anode

def blink_color(pin, blink_interval=0.5):
    try:
        #while not stop_event.is_set():
        #    if status_changed.is_set():
        #       break
        GPIO.output(pin, GPIO.LOW)    # ON
        time.sleep(.5)
    #    if status_changed.wait(blink_interval):
    #        break
        GPIO.output(pin, GPIO.HIGH)  # OFF
        time.sleep(.5)
    #    if status_changed.wait(blink_interval):
    #        break
    finally:
        # Always ensure the blinking pin is turned off on exit
        GPIO.output(pin, GPIO.HIGH)



def restart_indication():
    try:
        for i in range(3):
            GPIO.output(RED_PIN, GPIO.LOW)    # ON
            time.sleep(.5)
        #    if status_changed.wait(blink_interval):
        #        break
            GPIO.output(RED_PIN, GPIO.HIGH)  # OFF
            time.sleep(.5)
    finally:
        GPIO.output(RED_PIN, GPIO.HIGH)


def led_worker(muselsl_thread, pylsl_start_event, muselsl_start_event, error_flag):
    pylsl_start_event.is_set()
    
    current_code = None
    while not stop_event.is_set():
        # status_changed.clear()
        # with status_lock:
         #   code = status_code

        # if code != current_code:
           # print(f"[LED] status_code changed to {code}")
           # current_code = code

        # Flush previous state before applying new mode
        turn_off_all()

        if error_flag.is_set():
            # blinking red
            restart_indication()
        elif (not muselsl_start_event.is_set()):
            # blinking green
            blink_color(GREEN_PIN)
        elif (pylsl_start_event.is_set() and muselsl_start_event.is_set()):
            # solid green
            set_solid(GREEN_PIN)
            # wait until status change or stop
            #status_changed.wait()
        else:
            # invalid code, just off
            turn_off_all()
           # status_changed.wait()
        time.sleep(.1)

    # final cleanup
    turn_off_all()

# def get_status_code():
#     global status_lock, status_code
#     with status_lock:
#         return status_code

# def set_status_code(status_num):
#     global status_lock, status_code, status_changed
#     with status_lock:
#         if status_code != status_num:
#             status_code = status_num
#             status_changed.set()

# def main():
#     worker = threading.Thread(target=led_worker, daemon=True)
#     # cycle = threading.Thread(target=cycler, daemon=True)
#     worker.start()
#     # cycle.start()

#     try:
#         while True:
#             time.sleep(0.5)
#     except KeyboardInterrupt:
#         print("Interrupted, shutting down...")
#         stop_event.set()
#         status_changed.set()  # wake any waits
#         worker.join(timeout=1)
#         # cycle.join(timeout=1)
#     finally:
#         GPIO.cleanup()

# if __name__ == "__main__":
#     main()
