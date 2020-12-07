import pika
import uuid

def send(channel_name, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=channel_name,
                             exchange_type='fanout')
    channel.basic_publish(exchange=channel_name,
                          routing_key='',
                          body=str(message))
    connection.close()


def recv(channel_name, callbck):
    _uuid=str(uuid.uuid4())
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
    channel = connection.channel()
    result = channel.queue_declare(exclusive=True, queue=_uuid)
    queue_name = result.method.queue
    channel.queue_bind(exchange=channel_name,
                       queue=queue_name)

    def callback(ch, method, properties, body):
        return callbck(ch, method, properties, body)

    channel.basic_consume(queue_name, callback,
                          auto_ack=True)
    channel.start_consuming()
