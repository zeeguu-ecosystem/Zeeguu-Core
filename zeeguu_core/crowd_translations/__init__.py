from sqlalchemy.orm.exc import NoResultFound

from zeeguu_core.model import User, Language, UserWord, Text, Bookmark
from deprecated import deprecated

@deprecated(reason="there are now individual own_translation and crowdsourced_translations functions")
def own_or_crowdsourced_translation(user, word: str, from_lang_code: str, to_lang_code: str, context: str):

    own_past_translation = get_own_past_translation(user, word, from_lang_code, to_lang_code, context)

    if own_past_translation:
        translations = [{'translation': own_past_translation,
                         'service_name': 'Own Last Translation',
                         'quality': 100}]
        return translations

    others_past_translation = get_others_past_translation(word, from_lang_code, to_lang_code, context)
    if others_past_translation:
        translations = [{'translation': others_past_translation,
                         'service_name': 'Contributed Translation',
                         'quality': 100}]
        return translations

    return None

def own_translation(user, word: str, from_lang_code: str, to_lang_code:str, context: str):

    own_past_translation = get_own_past_translation(user, word, from_lang_code, to_lang_code, context)
    print(">>>>>>>>>> !!!!!! <<<<<<<<<<")
    print(own_past_translation)

    if own_past_translation:
        translations = [{'translation': own_past_translation,
                         'service_name': 'Own Last Translation',
                         'quality': 100}]
        return translations

    return None


def crowdsourced_translation(user, word: str, from_lang_code: str, context: str):

    others_past_translation = get_others_past_translation(word, from_lang_code, context)
    if others_past_translation:
        translations = [{'translation': others_past_translation,
                         'service_name': 'Contributed Translation',
                         'quality': 100}]
        return translations

    return None


def get_others_past_translation(word: str, from_lang_code: str, to_lang_code:str, context: str):
    return _get_past_translation(word, from_lang_code, to_lang_code, context)


def get_own_past_translation(user, word: str, from_lang_code: str, to_lang_code, context: str):
    return _get_past_translation(word, from_lang_code, to_lang_code, context, user)


def _get_past_translation(word: str, from_lang_code: str, to_lang_code:str, context: str, user: User = None):
    try:

        from_language = Language.find(from_lang_code)

        to_language = Language.find(to_lang_code)

        origin_word = UserWord.find(word, from_language)

        text = Text.query.filter_by(content=context).one()

        query = Bookmark.query.join(UserWord, UserWord.id==Bookmark.translation_id).\
            filter(UserWord.language_id==to_language.id,
                   Bookmark.origin_id==origin_word.id,
                   Bookmark.origin_id==origin_word.id,
                   Bookmark.text_id==text.id)

        if user:
            query = query.filter(Bookmark.user_id==user.id)

        # prioritize older users
        query.order_by(Bookmark.user_id.asc())

        return query.first().translation.word

    except Exception as e:
        return None
