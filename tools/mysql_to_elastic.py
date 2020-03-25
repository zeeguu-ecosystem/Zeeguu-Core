# coding=utf-8
import sqlalchemy as database
from elastic.converting_from_mysql import document_from_article
from sqlalchemy import func
from elasticsearch import Elasticsearch
import zeeguu_core
from sqlalchemy.orm import sessionmaker
from zeeguu_core.model import Article
from zeeguu_core.settings import INDEX_NAME, ELASTIC_CONN_STRING

es = Elasticsearch([ELASTIC_CONN_STRING])
DB_URI = zeeguu_core.app.config["SQLALCHEMY_DATABASE_URI"]
engine = database.create_engine(DB_URI)
Session = sessionmaker(bind=engine)
session = Session()


def main():
    max_id = session.query(func.max(Article.id)).first()[0]
    for i in range(0, max_id, 5000):
        # fetch 5000 articles at a time, to avoid to much loaded into memory
        for article in session.query(Article).order_by(Article.published_time.desc()).limit(5000).offset(i):
            doc = document_from_article(article, session)
            res = es.index(index=INDEX_NAME, id=article.id, body=doc)
            if article.id % 1000 == 0:
                print(res['result'] + str(article.id))


if __name__ == '__main__':
    main()
