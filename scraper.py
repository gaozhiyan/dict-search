import requests
from bs4 import BeautifulSoup

def get_word_info(word):
    word = word.strip().lower()
    url = f"https://dictionary.cambridge.org/dictionary/english-chinese-simplified/{word}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Audio
        uk_audio = soup.select_one('.uk.dpron-i source[type="audio/mpeg"]')
        us_audio = soup.select_one('.us.dpron-i source[type="audio/mpeg"]')
        
        uk_audio_url = f"https://dictionary.cambridge.org{uk_audio['src']}" if uk_audio else None
        us_audio_url = f"https://dictionary.cambridge.org{us_audio['src']}" if us_audio else None
        
        # Phonetic
        phonetic_elem = soup.select_one('.uk.dpron-i .ipa.dipa')
        if not phonetic_elem:
            phonetic_elem = soup.select_one('.us.dpron-i .ipa.dipa')
        phonetic = phonetic_elem.text.strip() if phonetic_elem else ""
        
        # Part of Speech
        pos_elem = soup.select_one('.pos.dpos')
        pos = pos_elem.text.strip() if pos_elem else ""
        # shorten common POS:
        if pos == "adjective": pos = "adj."
        elif pos == "noun": pos = "n."
        elif pos == "verb": pos = "v."
        elif pos == "adverb": pos = "adv."
        elif pos == "pronoun": pos = "pron."
        elif pos == "preposition": pos = "prep."
        elif pos == "conjunction": pos = "conj."
        elif pos == "interjection": pos = "int."
        
        # Sense blocks
        sense_blocks = soup.select('.sense-body.dsense_b')
        translation = ""
        en_definition = ""
        examples = []
        
        if sense_blocks:
            first_sense = sense_blocks[0]
            # Try to get pos from the parent block if possible
            # Definition
            def_elem = first_sense.select_one('.def.ddef_d.db')
            if def_elem:
                en_definition = def_elem.text.strip()
                if en_definition.endswith(':'):
                    en_definition = en_definition[:-1].strip()
            
            # Translation
            trans_elem = first_sense.select_one('.trans.dtrans.dtrans-se')
            if trans_elem:
                translation = trans_elem.text.strip()
                
            # Examples
            examp_blocks = soup.select('.examp.dexamp')
            for ex in examp_blocks:
                if len(examples) >= 3:
                    break
                en_eg = ex.select_one('.eg.deg')
                zh_eg = ex.select_one('.trans.dtrans')
                if en_eg:
                    en_text = en_eg.text.strip()
                    zh_text = zh_eg.text.strip() if zh_eg else ""
                    # Check if it looks like a sentence
                    is_sentence = en_text and (en_text[0].isupper() or en_text.endswith(('.', '!', '?')))
                    if is_sentence:
                        examples.append({"en": en_text, "zh": zh_text})
        else:
            # Fallback
            def_elem = soup.select_one('.def.ddef_d.db')
            if def_elem:
                en_definition = def_elem.text.strip()
                if en_definition.endswith(':'):
                    en_definition = en_definition[:-1].strip()
                    
            trans_elem = soup.select_one('.trans.dtrans.dtrans-se')
            if trans_elem:
                translation = trans_elem.text.strip()
            
            examp_blocks = soup.select('.examp.dexamp')
            for ex in examp_blocks:
                if len(examples) >= 3:
                    break
                en_eg = ex.select_one('.eg.deg')
                zh_eg = ex.select_one('.trans.dtrans')
                if en_eg:
                    en_text = en_eg.text.strip()
                    zh_text = zh_eg.text.strip() if zh_eg else ""
                    is_sentence = en_text and (en_text[0].isupper() or en_text.endswith(('.', '!', '?')))
                    if is_sentence:
                        examples.append({"en": en_text, "zh": zh_text})
                    
        return {
            "word": word,
            "uk_audio": uk_audio_url,
            "us_audio": us_audio_url,
            "phonetic": phonetic,
            "pos": pos,
            "definition": en_definition,
            "translation": translation,
            "examples": examples
        }
    except Exception as e:
        print(f"Error fetching {word}: {e}")
        return {
            "word": word,
            "error": str(e)
        }

if __name__ == "__main__":
    import json
    print(json.dumps(get_word_info("crisp"), indent=2, ensure_ascii=False))
