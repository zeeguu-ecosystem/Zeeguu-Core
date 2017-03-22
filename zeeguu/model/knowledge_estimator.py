from zeeguu.model.bookmark import Bookmark
from zeeguu.model.language import Language
from zeeguu.model.learner_stats.word_encounter_stats import EncounterStats


class SimpleKnowledgeEstimator(object):
    """
    Computes statistics about this user.
    """

    def __init__(self, user, lang_code=None):
        self.user = user
        if lang_code:
            self.lang_code = lang_code
        else:
            self.lang_code = self.user.learned_language_id
        self.language = Language.find(self.lang_code)

    def get_known_bookmarks(self):
        """
        All the bookmarks that the user knows *and* are in the estimator language
        :param user:
        :param lang:
        :return:
        """
        bookmarks = self.user.all_bookmarks()
        known_bookmarks = []
        for bookmark in bookmarks:
            if bookmark.check_is_latest_outcome_too_easy() and self.language == bookmark.origin.language:
                known_bookmark_dict = {
                    'id': bookmark.id,
                    'origin': bookmark.origin.word,
                    'text': bookmark.text.content,
                    'time': bookmark.time.strftime('%m/%d/%Y')}
                known_bookmarks.append(known_bookmark_dict)
        return known_bookmarks

    def get_known_words(self):
        return [each['origin'] for each in self.get_known_bookmarks()]

    def get_known_bookmarks_count(self):
        return len(self.get_known_bookmarks())

    def get_not_encountered_words(self):
        not_encountered_words = []
        return not_encountered_words

    def get_not_encountered_words_count(self):
        return len(self.get_not_encountered_words())

    def get_not_looked_up_words(self):
        enc_probs = EncounterStats.find_all(self.user, self.lang_code)
        words = [prob.word_form.word for prob in enc_probs
                 if prob.probability > 0.7]
        return words

    def get_not_looked_up_words_count(self):
        return len(self.get_not_looked_up_words_for_learned_language())

    def words_being_learned(self):
        """
            The words the user is currently learning
        :return:
        """
        words_learning = []
        bookmarks = Bookmark.find_by_specific_user(self.user)
        for bookmark in bookmarks:
            learning = not bookmark.check_is_latest_outcome_too_easy()
            user_word = bookmark.origin
            if learning and user_word.language == self.language:
                words_learning.append(user_word.word)
        return words_learning


# def update_probabilities_for_word(word):
#     try:
#         bookmarks_for_this_word = Bookmark.find_all_by_user_and_word(flask.g.user, word)
#
#         ex_prob = ExerciseBasedProbability.find_or_create(flask.g.user, word)
#         total_prob = 0
#         for b in bookmarks_for_this_word:
#             ex_prob.calculate_known_bookmark_probability(b)
#             total_prob += float(ex_prob.probability)
#         ex_prob.probability = total_prob / len(bookmarks_for_this_word)
#         print "!ex_prob: " + str(ex_prob.probability)
#
#         if RankedWord.exists(word.word, word.language):
#             ranked_word = RankedWord.find(word.word, word.language)
#             if EncounterBasedProbability.exists(flask.g.user, ranked_word):
#                 enc_prob = EncounterBasedProbability.find(flask.g.user, ranked_word)
#                 known_word_prob = KnownWordProbability.find(flask.g.user, word, ranked_word)
#                 print "!known word prob before: " + str(known_word_prob.probability)
#                 print "!enc_prob: " + str(enc_prob.probability)
#                 known_word_prob.probability = KnownWordProbability.calculate_known_word_prob(ex_prob.probability,
#                                                                                              enc_prob.probability)
#                 print "!known word prob after: " + str(known_word_prob.probability)
#             else:
#                 known_word_prob = KnownWordProbability.find(flask.g.user, word, ranked_word)
#                 known_word_prob.probability = ex_prob.probability
#
#         db.session.commit()
#     except:
#         print "failed to update probabilities for word with id: " + str(word.id)
#
#     print "!successfully updated probabilities for word with id {0}".format(word.id)
