from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import threading
import asyncio


tasks = {}


from led_indicator import led_worker
# , get_status_code, set_status_code
from muse_stream import start_muse_stream, update_eeg_buffer
from classifier import classify
import time

muselsl_start_event = threading.Event()
muselsl_stop_event = threading.Event()
pylsl_stop_event = threading.Event()
pylsl_start_event = threading.Event()
classifier_stop_event = threading.Event()
classifier_thread = None
pylsl_thread = None
muselsl_thread = None
blink_collection_thread = None
error_flag = threading.Event()
def connect_muse(mac_address: str):
    global muselsl_thread, muselsl_start_event, muselsl_stop_event, pylsl_thread, pylsl_stop_event, classifier_stop_event, classifier_thread
    pylsl_start_event.clear()
    pylsl_stop_event.clear()
    muselsl_start_event.clear()
    muselsl_stop_event.clear()
    classifier_stop_event.clear()
    error_flag.clear()
    muselsl_thread = threading.Thread(target=start_muse_stream, args=(mac_address, muselsl_start_event, muselsl_stop_event, error_flag))
    muselsl_thread.start()

    while not muselsl_start_event.is_set() and muselsl_thread.is_alive():
        time.sleep(0.1)

    if muselsl_start_event.is_set():
        pylsl_thread = threading.Thread(target=update_eeg_buffer, args=(pylsl_start_event, pylsl_stop_event, error_flag))
        pylsl_thread.start()
        while not pylsl_start_event.is_set() and pylsl_thread.is_alive():
            time.sleep(0.1)
        if pylsl_start_event.is_set():
            time.sleep(3)
           # classifier_stop_event.set()
            classifier_thread = threading.Thread(target=classify, args=(classifier_stop_event, error_flag))
            classifier_thread.start()

    return {"data" : "Stream Stopped"}



def disconnect_muse():
    global muselsl_thread, muselsl_stop_event, pylsl_stop_event, classifier_thread, classifier_stop_event
    classifier_stop_event.set()
    print("from main", classifier_stop_event)
    if classifier_thread is not None:
        classifier_thread.join()
    pylsl_stop_event.set()
    if pylsl_thread is not None:
        pylsl_thread.join()  # Wait for the thread to terminate
    muselsl_stop_event.set()
    if muselsl_thread is not None:
        muselsl_thread.join()
    return {"data": "Pylsl and muselsl terminated"}

def main():
    global led_indicator_thread, muselsl_thread, pylsl_start_event, muselsl_start_event, error_flag
    led_indicator_thread = threading.Thread(target=led_worker, args=(muselsl_thread, pylsl_start_event, muselsl_start_event, error_flag), daemon=True)
    led_indicator_thread.start()
    while True:
        try:
            response = connect_muse('00:55:DA:B0:1E:78')
            muselsl_thread.join()
            print(response)
        except Exception as e:
            print(e)
        finally:
            disconnect_muse()
if __name__ == "__main__":
    main()