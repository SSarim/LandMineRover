import sys
import json
import time
import pika
import hashlib
from concurrent.futures import ThreadPoolExecutor

# Thread Pool for multithreading (4 threads)
executor = ThreadPoolExecutor(max_workers=4)

def disarm_mine(serial):
    pin = 0
    while True:
        candidate = str(pin)
        temp_key = serial + candidate
        hashed = hashlib.sha256(temp_key.encode('utf-8')).hexdigest()
        if hashed.startswith("000000"):
            return candidate
        pin += 1
# Mine serial number to find the PIN, Increment the PIN until the hash starts with 6 zeros.

def process_message(ch, method, properties, body, deminer_id):
    try:
        data = json.loads(body)
        mine_serial = data.get("mine_serial")
        if not mine_serial:
            print("Message does not contain a mine_serial. Skipping.")
            return
        print(f"Deminer {deminer_id} is processing mine {mine_serial}...")
        pin = disarm_mine(mine_serial)
        print(f"Mine {mine_serial} disarmed with PIN {pin}")

        # Disarmed mine info to the Defused_Mines queue.
        result = {
            "mine_serial": mine_serial,
            "pin": pin,
            "deminer": deminer_id
        }
        result_message = json.dumps(result)
        ch.basic_publish(
            exchange='',
            routing_key='Defused-Mines',
            body=result_message
        )
        print(f"Deminer {deminer_id} published info to Defused_Mines channel.")

        #Defused mines to the text file.
        with open("Defused_Mines.txt", "a") as f:
            f.write(f"Mine {mine_serial} disarmed by Deminer {deminer_id} with PIN {pin} \n")
    except Exception as e:
        print(f"Error processing message: {e}")
    finally:
        # Acknowledgement (thread-safe)
        ch.connection.add_callback_threadsafe(lambda: ch.basic_ack(delivery_tag=method.delivery_tag))

def on_message(ch, method, properties, body):
    print(f"Deminer {deminer_id} received message: {body.decode()}")
    # Process to the thread pool
    executor.submit(process_message, ch, method, properties, body, deminer_id)

def main():
    global deminer_id
    if len(sys.argv) != 2:
        print("use the command: python deminers.py <deminer_number>")
        sys.exit(1)
    try:
        deminer_id = int(sys.argv[1])
        if deminer_id not in [1, 2]:
            raise ValueError()
    except ValueError:
        print("Please provide a valid deminer number (1 or 2).")
        sys.exit(1)

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # queues
    channel.queue_declare(queue='Demine-Queue', durable=True)
    channel.queue_declare(queue='Defused-Mines', durable=True)

    # multiple unacknowledged messages concurrently for async communication(4 threads)
    channel.basic_qos(prefetch_count=4)

    # concurrency by a thread from the pool
    channel.basic_consume(queue='Demine-Queue', on_message_callback=on_message)

    print(f"Deminer {deminer_id} is waiting for messages in Deminer-Queue. Press CTRL+C to exit.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Stopping deminer...")
        channel.stop_consuming()
    connection.close()

if __name__ == '__main__':
    main()

#  docker run -d --name mqserver -p 5672:5672 -p 15672:15672 rabbitmq:management
# for UI access: http://localhost:15672/, lofin is guest, guest
#start docker container "docker start mqserver"
#start Ground Control Server "python ground_control_server.py"
#start Deminer 1 "python deminers.py 1"
#start Deminer 2 "python deminers.py 2"
#start Rover 1-10 "python rover_client.py [Number]"
