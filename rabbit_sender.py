import pika
import uuid

"""
Helper file used to factor the functions used to send and/or receive rabbitmq messages
"""

def send(channel_name, message):
    """
    Sends a message to the channel on localhost
    We use fanout mode since the idea is that anyone could listen to any event
    """
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
    """
    Connect to a channel on localhost
    Use it on a new thread since it will block the thread using it
    """
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
