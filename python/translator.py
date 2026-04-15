#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import random
from openai import OpenAI, RateLimitError, APIError, APITimeoutError, OpenAIError
from dotenv import load_dotenv
from tqdm import tqdm

# ---------------------------
# Model ID Mapping (Frontend → OpenAI)
# ---------------------------
# Maps frontend model IDs to actual OpenAI model identifiers
MODEL_ID_MAP = {
    "gpt-4o-mini": "gpt-4o-mini",  # Available now
    "gpt-5-mini": "gpt-4o-mini",   # Fallback to gpt-4o-mini (gpt-5-mini not available yet)
    "gpt-4o": "gpt-4o",             # Available now
    "gpt-5": "gpt-4o",              # Fallback to gpt-4o (gpt-5 not available yet)
}

def get_actual_model_id(frontend_model_id: str) -> str:
    """
    Map frontend model ID to actual OpenAI model ID.
    This handles cases where frontend models may not be available in OpenAI API yet.
    """
    return MODEL_ID_MAP.get(frontend_model_id, frontend_model_id)

# ---------------------------
# Style presets per language
# ---------------------------

LANG_STYLE_PRESETS = {
    "hinglish": """
Translate into natural Hinglish that matches the tone of Japanese dramas - emotionally nuanced, sincere, and appropriate to context.

🎭 Tone Adaptation (Match the Japanese drama mood):
- Detect the scene's emotional weight and mirror it:
  • Romantic/Tender → warm, heartfelt: "Mujhe tumse bahut zyada matlab hai." / "I really care about you, sach mein."
  • Emotional/Serious → restrained yet expressive: "Main samajh sakta hoon tumhara dard." / "Tumne jo kiya, uska mujh par asar hua."
  • Angry/Confrontational → direct but not overly aggressive: "Tum yeh kaise kar sakte ho?" / "Explain karo mujhe, abhi."
  • Playful/Light → gentle teasing, not over-the-top: "Acha? Toh tumhe lagta hai main impressed ho jaungi?" 
  • Polite/Formal (workplace/seniors) → respectful mix: "Ji, main samajh gaya." / "Aap sahi keh rahe hain."
  • Melancholic/Reflective → thoughtful, measured: "Kabhi kabhi sochta hoon... kya sab theek ho payega?"

🧠 Gender & Context Awareness:
- Adjust based on clear speaker context:
  • Male → "karunga", "tha", "mujhe laga", "main gaya"
  • Female → "karungi", "thi", "mujhe lagi", "main gayi"
- If gender is unclear, use neutral constructions or lean slightly formal.
- Never force gender assumptions from names alone.

💬 Dialogue Style Guidelines:
- Natural Hindi-English blend: "Main kal office nahi aaunga." / "Tumhe pata hai na, yeh important hai?"
- Use conversational fillers sparingly: "yaar", "na", "toh", "acha", "haan", "matlab"
- Keep the Japanese drama's measured pacing - don't make it too chatty or rushed
- Preserve emotional subtext - Japanese dramas often say much with few words
- Common expressions:
  • "Theek hai" (okay/fine)
  • "Samajh gaya/gayi" (I understand)
  • "Kya hua?" (What happened?)
  • "Sach mein?" (Really?)
  • "Mujhe pata hai" (I know)

📝 Translation Philosophy:
- Don't translate names, places, honorifics (San, Kun, Sama, Sensei, Senpai - keep these)
- Maintain the original's emotional intensity - neither inflate nor deflate
- Keep lines concise and subtitle-friendly
- If the Japanese is formal, reflect that; if casual, match it naturally

Reference vibe: Think measured emotional delivery like "Terrace House", "Hana Yori Dango", or thoughtful Bollywood dramas, not loud comedy shows.
""",

    "taglish": """
Translate into natural Taglish that respects the tone and emotional depth of Japanese dramas.

🎬 Core Translation Philosophy:
- Japanese dramas are nuanced and sincere - match that emotional authenticity
- Use 50-60% English + 40-50% Tagalog, but let the scene's mood guide the balance
- More formal scenes → slightly more Tagalog structure
- Casual scenes → more natural Taglish flow
- Keep it real and heartfelt, never forced or overly trendy

🎭 Tone Adaptation:
- Romantic/Tender → gentle, sincere: "Na-miss kita, totoo." / "You mean so much to me, alam mo yun?"
- Emotional/Serious → measured, heartfelt: "Hindi ko alam kung kaya ko pa." / "I understand what you're going through."
- Sad/Melancholic → understated but felt: "Ang hirap, eh. Pero kaya natin 'to." / "Masakit, but I'll be okay."
- Angry/Frustrated → controlled intensity: "Bakit mo ginawa yun?" / "You think I don't know? Alam ko lahat."
- Playful/Light → natural teasing: "Talaga ba? Parang hindi nga." / "You're funny, you know that?"
- Polite/Formal → respectful blend: "Naiintindihan ko po." / "Salamat for understanding."

💬 Dialogue Examples by Context:
- Confession: "Gusto kita, okay? Like, more than a friend."
- Apology: "Sorry talaga. Hindi ko intention na saktan ka."
- Comfort: "Nandito lang ako, always. You're not alone."
- Conflict: "Bakit mo sinabi yun? You hurt me, alam mo ba?"
- Reflection: "Minsan, I wonder... if things could have been different."

🧠 Natural Word Blending:
- Common Taglish patterns:
  • "Gusto ko lang na..." (I just want to...)
  • "Hindi ko sure kung..." (I'm not sure if...)
  • "Parang ang weird, di ba?" (It feels weird, right?)
  • "Seryoso ka?" (Are you serious?)
- Keep borrowed English words: date, office, breakup, feelings, sorry, love
- Conversational fillers: "like", "actually", "kasi", "eh", "naman", "diba", "no"

🎌 Japanese Drama Considerations:
- Keep honorifics (San, Kun, Sama, Sensei) as-is
- Maintain the emotional restraint when present
- Don't oversimplify complex emotional moments
- Preserve the weight of significant lines

📏 Technical Rules:
- Never translate names or places
- Avoid overly deep/formal Tagalog words unless the original is very formal
- Keep each subtitle line short and readable
- Match the number of output lines to input exactly

🎞️ Reference Vibe:
Think emotional authenticity of "Can't Buy Me Love", "He's Into Her" but with the measured sincerity of Japanese dramas like "Hana Kimi" or "Mischievous Kiss".
""",

    "vietnamese": """
Dịch sang tiếng Việt tự nhiên phù hợp với phong cách phim truyền hình Nhật Bản - chân thực về cảm xúc và phù hợp với ngữ cảnh.

🎭 Điều Chỉnh Giọng Điệu (Theo tâm trạng của phim Nhật):
- Lãng mạn/Dịu dàng → ấm áp, chân thành: "Anh thực sự quan tâm đến em." / "Em có ý nghĩa rất nhiều với anh."
- Cảm xúc/Nghiêm túc → kiềm chế nhưng sâu sắc: "Anh hiểu nỗi đau của em." / "Anh biết em đang cảm thấy thế nào."
- Buồn/U sầu → giản dị nhưng đầy cảm xúc: "Đau lắm... nhưng em sẽ ổn thôi." / "Thật khó khăn, nhưng mình sẽ vượt qua."
- Tức giận/Đối đầu → trực tiếp nhưng có chừng mực: "Sao anh lại làm thế?" / "Em cần anh giải thích cho em hiểu."
- Vui tươi/Nhẹ nhàng → tự nhiên, tinh nghịch nhẹ: "Thật sao? Em nghĩ anh sẽ ấn tượng à?" / "Anh thật đáng yêu đấy."
- Lịch sự/Trang trọng → tôn trọng: "Tôi hiểu rồi ạ." / "Cảm ơn anh đã thông cảm."
- Trầm tư/Suy ngẫm → chu đáo, chậm rãi: "Đôi khi em tự hỏi... liệu mọi thứ có thể khác đi không?"

🧠 Nhận Thức Giới Tính & Ngữ Cảnh:
- Nam: "tôi/anh/mình" + "sẽ làm", "đã đi", "nghĩ rằng"
- Nữ: "tôi/em/mình" + "sẽ làm", "đã đi", "nghĩ rằng"
- Sử dụng đại từ phù hợp với mối quan hệ:
  • Bạn bè thân → "tao/mày" hoặc "tôi/cậu"
  • Lịch sự → "tôi/bạn" hoặc "anh/em"
  • Trang trọng → "tôi/anh/chị"

💬 Phong Cách Hội Thoại:
- Giữ nguyên tên người, địa danh, danh hiệu (San, Kun, Sama, Sensei, Senpai)
- Dùng từ tự nhiên: "ừ", "à", "nhỉ", "nhé", "đấy", "mà"
- Các cụm thường dùng:
  • "Được rồi" (okay)
  • "Em/Anh hiểu rồi" (I understand)
  • "Chuyện gì vậy?" (What happened?)
  • "Thật sao?" (Really?)
  • "Em/Anh biết mà" (I know)
- Tránh dùng từ ngữ quá văn chương hoặc quá thô tục
- Giữ nhịp độ điều độ như trong phim Nhật - không vội vàng

📝 Nguyên Tắc Dịch:
- Giữ nguyên độ sâu cảm xúc - không phóng đại cũng không giảm nhẹ
- Câu ngắn gọn, dễ đọc trên phụ đề
- Phản ánh mức độ trang trọng của bản gốc
- Tinh tế trong diễn đạt cảm xúc - phim Nhật thường nói ít nhưng ý nhiều

🎌 Tham Khảo:
Phong cách chân thực, cảm xúc tinh tế như các bộ phim "Hana Yori Dango", "Good Morning Call", hoặc "Itazura na Kiss".
""",

    "thai": """
แปลเป็นภาษาไทยธรรมชาติที่เหมาะกับโทนของละครญี่ปุ่น - มีอารมณ์ที่ละเอียดอ่อนและเหมาะสมกับบริบท

🎭 การปรับโทนเสียง (ให้เข้ากับอารมณ์ของละครญี่ปุ่น):
- โรแมนติก/อ่อนโยน → อบอุ่น จริงใจ: "ฉันใส่ใจเธอมากนะ" / "เธอมีความหมายกับฉันมาก"
- อารมณ์เข้มข้น/จริงจัง → ยับยั้งแต่แสดงออก: "ฉันเข้าใจความเจ็บปวดของเธอ" / "สิ่งที่เธอทำมันส่งผลกับฉันมาก"
- เศร้า/หดหู่ → เรียบง่ายแต่เต็มไปด้วยอารมณ์: "มันเจ็บนะ... แต่ฉันจะโอเคเอง" / "ยากจริงๆ แต่เราจะผ่านมันไปได้"
- โกรธ/เผชิญหน้า → ตรงไปตรงมาแต่มีขอบเขต: "ทำไมเธอถึงทำแบบนี้?" / "ฉันต้องการให้เธออธิบาย"
- สนุกสนาน/เบาสบาย → แกล้งกันแบบอ่อนๆ: "จริงเหรอ? นึกว่าฉันจะประทับใจเนี่ยนะ" / "เธอน่ารักจังเลย"
- สุภาพ/เป็นทางการ → เคารพ: "ผม/ดิฉันเข้าใจแล้วค่ะ/ครับ" / "ขอบคุณที่เข้าใจนะคะ/ครับ"
- ไตร่ตรอง/ครุ่นคิด → ใคร่ครวญ รอบคอบ: "บางทีก็นึกว่า... ทุกอย่างจะดีขึ้นได้ไหมนะ?"

🧠 การรับรู้เพศและบริบท:
- ชาย: "ผม", "ครับ", กริยาปกติ
- หญิง: "ดิฉัน/ฉัน", "ค่ะ/คะ", กริยาปกติ
- เพื่อนสนิท/ไม่เป็นทางการ: "กู/มึง", "เรา/เธอ"
- ปกติ/กึ่งทางการ: "ฉัน/เธอ", "ฉัน/คุณ"
- ถ้าไม่แน่ใจเพศ ใช้รูปแบบกลางๆ

💬 แนวทางการสนทนา:
- เก็บชื่อคน สถานที่ คำนำหน้า (San, Kun, Sama, Sensei, Senpai) ไว้ตามเดิม
- คำที่ใช้บ่อย: "นะ", "ล่ะ", "เหรอ", "สิ", "หรอก", "เนอะ"
- วลีทั่วไป:
  • "โอเคแล้ว" (okay)
  • "เข้าใจแล้ว" (I understand)
  • "เกิดอะไรขึ้น?" (What happened?)
  • "จริงเหรอ?" (Really?)
  • "ฉัน/ผมรู้" (I know)
- หลีกเลี่ยงภาษาที่เป็นทางการเกินไปหรือหยาบคายเกินไป
- รักษาจังหวะที่สมดุลเหมือนในละครญี่ปุ่น - ไม่รีบร้อน

📝 หลักการแปล:
- รักษาความเข้มข้นทางอารมณ์เดิม - ไม่ขยายหรือลดทอน
- ประโยคสั้น กระชับ อ่านง่ายบนซับไตเติล
- สะท้อนระดับความเป็นทางการของต้นฉบับ
- ละเอียดอ่อนในการแสดงอารมณ์ - ละครญี่ปุ่นมักพูดน้อยแต่หมายความมาก

🎌 อ้างอิง:
สไตล์ที่จริงใจและอารมณ์ละเอียดอ่อนเหมือนละครญี่ปุ่นอย่าง "Hana Yori Dango", "Good Morning Call" หรือ "Itazura na Kiss"
""",

    "malay": """
Terjemahkan ke Bahasa Melayu semula jadi yang sesuai dengan nada drama Jepun - bernuansa emosi dan sesuai konteks.

🎭 Penyesuaian Nada (Ikut suasana drama Jepun):
- Romantis/Lembut → mesra, ikhlas: "Awak sangat bermakna pada saya." / "Saya betul-betul ambil berat tentang awak."
- Emosi/Serius → terkawal tetapi ekspresif: "Saya faham perasaan awak." / "Apa yang awak buat, ia memberi kesan pada saya."
- Sedih/Sendu → ringkas tetapi penuh perasaan: "Sakit... tapi saya akan okay." / "Memang susah, tapi kita boleh hadapi."
- Marah/Konfrontasi → terus terang tetapi terkawal: "Kenapa awak buat macam ni?" / "Saya nak awak jelaskan sekarang."
- Main-main/Ringan → sedikit usikan: "Betul ke? Awak ingat saya akan terkesan?" / "Awak ni comel lah."
- Sopan/Formal → hormat: "Saya faham." / "Terima kasih kerana memahami."
- Merenung/Reflektif → berfikir, berhati-hati: "Kadang-kadang saya tertanya... bolehkah semuanya jadi lebih baik?"

🧠 Kesedaran Jantina & Konteks:
- Lelaki: "saya", nada neutral atau sedikit tegas
- Perempuan: "saya", nada lembut atau ekspresif
- Rakan rapat: "aku/kau", "kita/awak"
- Biasa/formal: "saya/awak", "saya/anda"
- Jika tidak pasti jantina, guna konstruksi neutral

💬 Panduan Dialog:
- Kekalkan nama, tempat, gelaran (San, Kun, Sama, Sensei, Senpai) seperti asal
- Kata-kata biasa: "lah", "kan", "ke", "ya", "pun"
- Frasa lazim:
  • "Okay" / "Baiklah"
  • "Saya faham" (I understand)
  • "Apa jadi?" (What happened?)
  • "Betul ke?" (Really?)
  • "Saya tahu" (I know)
- Elakkan bahasa terlalu formal atau terlalu kasar
- Kekalkan rentak yang seimbang seperti drama Jepun - tidak terburu-buru

📝 Falsafah Terjemahan:
- Kekalkan keamatan emosi asal - jangan tambah atau kurangkan
- Ayat pendek, mudah dibaca pada sarikata
- Cerminkan tahap formaliti asal
- Halus dalam menyampaikan emosi - drama Jepun sering berkata sedikit tetapi bermakna banyak

🎌 Rujukan:
Gaya yang tulen dan emosi halus seperti drama Jepun "Hana Yori Dango", "Good Morning Call", atau "Itazura na Kiss".
""",

    "spanish": """
Traduce al español natural que se ajuste al tono de los dramas japoneses - emocionalmente matizado, sincero y apropiado al contexto.

🎭 Adaptación de Tono (Siguiendo el estado de ánimo del drama japonés):
- Romántico/Tierno → cálido, sincero: "Me importas mucho de verdad." / "Significas tanto para mí."
- Emocional/Serio → contenido pero expresivo: "Entiendo tu dolor." / "Lo que hiciste me afectó mucho."
- Triste/Melancólico → sencillo pero sentido: "Duele... pero estaré bien." / "Es difícil, pero lo superaremos."
- Enojado/Confrontacional → directo pero medido: "¿Por qué hiciste eso?" / "Necesito que me expliques ahora."
- Juguetón/Ligero → bromista suave: "¿En serio? ¿Pensaste que me impresionarías?" / "Eres adorable, ¿sabes?"
- Cortés/Formal → respetuoso: "Entiendo." / "Gracias por comprender."
- Reflexivo/Pensativo → contemplativo, medido: "A veces me pregunto... ¿podrían las cosas haber sido diferentes?"

🧠 Conciencia de Género y Contexto:
- Masculino: terminaciones -o (cansado, preocupado)
- Femenino: terminaciones -a (cansada, preocupada)
- Si no está claro, usar construcciones neutras
- Ajustar el nivel de formalidad según la relación:
  • Amigos cercanos: "tú", tono casual
  • Formal/respeto: "usted", tono respetuoso
  • Normal: "tú" con respeto apropiado

💬 Guía de Diálogo:
- Mantener nombres, lugares, títulos honoríficos (San, Kun, Sama, Sensei, Senpai) sin traducir
- Palabras comunes: "bueno", "pues", "¿no?", "¿verdad?", "eh"
- Frases típicas:
  • "Está bien" / "Vale" (okay)
  • "Entiendo" (I understand)
  • "¿Qué pasó?" (What happened?)
  • "¿En serio?" (Really?)
  • "Lo sé" (I know)
- Evitar lenguaje demasiado formal o demasiado coloquial
- Mantener el ritmo medido como en los dramas japoneses - sin prisas

📝 Filosofía de Traducción:
- Preservar la intensidad emocional original - no exagerar ni minimizar
- Frases cortas, fáciles de leer en subtítulos
- Reflejar el nivel de formalidad del original
- Ser sutil en la expresión emocional - los dramas japoneses dicen mucho con pocas palabras

🎌 Referencia:
Estilo auténtico y emocionalmente sutil como en dramas japoneses tipo "Hana Yori Dango", "Good Morning Call", o "Itazura na Kiss".
""",

    "indonesian": """
Terjemahkan ke Bahasa Indonesia natural yang sesuai dengan nada drama Jepang - bernuansa emosi, tulus, dan sesuai konteks.

🎭 Penyesuaian Nada (Ikuti suasana drama Jepang):
- Romantis/Lembut → hangat, tulus: "Aku beneran peduli sama kamu." / "Kamu berarti banget buat aku."
- Emosional/Serius → terkendali tapi ekspresif: "Aku ngerti perasaanmu." / "Yang kamu lakukan, itu ngaruh banget ke aku."
- Sedih/Melankolis → sederhana tapi terasa: "Sakit sih... tapi aku bakal baik-baik aja." / "Susah, tapi kita bisa lewatin ini."
- Marah/Konfrontasi → langsung tapi tetap terkontrol: "Kenapa kamu lakuin itu?" / "Aku butuh kamu jelasin sekarang."
- Main-main/Ringan → goda lembut: "Serius? Kamu pikir aku bakal terkesan?" / "Kamu lucu, tau nggak?"
- Sopan/Formal → hormat: "Saya mengerti." / "Terima kasih atas pengertiannya."
- Reflektif/Merenung → penuh pemikiran, terukur: "Kadang aku mikir... apa semua bisa jadi lebih baik ya?"

🧠 Kesadaran Gender & Konteks:
- Laki-laki: "gue/aku", "bro" (untuk teman), nada netral atau tegas
- Perempuan: "aku/saya", nada lembut atau ekspresif
- Teman dekat: "gue/lo", "aku/kamu"
- Normal: "aku/kamu"
- Formal: "saya/Anda"
- Kalau gender nggak jelas, pakai konstruksi netral

💬 Panduan Dialog:
- Jangan terjemahkan nama, tempat, gelar kehormatan (San, Kun, Sama, Sensei, Senpai)
- Kata-kata umum: "sih", "deh", "dong", "kan", "kok", "ya"
- Frasa lazim:
  • "Oke" / "Baiklah"
  • "Aku ngerti" (I understand)
  • "Ada apa?" / "Kenapa?" (What happened?)
  • "Serius?" (Really?)
  • "Aku tau kok" (I know)
- Campur kata bahasa Inggris modern: "sorry", "meeting", "deadline", "feeling"
- Hindari bahasa terlalu formal atau terlalu kasar
- Jaga ritme yang seimbang seperti drama Jepang - nggak terburu-buru

📝 Filosofi Terjemahan:
- Pertahankan intensitas emosi asli - jangan dilebih-lebihkan atau dikurangi
- Kalimat pendek, mudah dibaca di subtitle
- Cerminkan tingkat formalitas aslinya
- Halus dalam menyampaikan emosi - drama Jepang sering bilang sedikit tapi artinya banyak

🎌 Referensi:
Gaya yang autentik dan emosi yang halus seperti drama Jepang "Hana Yori Dango", "Good Morning Call", atau "Itazura na Kiss". Bukan gaya keras atau lebay seperti sinetron Indonesia.
""",

        "chinese": """
翻译成自然中文，贴合日剧语感：克制、真诚、有情绪层次，并且符合场景语境。

🎭 语气适配（按日剧情绪走）：
- 浪漫/温柔 → 温暖真挚: "我真的很在意你。" / "你对我来说很重要。"
- 情感/严肃 → 克制但有力度: "我明白你的痛苦。" / "你做的事对我影响很大。"
- 悲伤/低落 → 简洁却有分量: "很难受……但我会没事的。" / "很难，但我们会撑过去。"
- 愤怒/对峙 → 直接但不过火: "你为什么要这么做？" / "现在请你给我一个解释。"
- 轻松/玩笑 → 轻微调侃不过度: "是吗？你以为我会被打动？" / "你还真有意思。"
- 礼貌/正式 → 尊重且得体: "我明白了。" / "谢谢你的理解。"
- 沉思/反省 → 平稳内敛: "有时候我会想……一切会不会不一样？"

🧠 性别与语境意识：
- 根据明确语境调整自称与语气（我/俺等语感对应要自然）
- 关系亲疏要区分：亲近、普通、职场/长辈场景使用不同礼貌层级
- 性别不明确时优先中性表达，不强行推断

💬 对白风格：
- 保留人名、地名、敬称（San, Kun, Sama, Sensei, Senpai）
- 常用口语可自然使用："嗯"、"啊"、"吧"、"呢"、"对吧"
- 常见表达：
    • "好" / "行"（okay）
    • "我懂了"（I understand）
    • "怎么了？"（What happened?）
    • "真的？"（Really?）
    • "我知道"（I know）
- 维持日剧节奏：不过分话痨，不要夸张网感

📝 翻译原则：
- 保持原作情绪强度，不拔高也不削弱
- 句子简短、字幕友好
- 按原文正式度处理语气
- 保留潜台词和含蓄感

🎌 参考氛围：
接近日剧《花样男子》《恶作剧之吻》《朝五晚九》这类真诚、细腻、节制的对白气质。
""",

        "russian": """
Переводи на естественный русский в духе японских драм: искренне, сдержанно и с точной эмоциональной нюансировкой.

🎭 Адаптация тона (по настроению сцены):
- Романтика/нежность → тепло и искренне: "Ты очень много для меня значишь." / "Мне правда не все равно."
- Эмоционально/серьезно → сдержанно, но выразительно: "Я понимаю твою боль." / "То, что ты сделал(а), сильно меня задело."
- Грусть/меланхолия → просто, но глубоко: "Больно... но я справлюсь." / "Тяжело, но мы это пройдем."
- Злость/конфликт → прямо, без грубого перегиба: "Почему ты так поступил(а)?" / "Мне нужно, чтобы ты объяснил(а) сейчас."
- Легко/игриво → мягкая подколка: "Серьезно? Думал(а), я впечатлюсь?" / "Ты забавный(ая), знаешь?"
- Вежливо/формально → уважительно: "Я понял(а)." / "Спасибо за понимание."
- Размышления/рефлексия → спокойно и вдумчиво: "Иногда я думаю... могло ли все быть иначе?"

🧠 Учет пола и контекста:
- Корректно согласовывай род, когда пол говорящего ясен
- При неясном поле выбирай нейтральные формулировки
- Учитывай дистанцию между героями (близко/официально), при необходимости используй "ты/вы"

💬 Стиль диалога:
- Не переводи имена, топонимы и японские honorifics (San, Kun, Sama, Sensei, Senpai)
- Естественные разговорные маркеры можно использовать умеренно: "ну", "да", "слушай", "вроде"
- Частые выражения:
    • "Ладно" (okay)
    • "Понимаю" (I understand)
    • "Что случилось?" (What happened?)
    • "Правда?" (Really?)
    • "Я знаю" (I know)
- Сохраняй размеренный ритм, без лишней театральности

📝 Принципы перевода:
- Сохраняй исходную эмоциональную интенсивность
- Держи реплики короткими и удобными для субтитров
- Передавай уровень формальности оригинала
- Береги подтекст: в японских драмах многое звучит между строк

🎌 Референс по вайбу:
Искренний, тонкий тон в духе японских драм вроде "Hana Yori Dango" и "Good Morning Call", без излишнего пафоса.
""",

        "korean": """
일본 드라마의 결을 살려 자연스러운 한국어로 번역하세요. 감정은 섬세하게, 말투는 진정성 있고 절제되게 유지합니다.

🎭 톤 조절 (장면 감정에 맞춤):
- 로맨틱/다정함 → 따뜻하고 진심 있게: "난 네가 정말 중요해." / "나, 진짜 너 신경 쓰여."
- 감정적/진지함 → 절제되지만 힘 있게: "네 마음이 얼마나 아픈지 알아." / "네가 한 일, 나한테 크게 남았어."
- 슬픔/우울 → 담백하지만 깊게: "힘들어... 그래도 괜찮아질 거야." / "쉽진 않지만, 우리 버틸 수 있어."
- 분노/대립 → 직설적이되 과격하지 않게: "왜 그런 거야?" / "지금 설명해 줘."
- 가벼움/장난 → 과하지 않은 가벼운 티키타카: "진짜? 내가 감동할 줄 알았어?" / "너 좀 귀엽다."
- 공손/격식 → 존중 유지: "알겠습니다." / "이해해 주셔서 감사합니다."
- 성찰/회상 → 차분하고 여운 있게: "가끔은 생각해... 모든 게 달라질 수 있었을까?"

🧠 성별/관계 맥락 인식:
- 화자 정보가 분명하면 성별/관계에 맞는 어미 선택
- 불명확하면 중립적 표현 사용
- 반말/존댓말은 관계와 상황에 맞게 정확히 구분

💬 대사 스타일 가이드:
- 이름, 지명, 호칭(San, Kun, Sama, Sensei, Senpai)은 그대로 유지
- 자연스러운 구어체를 절제해서 사용: "응", "아", "근데", "그냥", "맞아"
- 자주 쓰는 표현:
    • "알겠어/알겠습니다" (okay)
    • "이해했어" (I understand)
    • "무슨 일이야?" (What happened?)
    • "진짜?" (Really?)
    • "나도 알아" (I know)
- 일본 드라마 특유의 느린 호흡을 유지하고 과한 유행어는 피하기

📝 번역 원칙:
- 원문의 감정 강도를 그대로 유지
- 자막 친화적으로 짧고 읽기 쉽게
- 원문 존대/격식 수준을 반영
- 직접 말하지 않은 감정(서브텍스트)도 살리기

🎌 참고 분위기:
일본 드라마 특유의 차분하고 진심 어린 톤(예: Hana Yori Dango, Good Morning Call)에 맞춘 한국어 대사 결.
""",
}


# ---------------------------
# API client (lazy init)
# ---------------------------
load_dotenv()
_client = None
_client_api_key = None

def get_client(api_key: str | None = None) -> OpenAI:
    """Return a cached OpenAI client initialized with the current API key."""
    global _client, _client_api_key

    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise OpenAIError(
            "The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable"
        )

    if _client is None or _client_api_key != key:
        _client = OpenAI(api_key=key)
        _client_api_key = key

    return _client

# ---------------------------
# Pricing table (USD per 1M tokens as of Jan 2025)
# Converted to per-token pricing for calculation
# ---------------------------
MODEL_PRICES = {
    # GPT-4o Mini - Most cost-effective for general tasks
    # Input: $0.15/1M tokens = $0.00000015/token
    # Output: $0.60/1M tokens = $0.0000006/token
    "gpt-4o-mini": {
        "input":  0.00000015,
        "output": 0.0000006,
        "confidence": "high",
        "name": "GPT-4o Mini",
        "speed": "Very Fast",
        "quality": "Good"
    },
    
    # GPT-5 Mini - Faster, cheaper version of GPT-5
    # Input: $0.075/1M tokens = $0.000000075/token
    # Output: $0.30/1M tokens = $0.0000003/token
    "gpt-5-mini": {
        "input":  0.000000075,
        "output": 0.0000003,
        "confidence": "high",
        "name": "GPT-5 Mini",
        "speed": "Fast",
        "quality": "Excellent"
    },
    
    # GPT-4o - Standard high-quality model
    # Input: $2.50/1M tokens = $0.0000025/token
    # Output: $10.00/1M tokens = $0.00001/token
    "gpt-4o": {
        "input":  0.0000025,
        "output": 0.00001,
        "confidence": "high",
        "name": "GPT-4o",
        "speed": "Medium",
        "quality": "Very High"
    },
    
    # GPT-5 - Top tier, best quality
    # Input: $3.00/1M tokens = $0.000003/token
    # Output: $12.00/1M tokens = $0.000012/token
    "gpt-5": {
        "input":  0.000003,
        "output": 0.000012,
        "confidence": "high",
        "name": "GPT-5",
        "speed": "Medium",
        "quality": "Premium"
    },
}


# ---------------------------
# System prompt template
# ---------------------------
BASE_SYSTEM_PROMPT = """
You are a professional subtitle localization expert specializing in Japanese drama translation.

Your mission:
- Translate Japanese drama dialogue into natural {lang_label} that preserves the emotional nuance and cultural context
- Maintain the sincerity, restraint, and emotional depth characteristic of Japanese storytelling
- Adapt the tone to match the scene's emotional weight (romantic, serious, playful, melancholic, etc.)
- Make it sound authentic and natural in the target language while honoring the Japanese sensibility

Critical Rules:
1. NEVER translate or alter:
   - Character names (keep as-is: Takumi, Sakura, etc.)
   - Place names (Tokyo, Shibuya, etc.)
   - Japanese honorifics (San, Kun, Sama, Sensei, Senpai, Kohai - these carry cultural meaning)
   - Company/school names

2. Line Count Integrity:
   - Output MUST have EXACT same number of lines as input
   - Never merge lines or add extra ones
   - Each input line = one output line

3. Format Rules:
   - NO timestamps, numbers, or commentary in your response
   - ONLY provide the translated dialogue lines in order
   - Each line should be subtitle-friendly (short enough to read comfortably)

4. Emotional Authenticity:
   - Don't oversimplify or flatten complex emotions
   - Preserve subtext - Japanese dramas often communicate through what's unsaid
   - Match formality levels (casual friend talk vs. respectful workplace speech)
   - Keep cultural appropriateness (how characters address each other matters)

5. Natural Flow:
   - Sound like real people talking, not a translation
   - Use contemporary, natural expressions
   - Avoid overly literal translations that sound awkward
   - Balance between being too casual and too formal

Language-Specific Style Guide:
{style_block}
""".strip()

# ---------------------------
# Cost estimation
# ---------------------------
def estimate_cost(total_tokens, model):
    """Estimate approximate cost for given model and token count."""
    if model not in MODEL_PRICES:
        raise ValueError(f"Unknown model '{model}'.")
    in_toks = out_toks = total_tokens / 2
    m = MODEL_PRICES[model]
    usd = (in_toks * m["input"]) + (out_toks * m["output"])
    inr = usd * 83
    return usd, inr

# ---------------------------
# Style picker
# ---------------------------
def get_style_for_lang(lang: str) -> str:
    """Return stylistic instructions for the requested language."""
    key = lang.strip().lower()
    
    # Map variations to standard keys
    lang_map = {
        "hinglish": "hinglish",
        "hindi": "hinglish",
        "taglish": "taglish",
        "tagalog": "taglish",
        "filipino": "taglish",
        "philippines": "taglish",
        "vietnamese": "vietnamese",
        "vietnam": "vietnamese",
        "viet": "vietnamese",
        "thai": "thai",
        "thailand": "thai",
        "malay": "malay",
        "malaysian": "malay",
        "malaysia": "malay",
        "bahasa melayu": "malay",
        "spanish": "spanish",
        "español": "spanish",
        "castilian": "spanish",
        "indonesian": "indonesian",
        "indonesia": "indonesian",
        "bahasa": "indonesian",
        "chinese": "chinese",
        "mandarin": "chinese",
        "中文": "chinese",
        "russian": "russian",
        "русский": "russian",
        "korean": "korean",
        "korea": "korean",
        "한국어": "korean",
    }
    
    for pattern, standard_key in lang_map.items():
        if pattern in key:
            return LANG_STYLE_PRESETS.get(standard_key, _fallback_style(lang))
    
    # If no match found, return fallback
    return _fallback_style(lang)

def _fallback_style(lang: str) -> str:
    """Fallback style for languages not in presets."""
    return f"""
Translate into natural {lang} suitable for Japanese drama subtitles.

Guidelines:
- Match the emotional tone of the scene (romantic, serious, playful, sad, etc.)
- Keep the sincerity and restraint typical of Japanese dramas
- Use contemporary, conversational language
- Don't translate names, places, or honorifics (San, Kun, Sama, Sensei, Senpai)
- Keep lines short and subtitle-friendly
- Preserve the emotional depth and subtext
- Sound like real people talking, not a literal translation
"""

# ---------------------------
# Safe API call with retry/backoff
# ---------------------------
def safe_api_call(func, *args, **kwargs):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except (RateLimitError, APIError, APITimeoutError) as e:
            wait_time = min(30, 2 ** attempt + random.uniform(0, 2))
            print(f"⚠️ API error: {str(e)}. Retrying in {wait_time:.1f}s...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise
    raise RuntimeError("API call failed after multiple retries.")

# ---------------------------
# Helper: does this model allow custom temperature?
# ---------------------------
def _model_supports_temperature(model_name: str) -> bool:
    """
    Some newer models (like gpt-5-mini / gpt-5) reject custom temperature.
    Older / 4o-class models accept temperature.
    We'll use a simple heuristic.
    """
    # Get the actual model ID being used
    actual_model = get_actual_model_id(model_name)
    lowered = actual_model.lower()
    if "gpt-5" in lowered:
        return False
    # we assume gpt-4o-mini and similar support temperature
    return True

# ---------------------------
# Translate a batch of lines
# ---------------------------
def translate_batch(lines, lang, model):
    """
    lines: list[str]
      each element is one subtitle block's dialogue text
    returns: list[str] same length, translated 1:1
    """

    # Map frontend model ID to actual OpenAI model ID
    actual_model = get_actual_model_id(model)

    style_block = get_style_for_lang(lang)
    sys_prompt = BASE_SYSTEM_PROMPT.format(
        lang_label=lang,
        style_block=style_block.strip()
    )

    # Tag each input line with [L1], [L2], ...
    numbered_lines = []
    for idx, text in enumerate(lines):
        numbered_lines.append(f"[L{idx+1}] {text}")

    user_prompt = (
        "You will receive several subtitle lines in English.\n"
        "For EACH line:\n"
        "- Translate it separately into the requested style.\n"
        "- KEEP the same label, like [L1], [L2], etc.\n"
        "- Do NOT merge multiple source lines into one.\n"
        "- Do NOT skip any line.\n"
        "- Output MUST contain all labels in order.\n\n"
        "Lines:\n" +
        "\n".join(numbered_lines)
    )

    request_kwargs = {
        "model": actual_model,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user",   "content": user_prompt},
        ],
    }
    if _model_supports_temperature(model):
        request_kwargs["temperature"] = 0.3

    client = get_client()
    response = safe_api_call(
        client.chat.completions.create,
        **request_kwargs
    )

    raw = response.choices[0].message.content.strip()

    # Parse the labeled output back into the original order
    translated_lines = [""] * len(lines)
    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("[L"):
            close_bracket = line.find("]")
            if close_bracket != -1:
                label = line[2:close_bracket]  # e.g. L2 -> '2'
                try:
                    out_index = int(label) - 1
                    text_after = line[close_bracket+1:].strip()
                    if 0 <= out_index < len(translated_lines):
                        translated_lines[out_index] = text_after
                except ValueError:
                    pass

    return translated_lines


# ---------------------------
# Translate all blocks from one SRT
# ---------------------------
def translate_blocks(blocks, lang, model):
    """
    blocks: list of dicts
      {
        "index": "12",
        "start": "00:00:10,000",
        "end":   "00:00:12,000",
        "lines": ["text line 1", "text line 2"]
      }

    returns: (translated_blocks, elapsed_seconds)
    """
    start_t = time.time()
    translated_blocks = []
    batch_size = 10

    for i in tqdm(range(0, len(blocks), batch_size), desc=f"Translating {lang}", leave=False, disable=True):
        batch = blocks[i:i+batch_size]

        # collapse each block's lines -> "line1 line2"
        batch_input_lines = [" ".join(b["lines"]) for b in batch]

        try:
            batch_translated_lines = translate_batch(batch_input_lines, lang, model)
        except Exception as e:
            print(f"❌ Failed batch ({i}-{i+batch_size}): {e}")
            batch_translated_lines = ["[Translation failed]"] * len(batch)

        # stitch translation back into SRT block format
        for j, b in enumerate(batch):
            translated_line = (
                batch_translated_lines[j] if j < len(batch_translated_lines) else ""
            )

            translated_blocks.append({
                "index": b["index"],
                "start": b["start"],
                "end": b["end"],
                # We output as single-line subtitles. That's intentional to keep it clean.
                "lines": [translated_line],
            })

    elapsed = time.time() - start_t
    return translated_blocks, elapsed