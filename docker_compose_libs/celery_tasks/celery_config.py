import os
# rabbitMQ_user = os.environ.get("RABBITMQ_USER")
# rabbitMQ_password = os.environ.get("RABBITMQ_PWD")
# rabbitMQ_port = os.environ.get("RABBITMQ_PORT")

# rabbitMQ_user = "user"
# rabbitMQ_password = "password"
# rabbitMQ_port = 5672

# broker_url = f'pyamqp://{rabbitMQ_user}:{rabbitMQ_password}@broker:{rabbitMQ_port}'
broker_url = os.environ.get("CELERY_BROKER")
result_backend = 'rpc://'