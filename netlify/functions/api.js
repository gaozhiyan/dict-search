const cheerio = require('cheerio');

async function getWordInfo(word) {
    const w = word.trim().toLowerCase();
    const url = `https://dictionary.cambridge.org/dictionary/english-chinese-simplified/${encodeURIComponent(w)}`;
    
    try {
        const response = await fetch(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const html = await response.text();
        const $ = cheerio.load(html);
        
        const ukAudio = $('.uk.dpron-i source[type="audio/mpeg"]').attr('src');
        const usAudio = $('.us.dpron-i source[type="audio/mpeg"]').attr('src');
        
        const ukAudioUrl = ukAudio ? `https://dictionary.cambridge.org${ukAudio}` : null;
        const usAudioUrl = usAudio ? `https://dictionary.cambridge.org${usAudio}` : null;
        
        let phonetic = $('.uk.dpron-i .ipa.dipa').first().text().trim() || $('.us.dpron-i .ipa.dipa').first().text().trim();
        
        let pos = $('.pos.dpos').first().text().trim();
        if (pos === 'adjective') pos = 'adj.';
        else if (pos === 'noun') pos = 'n.';
        else if (pos === 'verb') pos = 'v.';
        else if (pos === 'adverb') pos = 'adv.';
        else if (pos === 'pronoun') pos = 'pron.';
        else if (pos === 'preposition') pos = 'prep.';
        else if (pos === 'conjunction') pos = 'conj.';
        else if (pos === 'interjection') pos = 'int.';
        
        let translation = "";
        let enDefinition = "";
        let examples = [];
        
        const senseBlocks = $('.sense-body.dsense_b');
        if (senseBlocks.length > 0) {
            const firstSense = senseBlocks.first();
            const defElem = firstSense.find('.def.ddef_d.db').first().text().trim();
            if (defElem) {
                enDefinition = defElem.endsWith(':') ? defElem.slice(0, -1).trim() : defElem;
            }
            
            translation = firstSense.find('.trans.dtrans.dtrans-se').first().text().trim();
            
            const exampBlocks = $('.examp.dexamp');
            exampBlocks.each((i, el) => {
                if (examples.length >= 3) return false;
                const enEg = $(el).find('.eg.deg').text().trim();
                const zhEg = $(el).find('.trans.dtrans').text().trim();
                if (enEg) {
                    const isSentence = enEg[0] === enEg[0].toUpperCase() || enEg.match(/[.!?]$/);
                    if (isSentence) {
                        examples.push({ en: enEg, zh: zhEg });
                    }
                }
            });
        } else {
            const defElem = $('.def.ddef_d.db').first().text().trim();
            if (defElem) {
                enDefinition = defElem.endsWith(':') ? defElem.slice(0, -1).trim() : defElem;
            }
            translation = $('.trans.dtrans.dtrans-se').first().text().trim();
            
            const exampBlocks = $('.examp.dexamp');
            exampBlocks.each((i, el) => {
                if (examples.length >= 3) return false;
                const enEg = $(el).find('.eg.deg').text().trim();
                const zhEg = $(el).find('.trans.dtrans').text().trim();
                if (enEg) {
                    const isSentence = enEg[0] === enEg[0].toUpperCase() || enEg.match(/[.!?]$/);
                    if (isSentence) {
                        examples.push({ en: enEg, zh: zhEg });
                    }
                }
            });
        }
        
        return {
            word: w,
            uk_audio: ukAudioUrl,
            us_audio: usAudioUrl,
            phonetic: phonetic,
            pos: pos,
            definition: enDefinition,
            translation: translation,
            examples: examples
        };
    } catch (e) {
        console.error(`Error fetching ${w}: ${e.message}`);
        return {
            word: w,
            error: e.message
        };
    }
}

exports.handler = async function(event, context) {
    const path = event.path;
    const httpMethod = event.httpMethod;

    if (httpMethod === 'GET' && (path.endsWith('/test') || path.endsWith('/api/test'))) {
        return {
            statusCode: 200,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: "Hello from JS FastAPI Alternative!" })
        };
    }

    if (httpMethod === 'POST' && (path.endsWith('/upload') || path.endsWith('/api/upload'))) {
        try {
            const body = JSON.parse(event.body);
            const text = body.text || '';
            
            // Extract words (simple splitting by whitespace)
            const words = text.match(/\b[a-zA-Z-]+\b/g) || [];
            
            const seen = new Set();
            const uniqueWords = [];
            for (const w of words) {
                const wLower = w.toLowerCase();
                if (!seen.has(wLower)) {
                    seen.add(wLower);
                    uniqueWords.push(wLower);
                }
            }
            
            const results = [];
            for (const word of uniqueWords) {
                const info = await getWordInfo(word);
                results.push(info);
            }
            
            return {
                statusCode: 200,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ results })
            };
        } catch (error) {
            return {
                statusCode: 400,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ error: error.message })
            };
        }
    }

    return {
        statusCode: 404,
        body: JSON.stringify({ message: "Not found", path })
    };
};