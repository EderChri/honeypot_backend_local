from happytransformer import HappyGeneration, GENSettings

gen_settings = GENSettings(
    min_length=20,
    max_length=50,
    do_sample=True,
    top_k=10,
    # top_p=0.92,
    temperature=0.8,
    #    early_stopping=True,
    #    num_beams=2,
    #    no_repeat_ngram_size=0,
    bad_words=["BITCH", "FUCK", "BITCH,", "fuck", "sucker"]
)


def gen_text(prompt: str, model_path=None):
    gen = HappyGeneration() if model_path is None else HappyGeneration(model_path)
    prompt = "You are a model that assumes the role of the first responder. Here is the conversation so far:" + "\n" + prompt
    # Word limit
    if len(prompt.split()) > 1000:
        word_list = prompt.replace("\n", "<br> ").split(" ")
        prompt = " ".join(word_list[-1000:]).replace("<br>", "\n")

    res = gen.generate_text(prompt, args=gen_settings)
    return res.text
