import spacy
from spellchecker import SpellChecker

nlp = spacy.load("ru_core_news_lg")
msg = """Upd: DHL отменил оплаченную отправку доков во вне рф. Говорят, работает только Яндекс.Доставка, а у DHL теперь с этим проблемы. Вдруг кто решит воспользоваться их «сервисом»"""

def grab_ents(doc_text, ent_label):
    doc_text = nlp(doc_text)
    ents = []
    for entity in doc_text.ents:
        if entity.label_ == ent_label:
            ents.append(entity.text)
    return ents

def msgs_filtering(msgs, filter_word, ent_label):
    filtering_msgs = []
    if len(filter_word) > 0:
        # print(filter_word)
        filter_doc = nlp(filter_word)
        # print(filter_doc.vector_norm, 'filter')
        for msg_text in msgs:
            for word in msg_text.split():
                word_doc = nlp(word)
                # print(word_doc.vector_norm, 'msg')
                # print(word, type(word), filter_doc.similarity(word_doc))
                if filter_doc.similarity(word_doc) > 0.4:
                    filtering_msgs.append(nlp(msg_text))
                    break
    else:
        filtering_msgs = msgs
    information = []
    for doc_obj in filtering_msgs:
        ents = []
        info = []
        for entity in doc_obj.ents:
            if entity.label_ == ent_label:
                ents.append(entity.text)
        info = [ents, doc_obj.text]
        information.append(info)
    return information