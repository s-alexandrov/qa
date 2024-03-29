from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager

engine = create_engine('sqlite:///test.db')
Base = declarative_base()
Session = scoped_session(sessionmaker(autoflush=True, autocommit=False, bind=engine))


@contextmanager
def session_scope():
        session = Session()
        try:
            yield session
            session.commit()
        except:
            print("OTRABOTAL ROLLBACK")
            session.rollback()
            raise
        finally:
            session.close()


class Orders(Base):
    """Заказы в БД."""

    __tablename__ = "order"
    id = Column(Integer, autoincrement=True, primary_key=True, comment="id заказа")
    address_from = Column(String, nullable=False, comment="Откуда")
    address_to = Column(String, nullable=False, comment="Куда")
    client_id = Column(String, ForeignKey('clients.id'), comment="Клиент")
    driver_id = Column(String, ForeignKey('drivers.id'), comment="Водитель")
    date_created = Column(datetime, default=datetime.utcnow, comment="Дата заказа")
    status = Column(String, nullable=False, comment="Статус")

    status_orders = {
        "not_accepted": "not_accepted",
        "in_progress": "in_progress",
        "done": "done",
        "cancelled": "cancelled",
    }

    # переопределение выдачи объекта на экран через print
    def __repr__(self):
        return "<Orders(Откуда={0}, Куда={1}, Клиент={2}, Водитель={3}, Дата заказа={4}, Статус={5})>".format(
            self.address_from,
            self.address_to,
            self.client_id,
            self.driver_id,
            self.date_created.strftime("%d-%b-%Y"),
            self.status)

    @contextmanager
    def get_order(self, order_id):
        """Запрос по id заказа."""
        with session_scope() as session:
            new_order = session.query(Orders).get(order_id)
            return new_order

    @contextmanager
    def get_status_order(self, order_id):
        """Запрос получения информации по заказу."""
        with session_scope() as session:
            status_order = session.query(Orders).filter(Orders.status == order_id).all()
            return status_order

    def create_order(self):
        """Создание заказа."""
        with session_scope() as session:
            session.add(self)
            session.commit()

    @contextmanager
    def status_order(self, order_id, new_order_id):
        """Статус заказа."""
        with session_scope() as session:
            session.query(Orders).filter(Orders.status == order_id).update({Orders.status: new_order_id})
            session.commit()


Base.metadata.create_all(engine)
