import redis

def watch_and_track():
    r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    pubsub = r.pubsub()
    pubsub.psubscribe('__keyspace@0__:*')

    print("감시 시작...")

    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            channel = message['channel']          
            event = message['data']               
            key = channel.split(":")[-1]

            print(f"[Event] key={key}, event={event}")

            if event == 'hset':
                current_fields = r.hgetall(f"task:{key}")
                print(f"현재 필드 상태: {current_fields}")

if __name__ == "__main__":
    try:
        watch_and_track()
    except KeyboardInterrupt:
        print("\n감시 종료됨.")
