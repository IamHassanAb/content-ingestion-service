## Broker settings.
broker_url = 'amqp://guest:guest@localhost:5672//'

# backend_url = 'mongodb+srv://db_user:150Mbps%40ATLAS@learningcluster.dscnkzi.mongodb.net/balagh_bot.lectures?retryWrites=true&w=majority&appName=LearningCluster'

# List of modules to import when the Celery worker starts.
imports = ('myapp.tasks',)

## Using the database to store task state and results.
# result_backend = 'db+sqlite:///results.db'

task_annotations = {'tasks.translate': {'rate_limit': '10/m'}}


task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Karachi'
enable_utc = True