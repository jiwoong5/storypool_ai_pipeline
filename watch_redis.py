from prometheus_client import start_http_server, Counter
import redis

event_counter = Counter('redis_keyspace_events', 'Count of Redis keyspace events', ['event_type'])

def watch_and_track():
    r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    pubsub = r.pubsub()
    pubsub.psubscribe('__keyspace@0__:*')

    print("감시 시작...")
    start_http_server(8000)

    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            channel = message['channel']
            event = message['data']
            key = channel.split(":")[-1]

            print(f"[Event] key={key}, event={event}")
            event_counter.labels(event_type=event).inc()

            if event == 'hset':
                current_fields = r.hgetall(f"task:{key}")
                print(f"현재 필드 상태: {current_fields}")
