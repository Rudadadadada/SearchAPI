from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy_serializer import SerializerMixin

from app.database.db_session import Base, create_session


# Здесь описаны модели, которые лежат в бд
class Folder(Base, SerializerMixin):
    __tablename__ = 'folders'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    parent_id = Column(Integer, ForeignKey('folders.id'), nullable=False)
    folder_url = Column(String, nullable=False)

    def __init__(self, parent_id, folder_url):
        self.parent_id = parent_id
        self.folder_url = folder_url

    @staticmethod
    def create_root():
        session = create_session()

        request = list(session.query(Folder.id).filter(Folder.id == 1))
        if len(request) == 0:
            root = Folder(parent_id=1, folder_url='/')

            session.add(root)
            session.commit()


class File(Base, SerializerMixin):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey('folders.id'), index=True, nullable=False)
    file_url = Column(String, nullable=False)

    file_text = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    creation_time = Column(DateTime, nullable=False)

    def __init__(self, parent_id, file_url, file_text, size, creation_time):
        self.parent_id = parent_id
        self.file_url = file_url
        self.file_text = file_text
        self.size = size
        self.creation_time = creation_time
