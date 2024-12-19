import spacy

nlp = spacy.load("ru_core_news_md")
msg = """Upd: DHL отменил оплаченную отправку доков во вне рф. Говорят, работает только Яндекс.Доставка, а у DHL теперь с этим проблемы. Вдруг кто решит воспользоваться их «сервисом»"""
doc = nlp(msg)
for ent in doc.ents:
    print(ent.label_, ent.text)
def grab_ents(doc_text, ent_label):
    doc_text = nlp(doc_text)
    ents = []
    for entity in doc_text.ents:
        if entity.label_ == ent_label:
            ents.append(entity.text)
    return ents
def msgs_filtering(msgs, filter_word, ent_label):
    filtering_msgs = []
    if len(filter_word)>0:
        print(filter_word)
        filter_doc = nlp(filter_word)
        for msg_text in msgs:
            msg_doc = nlp(msg_text)
            print(msg_text, type(msg_text))
            if filter_doc.similarity(msg_doc) > 0.6:
                filtering_msgs.append(msg_doc)
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