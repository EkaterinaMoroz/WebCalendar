import datetime
import sys
from flask import Flask, abort
from flask_restful import Api, Resource, reqparse, inputs, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'


class Event(db.Model):
    __tablename__ = 'Calendar'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)


db.create_all()

resource_fields = {
    'id': fields.Integer,
    'event': fields.String,
    'date': fields.String
}


parser_post = reqparse.RequestParser()
parser_post.add_argument(
    'date',
    type=inputs.date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=True
)
parser_post.add_argument(
    'event',
    type=str,
    help="The event name is required!",
    required=True
)

parser_get = reqparse.RequestParser()
parser_get.add_argument(
    'start_time',
    type=inputs.date,
    help="The event date with the correct format is required!",
    required=False
)
parser_get.add_argument(
    'end_time',
    type=inputs.date,
    help="The event date with the correct format is required!",
    required=False
)


class GetResourceById(Resource):
    @marshal_with(resource_fields)
    def get(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        return event

    def delete(self, event_id):
        if Event.query.filter(Event.id == event_id).first() is not None:
            db.engine.execute(f"delete from calendar where id={event_id}")
            return {"message": "The event has been deleted!"}
        else:
            abort(404, "The event doesn't exist!")


class GetResourceToday(Resource):
    @marshal_with(resource_fields)
    def get(self):
        return Event.query.filter(Event.date == datetime.date.today()).all()


class GetResource(Resource):
    @marshal_with(resource_fields)
    def get(self):
        args = parser_get.parse_args()
        if args['start_time'] or args['end_time']:
            events = Event.query.filter(Event.date.between(args['start_time'], args['end_time'])).all()
            return events
        else:
            return Event.query.all()

    def post(self):
        args = parser_post.parse_args()
        ev = Event(event=args['event'], date=args['date'].date())
        db.session.add(ev)
        db.session.commit()
        return {
            "message": "The event has been added!",
            "id": int(ev.id),
            "event": args['event'],
            "date": str(args['date'].date())
        }


api.add_resource(GetResource, '/event')
api.add_resource(GetResourceToday, '/event/today')
api.add_resource(GetResourceById, '/event/<int:event_id>')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)

    else:
        app.run(debug=True)
