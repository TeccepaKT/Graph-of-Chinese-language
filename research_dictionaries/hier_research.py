from word_similarity import WordSimilarity2010
#from most_similar...

from loggers import ResearchLogger as Logger
from work_with_bases.bases import base_dicts
from hieroglyph_frequency_lists.hier_dictionaries import \
    subtlex_hier_freq_list, bcc_hier_freq_list


similarity = WordSimilarity2010().similarity


def get_relations(hier: str, hiers: list[str]) -> list[str, float]:
    """ Получение ближайших по смыслу иероглифов к данному """
    sim: list[list[str, float]] = []
    minsim: float = 0.8  # Наименьшая связь для вхождения
    tosim: float = 0.1  # Нормализация значения: будет входить в пределы [tosim, 1]
    
    for h in hiers:
        if hier == h:
            continue
        
        s = similarity(hier, h)
        if s < minsim:
            continue
        
        sim.append([h, 1 - (1 - s) / (1 - minsim) * (1 - tosim)])
    
    sim.sort(key=lambda t: t[1], reverse=True)
    return [[h, round(s * 10, 3)] for h, s in sim]


def run():
    pool: int = 3000
    hiers: list[str] = subtlex_hier_freq_list[:pool]
    
    for i, hier in enumerate(hiers):
        relations = get_relations(hier, hiers)
        text = '{\n    "related_words": ' + repr(relations).replace("'", '"') + '\n}'
        base_dicts.form_and_write(hier, text, rewrite=True)
        
        Logger.log(f'[_] Ended {hier} (№{i + 1}), go forward')
        if i == 50:
            break

