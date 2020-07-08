import json

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from pynats import NATSClient
from evaluate import evaluate
from problem_init import init
from models import Base
from config import Config


def message_handler(msg):
    obj = json.loads(msg.payload.decode('utf-8'))
    if obj['type'] == 'evaluate':
        evaluate(obj['submission_id'], session)
    elif obj['type'] == 'problem_init':
        init(obj['problem_id'])
    else:
        print('Unsupported type of query: {}'.format(obj['type']), flush=True)


if __name__ == "__main__":
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Base.metadata.create_all(engine)
    session = Session(bind=engine)

    nats = NATSClient(Config.NATS_SERVER, name=Config.INVOKER_NAME)
    nats.connect()
    nats.subscribe('invokers', queue='worker', callback=message_handler)
    nats.wait() # TODO: reconnect