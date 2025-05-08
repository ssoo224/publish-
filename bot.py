import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions, ReactionTypeEmoji
from datetime import datetime, timedelta, date
import threading
import time
import random
import requests
import os
import asyncio
import shutil
from yt_dlp import YoutubeDL

# Bot settings
TOKEN = "7117925617:AAEvrbPnqplZsPwc5lTNLAPTGXPLWiV4ZPg"
bot = telebot.TeleBot(TOKEN)
DEVELOPER_ID = 7115002714


# --- User data ---
user_balances = {}  # {user_id: int}
clubs_owned = {}  # {user_id: {"type": "عربي" or "أجنبي", "join_date": datetime, "ball": "كرة القدم" or "كرة السلة"}}
warnings = {}  # {chat_id: {user_id: warning_count}}
mutes = {}  # {chat_id: {user_id: mute_until_datetime}}
user_gifts = {}  # {user_id: last_gift_date}
user_animals = {}  # {user_id: {animal_name: price}}
user_foods = {}  # {user_id: {food_name: price}}
user_vehicles = {}  # {user_id: {vehicle_name: price}}
ball_status = {}  # {user_id: {"has_ball": bool, "last_action": datetime, "ball_type": "كرة القدم" or "كرة السلة", "start_time": datetime, "stars_earned": int, "result": str, "duration": int}}
ongoing_trainings = {}  # {user_id: {"end_time": datetime, "last_training_date": date}}
last_feed_time = {}  # {user_id: {animal_name: datetime}}
welcome_messages = {}  # {chat_id: {"type": "text" or "photo" or "voice", "content": str or file_id, "caption": str or None}}
waiting_welcome = {}  # {user_id: {"chat_id": int, "message_id": int}}
waiting_admin_action = {}  # {user_id: {"chat_id": int, "action": "promote" or "demote"}}
waiting_gift = {}  # {user_id: {"chat_id": int, "message_id": int, "target_id": int}}
words_waiting = {}  # {user_id: {"word": str, "message_id": int, "chat_id": int, "sent_time": datetime}}
waiting_media = {}  # {user_id: {"chat_id": int, "platform": str, "message_id": int}}
user_messages = {}  # {chat_id: {user_id: message_count}}

# --- Darlen replies ---
darlen_replies = ["هاااع", "تفضل يئلبي 😘", "مشغولة وية صاحبي", "عيوني", "متزوجة ترة 💍", "؟!"]
darlen_reply_index = {}

# --- Bad word reactions ---
badword_reactions = ["🗿", "🌚", "🌝", "😐", "😡", "🤯"]
badword_index = {}

# --- Morning messages ---
morning_messages = [
    "جدعان، فينكم؟ طنشتوني ولا إيه؟ أخباركم؟ 🗿",
    "إيه يا رجالة، نمتوا ولا ايه؟ فاكرين العيش والملح ولا نسيتوا؟ عاملين ايه؟ 🌞",
    "يا أصحاب، اختفيتوا فين؟ مش لاقي حد؟ الدنيا عاملة ايه؟ 🌎",
    "معلمين، مفيش حس؟ كله تمام ولا ايه؟🙈"
]
morning_message_index = 0
last_morning_message_date = None

# --- Inactive user replies ---
inactive_user_replies = [
    "يا جدعان، فينكوا؟ زهقت! ما تيجوا نروق الدنيا ونجيب كام نجمة نهيص بيهم ⭐️",
    "إيه يا رجالة؟ نمتوا ولا إيه؟ يلا بينا نولعها ونجيب نجوم السماء 💫",
    "يا أهالينا، الطفش دبحني! مش هتيجوا نلم نجوم ونقلب الدنيا فرح؟ 🌚",
    "يلا بينا على السوق نجيب حيوانات تهبل! بس لازم نلم نجوم الأول عشان الفلوس تكفي ✨",
    "نفسي في قرد نطاط... بس استنى! لازم نشتغل ونجيب نجوم الأول عشان خاطر عيون القرد 🐵",
    "يا ترى هنشتري ببغاء ولا قطة؟ المهم نجمع نجوم كتير الأول عشان نختار براحتنا 🌹",
    "يا عمري، كل ده تأخير؟ قلبي هيقف! يلا بقى، مستنياك عشان نلعب وننور الدنيا 🔥",
    "يا حبيبي، روحت فين؟ وحشتني! تعالى بسرعة نلم نجوم وننسى الزعل 🌺",
    "يا نور عيني، بطّلت أشوف من غيرك! يلا تعالى نجمع نجوم ونرجع نضحك تاني 😂"
]
inactive_reply_index = 0
last_inactive_reply_date = None
replied_users = set()

# --- Private chat replies ---
private_chat_replies = [
    "اخذوني وياكم 😔",
    "شسوون هناك 😈",
    "راح يتحرش بالخاص"
]
private_reply_index = 0

# --- Arabic words for word game ---
arabic_words = [
    "كتاب", "مدرسة", "شجرة", "بحر", "سماء", "قمر", "شمس", "نجم", "وردة", "طائر",
    "سيارة", "منزل", "حديقة", "نهر", "جبل", "غابة", "مدينة", "قرية", "طريق", "جسر"
]

# --- Store ---
store_foods = {
    "الحلويات": 50,
    "الفواكه": 40,
    "الألبان": 30,
    "الأسماك": 70,
    "خضروات": 20,
    "الأرز": 25,
    "بطاطس": 15,
    "مكسرات": 60
}

store_animals = {
    "خنزير": 500, "الخنزير": 500,
    "تلقطة": 600, "التلقطة": 600,
    "دلفين": 800, "الدلفين": 800,
    "سلحفات": 400, "السلحفات": 400,
    "كلب": 300, "الكلب": 300,
    "معز": 350, "المعز": 350,
    "بقرة": 700, "البقرة": 700,
    "غزالة": 650, "الغزالة": 650,
    "ضفدع": 150, "الضفدع": 150,
    "أسد": 900, "الأسد": 900,
    "نمر": 850, "النمر": 850,
    "فيل": 1000, "الفيل": 1000,
    "زرافة": 950, "الزرافة": 950,
    "قرد": 550, "القرد": 550,
    "حصان": 750, "الحصان": 750,
    "أرنب": 200, "الأرنب": 200,
    "ببغاء": 250, "الببغاء": 250
}

store_vehicles = {
    "سيارة": 37,
    "دراجة نارية": 59,
    "طائرة": 100,
    "حافلة": 79,
    "صاروخ": 83
}

# --- Commands that can be deleted by admins or owner ---
ALLOWED_DELETE_COMMANDS = [
    "رصيدي", "المتجر", "متجر", "الكلمات", "كلمات", "حيواناتي", "الأوامر", "اوامر",
    "كرة", "الكرة", "تمرير", "هدف", "تسجيل", "تمرين", "فيس", "فيسبوك",
    "يوت", "انستا", "إنستا", "انستغرام", "إنستغرام", "أنستغرام"
]

# --- وظيفة مساعدة لتثبيت المكتبات ---
def install_library(library_name):
    try:
        __import__(library_name)
        print(f"✅ مكتبة {library_name} مثبتة.")
        return True
    except ImportError:
        print(f"🔄 جاري تثبيت مكتبة {library_name}...")
        os.system(f"pip install {library_name}")
        try:
            __import__(library_name)
            print(f"✅ تم تثبيت مكتبة {library_name} بنجاح.")
            return True
        except ImportError:
            print(f"❌ فشل تثبيت مكتبة {library_name}. يرجى المحاولة مرة أخرى.")
            return False

# --- تثبيت yt-dlp ---
if not install_library("yt_dlp"):
    print("❌ يجب تثبيت yt-dlp لتحميل الصوت.")
    exit()

# --- وظيفة مساعدة للتحقق من ffmpeg ---
def check_ffmpeg():
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        print("✅ تم العثور على ffmpeg و ffprobe.")
        return True
    else:
        print("⚠️ لم يتم العثور على ffmpeg أو ffprobe.")
        print("   يرجى تثبيتهما لتحميل الصوت.")
        print("   - Linux (Debian/Ubuntu): sudo apt update && sudo apt install ffmpeg")
        print("   - Linux (Fedora/CentOS): sudo dnf install ffmpeg")
        print("   - macOS: brew install ffmpeg")
        print("   - Windows: قم بتنزيلهما من موقع ffmpeg وإضافتهما إلى PATH.")
        return False

# --- التحقق من ffmpeg ---
if not check_ffmpeg():
    exit()

# --- إعدادات التحميل ---
if not os.path.exists("downloads"):
    os.makedirs("downloads")

YDL_OPTIONS = {
    'format': 'bestaudio/best[abr<=160]',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'cookiefile': 'cookies.txt',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '128',
    }],
}

# --- Helpers ---
def is_owner(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status == 'creator'
    except:
        return False

def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except:
        return False

def promote_user(chat_id, user_id, custom_title=None):
    try:
        bot.promote_chat_member(chat_id, user_id,
                                can_change_info=True,
                                can_delete_messages=True,
                                can_invite_users=True,
                                can_restrict_members=True,
                                can_pin_messages=True,
                                can_promote_members=False,
                                can_manage_voice_chats=True)
        if custom_title:
            bot.set_chat_administrator_custom_title(chat_id, user_id, custom_title)
        return True
    except:
        return False

def demote_user(chat_id, user_id):
    try:
        bot.promote_chat_member(chat_id, user_id,
                                can_change_info=False,
                                can_delete_messages=False,
                                can_invite_users=False,
                                can_restrict_members=False,
                                can_pin_messages=False,
                                can_promote_members=False,
                                can_manage_voice_chats=False)
        return True
    except:
        return False

def mute_user_until_tomorrow_evening(chat_id, user_id):
    try:
        now = datetime.now()
        tomorrow_evening = datetime.combine(now.date() + timedelta(days=1), datetime.min.time()) + timedelta(hours=20)
        permissions = ChatPermissions(can_send_messages=False, can_send_media_messages=False,
                                      can_send_polls=False, can_send_other_messages=False,
                                      can_add_web_page_previews=False, can_change_info=False,
                                      can_invite_users=False, can_pin_messages=False)
        bot.restrict_chat_member(chat_id, user_id, permissions=permissions, until_date=tomorrow_evening)
        if chat_id not in mutes:
            mutes[chat_id] = {}
        mutes[chat_id][user_id] = tomorrow_evening
        return True
    except:
        return False

def unmute_user(chat_id, user_id):
    try:
        permissions = ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                                      can_send_polls=True, can_send_other_messages=True,
                                      can_add_web_page_previews=True, can_change_info=False,
                                      can_invite_users=True, can_pin_messages=True)
        bot.restrict_chat_member(chat_id, user_id, permissions=permissions)
        if chat_id in mutes and user_id in mutes[chat_id]:
            del mutes[chat_id][user_id]
        return True
    except:
        return False

def normalize_word(word):
    word = word.strip().lower()
    if word.endswith("ة"):
        return word[:-1] + "ه"
    elif word.endswith("ه"):
        return word[:-1] + "ة"
    else:
        return word

def get_user_id_from_username(chat_id, username):
    try:
        username = username.lstrip('@').lower()
        admins = bot.get_chat_administrators(chat_id)
        members = bot.get_chat_members(chat_id)
        for member in admins + members:
            if member.user.username and member.user.username.lower() == username:
                return member.user.id
        return None
    except:
        return None

def download_media(url, platform):
    try:
        if platform == "facebook":
            download_url = f"https://fdown.hideme.eu.org/?url={url}"
            response = requests.get(download_url, timeout=10)
            if response.status_code == 200:
                return response.text  # Adjust based on actual API response
        else:
            api_url = f"https://tele-social.vercel.app/down?url={url}"
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status"):
                    if platform == "youtube":
                        return data["data"].get("audio")
                    elif platform == "instagram":
                        return data["data"].get("video") or data["data"].get("image")
        return None
    except:
        return None

# --- Morning message and inactive user reply scheduler ---
def send_morning_and_inactive_messages():
    global morning_message_index, last_morning_message_date, inactive_reply_index, last_inactive_reply_date
    while True:
        now = datetime.now()
        today = now.date()
        # Morning messages at 8:00 AM
        if last_morning_message_date != today and now.hour == 8 and now.minute == 0:
            message = morning_messages[morning_message_index]
            for chat_id in welcome_messages.keys():
                try:
                    bot.send_message(chat_id, message)
                except:
                    pass
            morning_message_index = (morning_message_index + 1) % len(morning_messages)
            last_morning_message_date = today

        # Inactive user replies at 9:00 AM
        if last_inactive_reply_date != today and now.hour == 9 and now.minute == 0:
            for chat_id in user_messages.keys():
                for user_id, count in user_messages[chat_id].items():
                    if user_id not in replied_users and count > 0:
                        bot_commands = ["رصيدي", "المتجر", "متجر", "الكلمات", "كلمات", "حيواناتي", "الأوامر", "اوامر",
                                        "كرة", "الكرة", "تمرير", "هدف", "تسجيل", "تمرين", "فيس", "فيسبوك",
                                        "يوت", "انستا", "إنستا", "انستغرام", "إنستغرام", "أنستغرام"]
                        user_used_bot = False
                        try:
                            messages = bot.search_chat_messages(chat_id, from_user=user_id)
                            for msg in messages:
                                if msg.text and msg.text.lower() in bot_commands:
                                    user_used_bot = True
                                    break
                        except:
                            continue
                        if not user_used_bot:
                            try:
                                bot.send_message(chat_id, inactive_user_replies[inactive_reply_index])
                                replied_users.add(user_id)
                                inactive_reply_index = (inactive_reply_index + 1) % len(inactive_user_replies)
                                last_inactive_reply_date = today
                                break
                            except:
                                continue
            if last_inactive_reply_date != today:
                replied_users.clear()
        time.sleep(60)

# --- Word game timeout checker ---
def check_word_game_timeout():
    while True:
        now = datetime.now()
        for user_id, data in list(words_waiting.items()):
            if now >= data["sent_time"] + timedelta(hours=5):
                try:
                    bot.delete_message(data["chat_id"], data["message_id"])
                except:
                    pass
                words_waiting.pop(user_id, None)
        time.sleep(60)

threading.Thread(target=send_morning_and_inactive_messages, daemon=True).start()
threading.Thread(target=check_word_game_timeout, daemon=True).start()

# --- Message Handlers ---
@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["هه", "ههه", "هههه", "ههههه", "هههههه", "ههههههههههه"])
def laugh_reply(m):
    bot.reply_to(m, "خوش تسلك")

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "شوف")
def show_reply(m):
    bot.reply_to(m, "ششوف")

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "الحمدلله")
def alhamdulillah_reply(m):
    bot.reply_to(m, "دوم بيبي 🤭")

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["هلا", "اهلا"])
def hello_reply(m):
    bot.reply_to(m, "هلع")

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "سلام")
def salam_reply(m):
    bot.reply_to(m, "كمل سلام ابني")

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "نعم")
def yes_reply(m):
    bot.reply_to(m, "الله ينعم عليك")

@bot.message_handler(func=lambda m: m.text and "احبج" in m.text)
def middle_finger_reply(m):
    bot.set_message_reaction(m.chat.id, m.message_id, reaction=[ReactionTypeEmoji(emoji="🤣")])
    bot.reply_to(m, "حبتك حية ام راسين")

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "اي")
def what_reply(m):
    bot.reply_to(m, "وجعي")

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "حبيبي")
def darling_reply(m):
    bot.reply_to(m, "متحرش")

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "بوت")
def bot_reply(m):
    bot.reply_to(m, "اسمي NoNa ولك 🙄❤️")

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["خاص", "خاااص", "تعال خاص", "تع", "ابعث", "إبعث"])
def private_chat_reply(m):
    global private_reply_index
    bot.reply_to(m, private_chat_replies[private_reply_index])
    private_reply_index = (private_reply_index + 1) % len(private_chat_replies)

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "نونا")
def reply_darlen(m):
    uid = m.from_user.id
    idx = darlen_reply_index.get(uid, 0)
    bot.reply_to(m, darlen_replies[idx])
    idx = (idx + 1) % len(darlen_replies)
    darlen_reply_index[uid] = idx

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["تبا", "كس امك", "كس أمك"])
def react_badword(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    idx = badword_index.get(uid, 0)
    reaction = random.choice(badword_reactions)
    try:
        bot.set_message_reaction(chat_id, m.message_id, reaction=[ReactionTypeEmoji(emoji=reaction)])
        def delete_message():
            time.sleep(5)
            try:
                bot.delete_message(chat_id, m.message_id)
            except:
                pass
        threading.Thread(target=delete_message).start()
    except:
        pass
    idx = (idx + 1) % len(badword_reactions)
    badword_index[uid] = idx

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "ايدي")
def show_user_id(m):
    user_id = m.from_user.id
    firstname = m.from_user.first_name
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{user_id}"))
    bot.reply_to(m, f"معرفك: {user_id}", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["سيارة", "سياره"])
def vehicle_car(m):
    uid = m.from_user.id
    if "سيارة" in user_vehicles.get(uid, {}):
        bot.reply_to(m, "🚗")

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["دراجة", "دراجه", "دراجة نارية", "دراجه ناريه"])
def vehicle_motorcycle(m):
    uid = m.from_user.id
    if "دراجة نارية" in user_vehicles.get(uid, {}):
        bot.reply_to(m, "🏍️")

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["طائرة", "طائره"])
def vehicle_plane(m):
    uid = m.from_user.id
    if "طائرة" in user_vehicles.get(uid, {}):
        bot.reply_to(m, "✈️")

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["حافلة", "حافله"])
def vehicle_bus(m):
    uid = m.from_user.id
    if "حافلة" in user_vehicles.get(uid, {}):
        bot.reply_to(m, "🚎")

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "صاروخ")
def vehicle_rocket(m):
    uid = m.from_user.id
    if "صاروخ" in user_vehicles.get(uid, {}):
        bot.reply_to(m, "🚀")

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["الكرة", "كرة"])
def start_ball_game(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    ball_status[uid] = {
        "has_ball": True,
        "last_action": datetime.now(),
        "ball_type": "كرة القدم",
        "start_time": datetime.now(),
        "stars_earned": 0,
        "result": None,
        "duration": 0
    }
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}"))
    bot.reply_to(m, "دعنا نلعب معًا!", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "تمرير")
def pass_ball(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    if uid not in ball_status:
        return
    ball_status[uid]["last_action"] = datetime.now()
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}"))
    if ball_status[uid]["has_ball"]:
        ball_status[uid]["has_ball"] = False
        bot.reply_to(m, "مررت الكرة إلى رفاقك!", reply_markup=kb)
    else:
        ball_status[uid]["has_ball"] = True
        bot.reply_to(m, "مررت الكرة إليك!", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["هدف", "تسجيل"])
def score_goal(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    if uid not in ball_status or not ball_status[uid]["has_ball"]:
        return
    ball_status[uid]["last_action"] = datetime.now()
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("النتيجة", callback_data=f"show_result_{uid}"))
    bot.reply_to(m, "⚽ هدف رائع!", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text and m.text == "رصيده" and m.reply_to_message)
def show_other_balance(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    target = m.reply_to_message.from_user
    balance = user_balances.get(target.id, 0)
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("إهداء", callback_data=f"gift_start_{target.id}_{uid}"),
        InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}")
    )
    bot.reply_to(m, f"الرصيد الخاص به: {balance} نجمة", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text and m.text.startswith("إهداء ") and m.reply_to_message)
def gift_command(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    if m.reply_to_message.from_user.id == uid:
        return
    parts = m.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return
    amount = int(parts[1])
    if amount <= 0:
        return
    balance = user_balances.get(uid, 0)
    target_user = m.reply_to_message.from_user
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}"))
    if balance < amount:
        bot.reply_to(m, "ليس لديك رصيد كافٍ!", reply_markup=kb)
        return
    user_balances[uid] = balance - amount
    user_balances[target_user.id] = user_balances.get(target_user.id, 0) + amount
    bot.reply_to(m, "تم الإهداء!", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "رصيدي")
def show_my_balance(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    balance = user_balances.get(uid, 0)
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("الهدية اليومية", callback_data=f"daily_gift_{uid}"),
        InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}")
    )
    bot.reply_to(m, f"الرصيد الخاص بك: {balance} نجمة", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "مسح" and m.reply_to_message)
def delete_messages(m):
    chat_id = m.chat.id
    from_user = m.from_user
    reply_msg = m.reply_to_message
    if not (is_owner(chat_id, from_user.id) or is_admin(chat_id, from_user.id)):
        return
    try:
        bot.delete_message(chat_id, reply_msg.message_id)
        bot.delete_message(chat_id, m.message_id)
    except:
        pass

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["رفع مشرف", "ترقية", "ترقيه", "الترقية", "الترقيه"] and m.reply_to_message)
def promote_admin(m):
    chat_id = m.chat.id
    from_user = m.from_user
    target_user = m.reply_to_message.from_user
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{from_user.id}"))
    if not is_owner(chat_id, from_user.id):
        bot.reply_to(m, "هذا الأمر لمالك المجموعة فقط!", reply_markup=kb)
        return
    if is_admin(chat_id, target_user.id):
        bot.reply_to(m, "هذا المستخدم مشرف بالفعل!", reply_markup=kb)
        return
    if promote_user(chat_id, target_user.id):
        bot.reply_to(m, "تم رفعه كمشرف!", reply_markup=kb)
    else:
        bot.reply_to(m, "فشل في رفع العضو!", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["عزل مشرف", "ازالة الاشراف", "إزالة الإشراف"] and m.reply_to_message)
def demote_admin(m):
    chat_id = m.chat.id
    from_user = m.from_user
    target_user = m.reply_to_message.from_user
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{from_user.id}"))
    if not is_owner(chat_id, from_user.id):
        bot.reply_to(m, "لا يمكنك استخدام ذلك الأمر.", reply_markup=kb)
        return
    if not is_admin(chat_id, target_user.id):
        bot.reply_to(m, "هذا المستخدم ليس مشرفًا!", reply_markup=kb)
        return
    if demote_user(chat_id, target_user.id):
        bot.reply_to(m, "تم عزل الإشراف!", reply_markup=kb)
    else:
        bot.reply_to(m, "فشل في عزل الإشراف!", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["طرد", "بنعال"] and m.reply_to_message)
def kick_user(m):
    chat_id = m.chat.id
    from_user = m.from_user
    target_user = m.reply_to_message.from_user
    bot_id = bot.get_me().id
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{from_user.id}"))

    if not (is_owner(chat_id, from_user.id) or is_admin(chat_id, from_user.id)):
        bot.reply_to(m, "هذا الأمر للمشرفين أو المالك فقط!", reply_markup=kb)
        return

    if target_user.id == bot_id:
        bot.reply_to(m, "عذرًا، لا يمكنني طرد نفسي!", reply_markup=kb)
        return

    if is_owner(chat_id, target_user.id):
        bot.reply_to(m, "عذرًا، لا يمكنني طرد المالك!", reply_markup=kb)
        return

    try:
        bot.kick_chat_member(chat_id, target_user.id)
        bot.reply_to(m, f"تم طرد {target_user.first_name} من المجموعة بنجاح!", reply_markup=kb)
    except:
        bot.reply_to(m, "فشل في طرد العضو!", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["إلغاء الحظر", "الغاء الحظر"] and m.reply_to_message)
def unban_user(m):
    chat_id = m.chat.id
    from_user = m.from_user
    target_user = m.reply_to_message.from_user
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{from_user.id}"))

    if not (is_owner(chat_id, from_user.id) or is_admin(chat_id, from_user.id)):
        bot.reply_to(m, "هذا الأمر للمشرفين أو المالك فقط!", reply_markup=kb)
        return

    try:
        bot.unban_chat_member(chat_id, target_user.id)
        bot.reply_to(m, "رجعت الحرية! يمكنه الإنضمام مرة أخرى من خلال رابط الدعوة.", reply_markup=kb)
    except:
        bot.reply_to(m, "فشل في إلغاء الحظر!", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["الأوامر", "اوامر"])
def admin_commands(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    if not is_owner(chat_id, uid):
        return
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("رسالة الترحيب", callback_data=f"welcome_msg_{uid}"),
        InlineKeyboardButton("الإحصائيات", callback_data=f"stats_{uid}"),
        InlineKeyboardButton("الأدوات", callback_data=f"tools_{uid}")
    )
    bot.reply_to(m, "أهلًا، يمكنك تخصيص المجموعة ومراجعتها.", reply_markup=kb)

@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(m):
    chat_id = m.chat.id
    if chat_id in welcome_messages:
        msg = welcome_messages[chat_id]
        if msg["type"] == "text":
            bot.send_message(chat_id, msg["content"])
        elif msg["type"] == "photo":
            bot.send_photo(chat_id, msg["content"], caption=msg["caption"])
        elif msg["type"] == "voice":
            bot.send_voice(chat_id, msg["content"], caption=msg["caption"])

@bot.message_handler(content_types=['left_chat_member'])
def handle_left_member(m):
    chat_id = m.chat.id
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{m.from_user.id}"))
    bot.reply_to(m, "توصل بالسلامة", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "حيواناتي")
def show_user_animals(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    animals = user_animals.get(uid, {})
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}"))
    if not animals:
        bot.send_message(chat_id, "لم تشترِ أي حيوانات بعد.", reply_markup=kb)
        return
    lines = []
    line = []
    count = 0
    for animal, price in animals.items():
        line.append(f"{animal} بـ {price}")
        count += 1
        if count % 3 == 0:
            lines.append(" | ".join(line))
            line = []
    if line:
        lines.append(" | ".join(line))
    text = "حيواناتك:\n" + "\n".join(lines)
    bot.send_message(chat_id, text, reply_markup=kb)

# --- Feed animal ---
FEED_COST = 25
FEED_COOLDOWN = timedelta(hours=24)

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("إطعام "))
def feed_animal(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    text = m.text.strip()
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}"))
        bot.reply_to(m, "اكتب: إطعام [اسم الحيوان]", reply_markup=kb)
        return
    animal_name = parts[1].strip()
    user_animals_set = user_animals.get(uid, {})
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}"))

    normalized_animal = animal_name
    if not animal_name.startswith("ال"):
        normalized_animal = "ال" + animal_name
    if animal_name.startswith("ال"):
        normalized_animal = animal_name[2:]

    if normalized_animal not in store_animals and animal_name not in store_animals:
        bot.reply_to(m, "تأكد من أن اسم الحيوان صحيح.", reply_markup=kb)
        return

    animal_key = animal_name if animal_name in store_animals else normalized_animal
    if animal_key not in user_animals_set:
        bot.reply_to(m, "مهلًا، أنت لا تمتلك ذلك الحيوان.", reply_markup=kb)
        return

    last_feed = last_feed_time.get(uid, {}).get(animal_key)
    if last_feed and datetime.now() < last_feed + FEED_COOLDOWN:
        bot.reply_to(m, "لا يمكنك إطعام الحيوان مرة أخرى! حاول لاحقًا.", reply_markup=kb)
        return

    balance = user_balances.get(uid, 0)
    if balance < FEED_COST:
        bot.reply_to(m, "بحاجة إلى 25 نجمة لأداء هذه العملية. تأكد أنك تمتلك الرصيد الكافي وحاول مرة أخرى.", reply_markup=kb)
        return

    user_balances[uid] = balance - FEED_COST
    last_feed_time.setdefault(uid, {})
    last_feed_time[uid][animal_key] = datetime.now()
    msg = bot.reply_to(m, f"يتم إطعام {animal_name}...", reply_markup=kb)

    def update_message():
        time.sleep(19)
        try:
            bot.edit_message_text(f"تم إطعام {animal_name}!", chat_id, msg.message_id, reply_markup=kb)
        except:
            pass

    threading.Thread(target=update_message).start()

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["المتجر", "متجر"])
def store_start(m):
    uid = m.from_user.id
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("الحيوانات", callback_data=f"store_animals_{uid}"),
        InlineKeyboardButton("الأطعمة", callback_data=f"store_foods_{uid}"),
        InlineKeyboardButton("المركبات", callback_data=f"store_vehicles_{uid}"),
        InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}")
    )
    bot.reply_to(m, "اشترِ منتجات متنوعة من المتجر!", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["كلمات", "الكلمات"])
def start_words_game(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    word = random.choice(arabic_words)
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("تخطي", callback_data=f"skip_word_{uid}"))
    sent = bot.reply_to(m, f"أعد إرسال الكلمة، وأحصل على نجوم إضافية: {word}", reply_markup=kb)
    words_waiting[uid] = {"word": normalize_word(word), "message_id": sent.message_id, "chat_id": chat_id, "sent_time": datetime.now()}

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "تمرين")
def start_training(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    if uid not in ball_status:
        return
    now = datetime.now()
    today = now.date()
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}"))
    if uid in ongoing_trainings and ongoing_trainings[uid]["last_training_date"] == today:
        bot.reply_to(m, "رفاقك متمرنون بالفعل، حاول لاحقًا!", reply_markup=kb)
        return
    if uid in ongoing_trainings and ongoing_trainings[uid]["end_time"] > now:
        bot.reply_to(m, "مهلًا، لم يتم التمرين بعد!", reply_markup=kb)
        return
    ongoing_trainings[uid] = {"end_time": now + timedelta(seconds=10), "last_training_date": today}
    bot.reply_to(m, "جاري التمرين. انتظر 10 ثوانٍ!", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text and m.from_user.id in waiting_gift and m.text.isdigit())
def process_gift_amount(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    amount = int(m.text)
    if amount <= 0:
        return
    gift_data = waiting_gift.get(uid)
    if not gift_data:
        return
    balance = user_balances.get(uid, 0)
    target_id = gift_data["target_id"]
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}"))
    if balance < amount:
        bot.reply_to(m, "لا تمتلك الرصيد الكافي!", reply_markup=kb)
        del waiting_gift[uid]
        return
    user_balances[uid] = balance - amount
    user_balances[target_id] = user_balances.get(target_id, 0) + amount
    bot.reply_to(m, "تم الإهداء!", reply_markup=kb)
    del waiting_gift[uid]

@bot.message_handler(content_types=['text', 'photo', 'voice'], func=lambda m: m.from_user.id in waiting_welcome)
def set_welcome_message(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    if uid not in waiting_welcome:
        return
    welcome_data = waiting_welcome[uid]
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}"))
    if m.text:
        welcome_messages[chat_id] = {"type": "text", "content": m.text, "caption": None}
    elif m.photo:
        welcome_messages[chat_id] = {"type": "photo", "content": m.photo[-1].file_id, "caption": m.caption}
    elif m.voice:
        welcome_messages[chat_id] = {"type": "voice", "content": m.voice.file_id, "caption": m.caption}
    bot.reply_to(m, "تم تعيين رسالة الترحيب!", reply_markup=kb)
    del waiting_welcome[uid]

@bot.message_handler(func=lambda m: m.text and m.from_user.id in waiting_admin_action)
def process_admin_action(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    if uid not in waiting_admin_action:
        return
    action_data = waiting_admin_action[uid]
    action = action_data["action"]
    username = m.text.strip()
    if not username.startswith("@"):
        username = f"@{username}"
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}"))
    
    target_user_id = get_user_id_from_username(chat_id, username)
    if not target_user_id:
        bot.reply_to(m, "مهلًا، المستخدم ليس عضوًا هنا.", reply_markup=kb)
        del waiting_admin_action[uid]
        return

    if action == "promote":
        if is_admin(chat_id, target_user_id):
            bot.reply_to(m, "مهلًا، المستخدم مشرف بالفعل.", reply_markup=kb)
        elif promote_user(chat_id, target_user_id):
            bot.reply_to(m, "تم رفعه مشرفًا!", reply_markup=kb)
        else:
            bot.reply_to(m, "فشل في رفع العضو!", reply_markup=kb)
    elif action == "demote":
        if not is_admin(chat_id, target_user_id):
            bot.reply_to(m, "هذا المستخدم ليس مشرفًا!", reply_markup=kb)
        elif demote_user(chat_id, target_user_id):
            bot.reply_to(m, "تم عزله من الإشراف!", reply_markup=kb)
        else:
            bot.reply_to(m, "فشل في عزل الإشراف!", reply_markup=kb)
    del waiting_admin_action[uid]

@bot.message_handler(func=lambda m: m.text and m.from_user.id in words_waiting)
def check_word_answer(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    user_data = words_waiting.get(uid)
    if not user_data:
        return
    input_word = m.text.strip().lower()
    expected_word = user_data["word"]
    normalized_input = normalize_word(input_word)
    kb = InlineKeyboardMarkup()
    if input_word == expected_word or normalized_input == expected_word:
        user_balances[uid] = user_balances.get(uid, 0) + 20
        kb.add(
            InlineKeyboardButton("كلمة جديدة", callback_data=f"new_word_{uid}"),
            InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}")
        )
        bot.reply_to(m, "صحيح! حصلت على 20 نجوم!", reply_markup=kb)
        try:
            bot.delete_message(chat_id, user_data["message_id"])
        except:
            pass
        del words_waiting[uid]

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["فيس", "فيسبوك"])
def request_facebook_url(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}"))
    bot_reply = bot.reply_to(m, "أرسل رابط مقطع الفيديو وسأقوم بتنزيله بسرعة..", reply_markup=kb)
    waiting_media[uid] = {"chat_id": chat_id, "platform": "facebook", "message_id": bot_reply.message_id}

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith(("فيس ", "فيس،", "فيسبوك ", "فيسبوك،")))
def download_facebook_video(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    text = m.text.strip()
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}"))
        bot.reply_to(m, "يرجى إرسال رابط الفيديو!", reply_markup=kb)
        return
    url = parts[1].strip()
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إلغاء", callback_data=f"close_msg_{uid}"))
    bot_reply = bot.reply_to(m, "جاري التحميل... انتظر لحظة", reply_markup=kb)
    
    def process_download():
        media_url = download_media(url, "facebook")
        if media_url:
            try:
                bot.edit_message_text("تم التحميل!", chat_id, bot_reply.message_id)
                bot.send_video(chat_id, media_url, reply_to_message_id=m.message_id)
            except:
                bot.edit_message_text("فشل في تحميل الفيديو!", chat_id, bot_reply.message_id, reply_markup=kb)
        else:
            bot.edit_message_text("فشل في تحميل الفيديو!", chat_id, bot_reply.message_id, reply_markup=kb)
    
    threading.Thread(target=process_download).start()

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith(("يوت ", "يوت،")))
def download_youtube_audio(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    text = m.text.strip()
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}"))
        bot.reply_to(m, "يرجى إرسال نص البحث!", reply_markup=kb)
        return
    search_query = parts[1].strip()
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}"))
    bot_reply = bot.reply_to(m, "جاري البحث عن وتحميل الصوت... 🎧", reply_markup=kb)

    async def download_and_send():
        ydl = YoutubeDL(YDL_OPTIONS)
        try:
            info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{search_query}", download=True)
            if 'entries' in info and len(info['entries']) > 0:
                info = info['entries'][0]
                file_path = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
                bot.edit_message_text("تم التحميل!", chat_id, bot_reply.message_id, reply_markup=kb)
                bot.send_audio(
                    chat_id=chat_id,
                    audio=open(file_path, 'rb'),
                    title=info.get("title"),
                    performer=info.get("uploader"),
                    reply_to_message_id=m.message_id
                )
                os.remove(file_path)
            else:
                bot.edit_message_text("🚫 لم يتم العثور على نتائج للبحث.", chat_id, bot_reply.message_id, reply_markup=kb)
        except Exception as e:
            bot.edit_message_text(f"🚫 حدث خطأ أثناء التحميل: {str(e)}", chat_id, bot_reply.message_id, reply_markup=kb)

    threading.Thread(target=lambda: asyncio.run(download_and_send()), daemon=True).start()

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith(("انستا ", "انستا،", "إنستا ", "إنستا،", "انستغرام ", "انستغرام،", "إنستغرام ", "إنستغرام،", "أنستغرام ", "أنستغرام،")))
def download_instagram_media(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    text = m.text.strip()
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{uid}"))
        bot.reply_to(m, "يرجى إرسال رابط الميديا!", reply_markup=kb)
        return
    url = parts[1].strip()
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إلغاء", callback_data=f"close_msg_{uid}"))
    bot_reply = bot.reply_to(m, "جاري التحميل... انتظر لحظة", reply_markup=kb)
    
    def process_download():
        media_url = download_media(url, "instagram")
        if media_url:
            try:
                bot.edit_message_text("تم التحميل!", chat_id, bot_reply.message_id)
                if media_url.endswith(('.jpg', '.png')):
                    bot.send_photo(chat_id, media_url, reply_to_message_id=m.message_id)
                else:
                    bot.send_video(chat_id, media_url, reply_to_message_id=m.message_id)
            except:
                bot.edit_message_text("فشل في تحميل الميديا!", chat_id, bot_reply.message_id, reply_markup=kb)
        else:
            bot.edit_message_text("فشل في تحميل الميديا!", chat_id, bot_reply.message_id, reply_markup=kb)
    
    threading.Thread(target=process_download).start()

@bot.message_handler(func=lambda m: m.text and m.from_user.id in waiting_media)
def process_media_url(m):
    uid = m.from_user.id
    chat_id = m.chat.id
    media_data = waiting_media.get(uid)
    if not media_data:
        return
    platform = media_data["platform"]
    url = m.text.strip()
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("إلغاء", callback_data=f"close_msg_{uid}"))
    bot_reply = bot.reply_to(m, "جاري التحميل... انتظر لحظة", reply_markup=kb)
    
    def process_download():
        media_url = download_media(url, platform)
        if media_url:
            try:
                bot.edit_message_text("تم التحميل!", chat_id, bot_reply.message_id)
                if platform == "facebook":
                    bot.send_video(chat_id, media_url, reply_to_message_id=m.message_id)
                elif platform == "instagram":
                    if media_url.endswith(('.jpg', '.png')):
                        bot.send_photo(chat_id, media_url, reply_to_message_id=m.message_id)
                    else:
                        bot.send_video(chat_id, media_url, reply_to_message_id=m.message_id)
                elif platform == "youtube":
                    bot.send_audio(chat_id, media_url, reply_to_message_id=m.message_id)
            except:
                bot.edit_message_text(f"فشل في تحميل {'الفيديو' if platform == 'facebook' else 'الميديا' if platform == 'instagram' else 'الصوت'}!", chat_id, bot_reply.message_id, reply_markup=kb)
        else:
            bot.edit_message_text(f"فشل في تحميل {'الفيديو' if platform == 'facebook' else 'الميديا' if platform == 'instagram' else 'الصوت'}!", chat_id, bot_reply.message_id, reply_markup=kb)
    
    threading.Thread(target=process_download).start()
    del waiting_media[uid]

# --- Message counter ---
@bot.message_handler(content_types=['text'])
def count_messages(m):
    chat_id = m.chat.id
    user_id = m.from_user.id
    user_messages.setdefault(chat_id, {})
    user_messages[chat_id][user_id] = user_messages[chat_id].get(user_id, 0) + 1

# --- Callback Query Handler ---
@bot.callback_query_handler(func=lambda c: True)
def handle_all_callbacks(c):
    chat_id = c.message.chat.id
    user_id = c.from_user.id
    data = c.data

    target_uid = None
    if "_" in data:
        parts = data.split("_")
        try:
            target_uid = int(parts[-1]) if parts[-1].isdigit() else None
        except ValueError:
            target_uid = None

    if not (is_owner(chat_id, user_id) or is_admin(chat_id, user_id) or (target_uid and user_id == target_uid)):
        bot.answer_callback_query(c.id)
        return

    if data.startswith("close_msg_"):
        try:
            bot.delete_message(chat_id, c.message.message_id)
        except:
            bot.answer_callback_query(c.id)
        return

    if data.startswith("show_result_"):
        target_uid = int(data.split("_")[2])
        if target_uid not in ball_status:
            bot.answer_callback_query(c.id)
            return
        results = ["تعادل", "تسجيل", "إخفاق"]
        result = random.choice(results)
        stars = {"تعادل": 10, "تسجيل": 25, "إخفاق": 0}[result]
        ball_status[target_uid]["stars_earned"] = stars
        ball_status[target_uid]["result"] = result
        start_time = ball_status[target_uid]["start_time"]
        duration = int((datetime.now() - start_time).total_seconds())
        ball_status[target_uid]["duration"] = duration
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("سحب", callback_data=f"claim_stars_{target_uid}"),
            InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{target_uid}")
        )
        bot.edit_message_text(
            f"النتيجة: {result}\n"
            f"مدة المباراة: {duration} ثانية\n"
            f"الربح: {stars} نجمة",
            chat_id, c.message.message_id, reply_markup=kb
        )

    elif data.startswith("claim_stars_"):
        target_uid = int(data.split("_")[2])
        if target_uid not in ball_status:
            bot.answer_callback_query(c.id)
            return
        stars = ball_status[target_uid]["stars_earned"]
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{target_uid}"))
        if stars == 0:
            bot.edit_message_text(
                "ليس لديك ما تسحبه!",
                chat_id, c.message.message_id, reply_markup=kb
            )
        else:
            user_balances[target_uid] = user_balances.get(target_uid, 0) + stars
            bot.edit_message_text(
                f"تهانينا! لقد سحبت {stars} نجمة إلى رصيدك.",
                chat_id, c.message.message_id, reply_markup=kb
            )
        del ball_status[target_uid]

    elif data.startswith("gift_start_"):
        target_id = int(data.split("_")[2])
        initiator_id = int(data.split("_")[3])
        waiting_gift[user_id] = {"chat_id": chat_id, "message_id": c.message.message_id, "target_id": target_id}
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("الرجوع", callback_data=f"gift_back_{target_id}_{user_id}"))
        bot.edit_message_text("ما هي كمية النجوم التي تريد إهداءها له؟", chat_id, c.message.message_id, reply_markup=kb)

    elif data.startswith("gift_back_"):
        target_id = int(data.split("_")[2])
        initiator_id = int(data.split("_")[3])
        balance = user_balances.get(target_id, 0)
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("إهداء", callback_data=f"gift_start_{target_id}_{user_id}"),
            InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{user_id}")
        )
        bot.edit_message_text(f"الرصيد الخاص به: {balance} نجمة", chat_id, c.message.message_id, reply_markup=kb)
        if user_id in waiting_gift:
            del waiting_gift[user_id]

    elif data.startswith("daily_gift_"):
        target_uid = int(data.split("_")[2])
        if user_id != target_uid:
            bot.answer_callback_query(c.id)
            return
        now = datetime.now().date()
        last_gift = user_gifts.get(target_uid)
        kb = InlineKeyboardMarkup()
        if last_gift == now:
            kb.add(InlineKeyboardButton("الرجوع", callback_data=f"balance_back_{target_uid}"))
            bot.edit_message_text("محاولات كثيرة! حاول مرة أخرى غدًا.", chat_id, c.message.message_id, reply_markup=kb)
            return
        user_balances[target_uid] = user_balances.get(target_uid, 0) + 25
        user_gifts[target_uid] = now
        kb.add(InlineKeyboardButton("الرجوع", callback_data=f"balance_back_{target_uid}"))
        bot.edit_message_text("تهانينا! حصلت على 25 نجمة!", chat_id, c.message.message_id, reply_markup=kb)

    elif data.startswith("balance_back_"):
        target_uid = int(data.split("_")[2])
        balance = user_balances.get(target_uid, 0)
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("الهدية اليومية", callback_data=f"daily_gift_{target_uid}"),
            InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{target_uid}")
        )
        bot.edit_message_text(f"الرصيد الخاص بك: {balance} نجمة", chat_id, c.message.message_id, reply_markup=kb)

    elif data.startswith("welcome_msg_"):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("الرجوع", callback_data=f"admin_commands_{user_id}"))
        if chat_id in welcome_messages:
            kb.add(InlineKeyboardButton("تعديل", callback_data=f"edit_welcome_{user_id}"))
        else:
            waiting_welcome[user_id] = {"chat_id": chat_id, "message_id": c.message.message_id}
            bot.edit_message_text(
                "أرسل الرسالة التي تريدني أن أرسلها عند انضمام أعضاء جدد:",
                chat_id, c.message.message_id, reply_markup=kb
            )
        if chat_id in welcome_messages:
            bot.edit_message_text(
                "تم تعيين رسالة الترحيب بالفعل.",
                chat_id, c.message.message_id, reply_markup=kb
            )

    elif data.startswith("edit_welcome_"):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("الرجوع", callback_data=f"admin_commands_{user_id}"))
        bot.edit_message_text(
            "أرسل الرسالة التي تريدني أن أرسلها عند انضمام أعضاء جدد:",
            chat_id, c.message.message_id, reply_markup=kb
        )
        waiting_welcome[user_id] = {"chat_id": chat_id, "message_id": c.message.message_id}

    elif data.startswith("admin_commands_"):
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("رسالة الترحيب", callback_data=f"welcome_msg_{user_id}"),
            InlineKeyboardButton("الإحصائيات", callback_data=f"stats_{user_id}"),
            InlineKeyboardButton("الأدوات", callback_data=f"tools_{user_id}")
        )
        bot.edit_message_text("أهلًا، يمكنك تخصيص المجموعة ومراجعتها.", chat_id, c.message.message_id, reply_markup=kb)

    elif data.startswith("tools_"):
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("المسح", callback_data=f"delete_tool_{user_id}"),
            InlineKeyboardButton("الترقية", callback_data=f"promote_tool_{user_id}"),
            InlineKeyboardButton("الطرد", callback_data=f"kick_tool_{user_id}"),
            InlineKeyboardButton("عزل مشرف", callback_data=f"demote_tool_{user_id}"),
            InlineKeyboardButton("الرجوع", callback_data=f"admin_commands_{user_id}")
        )
        bot.edit_message_text("طريقة جديدة للتعامل مع أعضائك!\nالمسح | الترقية | الطرد | عزل مشرف", chat_id, c.message.message_id, reply_markup=kb)

    elif data.startswith("delete_tool_"):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("الرجوع", callback_data=f"tools_{user_id}"))
        bot.edit_message_text("يكفي أن ترسل مسح كرد على رسالة ليتم حذفها.", chat_id, c.message.message_id, reply_markup=kb)

    elif data.startswith("promote_tool_"):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("الرجع", callback_data=f"tools_{user_id}"))
        bot.edit_message_text("يكفي أن ترسل رفع مشرف كرد على رسالة المستخدم لرفعه مشرفا.", chat_id, c.message.message_id, reply_markup=kb)

    elif data.startswith("kick_tool_"):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("الرجوع", callback_data=f"tools_{user_id}"))
        bot.edit_message_text(
            "إحظر أي شخص مخالف للقوانين بضغطة واحدة؛ عن طريق إرسال طرد كرد على رسالته.",
            chat_id, c.message.message_id, reply_markup=kb
        )

    elif data.startswith("demote_tool_"):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("الرجوع", callback_data=f"tools_{user_id}"))
        bot.edit_message_text(
            "أزل الإشراف عن أي مشرف، بالرد على رسالته بـ عزل مشرف.",
            chat_id, c.message.message_id, reply_markup=kb
        )

    elif data.startswith("stats_"):
        try:
            member_count = bot.get_chat_member_count(chat_id)
            admins = bot.get_chat_administrators(chat_id)
            admin_count = len(admins)
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("الرجوع", callback_data=f"admin_commands_{user_id}"))
            bot.edit_message_text(
                f"الأعضاء: {member_count}\n"
                f"المشرفون: {admin_count}",
                chat_id, c.message.message_id, reply_markup=kb
            )
        except:
            bot.answer_callback_query(c.id)

    elif data.startswith("store_animals_"):
        kb = InlineKeyboardMarkup(row_width=3)
        buttons = [InlineKeyboardButton(animal, callback_data=f"buy_animal_{animal}_{user_id}") for animal in store_animals.keys() if not animal.startswith("ال")]
        for i in range(0, len(buttons), 3):
            kb.add(*buttons[i:i+3])
        kb.add(InlineKeyboardButton("الرجوع", callback_data=f"store_back_{user_id}"))
        bot.edit_message_text("اشترِ حيوانات أليفة رائعة!", chat_id, c.message.message_id, reply_markup=kb)

    elif data.startswith("store_foods_"):
        kb = InlineKeyboardMarkup(row_width=3)
        buttons = [InlineKeyboardButton(food, callback_data=f"buy_food_{food}_{user_id}") for food in store_foods.keys()]
        for i in range(0, len(buttons), 3):
            kb.add(*buttons[i:i+3])
        kb.add(InlineKeyboardButton("الرجوع", callback_data=f"store_back_{user_id}"))
        bot.edit_message_text("اشترِ أطعمة لذيذة!", chat_id, c.message.message_id, reply_markup=kb)

    elif data.startswith("store_vehicles_"):
        kb = InlineKeyboardMarkup(row_width=3)
        buttons = [InlineKeyboardButton(vehicle, callback_data=f"buy_vehicle_{vehicle}_{user_id}") for vehicle in store_vehicles.keys()]
        for i in range(0, len(buttons), 3):
            kb.add(*buttons[i:i+3])
        kb.add(InlineKeyboardButton("الرجوع", callback_data=f"store_back_{user_id}"))
        bot.edit_message_text("اشترِ مركبات ممتعة!", chat_id, c.message.message_id, reply_markup=kb)

    elif data.startswith("store_back_"):
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("الحيوانات", callback_data=f"store_animals_{user_id}"),
            InlineKeyboardButton("الأطعمة", callback_data=f"store_foods_{user_id}"),
            InlineKeyboardButton("المركبات", callback_data=f"store_vehicles_{user_id}"),
            InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{user_id}")
        )
        bot.edit_message_text("اشترِ منتجات متنوعة من المتجر!", chat_id, c.message.message_id, reply_markup=kb)

    elif data.startswith("buy_animal_"):
        animal = data.split("_")[2]
        price = store_animals.get(animal)
        if not price:
            bot.answer_callback_query(c.id)
            return
        user_animals.setdefault(user_id, {})
        if animal in user_animals[user_id] or f"ال{animal}" in user_animals[user_id]:
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{user_id}"))
            bot.edit_message_text("أنت تمتلك هذا الحيوان بالفعل!", chat_id, c.message.message_id, reply_markup=kb)
            return
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("شراء", callback_data=f"confirm_buy_animal_{animal}_{user_id}"),
            InlineKeyboardButton("الرجوع", callback_data=f"store_back_{user_id}")
        )
        bot.edit_message_text(f"هل تريد شراء {animal} بـ {price} نجمة؟", chat_id, c.message.message_id, reply_markup=kb)

    elif data.startswith("buy_food_"):
        food = data.split("_")[2]
        price = store_foods.get(food)
        if not price:
            bot.answer_callback_query(c.id)
            return
        user_foods.setdefault(user_id, {})
        if food in user_foods[user_id]:
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{user_id}"))
            bot.edit_message_text("أنت تمتلك هذا الطعام بالفعل!", chat_id, c.message.message_id, reply_markup=kb)
            return
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("شراء", callback_data=f"confirm_buy_food_{food}_{user_id}"),
            InlineKeyboardButton("الرجوع", callback_data=f"store_back_{user_id}")
        )
        bot.edit_message_text(f"هل تريد شراء {food} بـ {price} نجمة؟", chat_id, c.message.message_id, reply_markup=kb)

    elif data.startswith("buy_vehicle_"):
        vehicle = data.split("_")[2]
        price = store_vehicles.get(vehicle)
        if not price:
            bot.answer_callback_query(c.id)
            return
        user_vehicles.setdefault(user_id, {})
        if vehicle in user_vehicles[user_id]:
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{user_id}"))
            bot.edit_message_text("أنت تمتلك هذه المركبة بالفعل!", chat_id, c.message.message_id, reply_markup=kb)
            return
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("شراء", callback_data=f"confirm_buy_vehicle_{vehicle}_{user_id}"),
            InlineKeyboardButton("الرجوع", callback_data=f"store_back_{user_id}")
        )
        bot.edit_message_text(f"هل تريد شراء {vehicle} بـ {price} نجمة؟", chat_id, c.message.message_id, reply_markup=kb)

    elif data.startswith("confirm_buy_animal_"):
        animal = data.split("_")[2]
        price = store_animals.get(animal)
        if not price:
            bot.answer_callback_query(c.id)
            return
        balance = user_balances.get(user_id, 0)
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{user_id}"))
        if balance < price:
            bot.edit_message_text("ليس لديك رصيد كافٍ!", chat_id, c.message.message_id, reply_markup=kb)
            return
        user_animals[user_id][animal] = price
        user_balances[user_id] = balance - price
        bot.edit_message_text(f"تهانينا! اشتريت {animal}!", chat_id, c.message.message_id, reply_markup=kb)

    elif data.startswith("confirm_buy_food_"):
        food = data.split("_")[2]
        price = store_foods.get(food)
        if not price:
            bot.answer_callback_query(c.id)
            return
        balance = user_balances.get(user_id, 0)
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{user_id}"))
        if balance < price:
            bot.edit_message_text("ليس لديك رصيد كافٍ!", chat_id, c.message.message_id, reply_markup=kb)
            return
        user_foods[user_id][food] = price
        user_balances[user_id] = balance - price
        bot.edit_message_text(f"تهانينا! اشتريت {food}!", chat_id, c.message.message_id, reply_markup=kb)

    elif data.startswith("confirm_buy_vehicle_"):
        vehicle = data.split("_")[2]
        price = store_vehicles.get(vehicle)
        if not price:
            bot.answer_callback_query(c.id)
            return
        balance = user_balances.get(user_id, 0)
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("إغلاق", callback_data=f"close_msg_{user_id}"))
        if balance < price:
            bot.edit_message_text("ليس لديك رصيد كافٍ!", chat_id, c.message.message_id, reply_markup=kb)
            return
        user_vehicles[user_id][vehicle] = price
        user_balances[user_id] = balance - price
        bot.edit_message_text(f"تهانينا! اشتريت {vehicle}!", chat_id, c.message.message_id, reply_markup=kb)

    elif data.startswith("new_word_"):
        target_uid = int(data.split("_")[2])
        if user_id != target_uid:
            bot.answer_callback_query(c.id)
            return
        word = random.choice(arabic_words)
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("تخطي", callback_data=f"skip_word_{target_uid}"))
        bot.edit_message_text(
            f"أعد إرسال الكلمة، وأحصل على نجوم إضافية: {word}",
            chat_id, c.message.message_id, reply_markup=kb
        )
        words_waiting[target_uid] = {
            "word": normalize_word(word),
            "message_id": c.message.message_id,
            "chat_id": chat_id,
            "sent_time": datetime.now()
        }

    elif data.startswith("skip_word_"):
        target_uid = int(data.split("_")[2])
        if user_id != target_uid:
            bot.answer_callback_query(c.id)
            return
        word = random.choice(arabic_words)
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("تخطي", callback_data=f"skip_word_{target_uid}"))
        bot.edit_message_text(
            f"أعد إرسال الكلمة، وأحصل على نجوم إضافية: {word}",
            chat_id, c.message.message_id, reply_markup=kb
        )
        words_waiting[target_uid] = {
            "word": normalize_word(word),
            "message_id": c.message.message_id,
            "chat_id": chat_id,
            "sent_time": datetime.now()
        }

    bot.answer_callback_query(c.id)

@bot.message_handler(func=lambda m: m.text and m.reply_to_message and m.from_user.id == DEVELOPER_ID and m.text.startswith("اضافة "))
def add_balance(m):
    try:
        amount = int(m.text.split()[1])
        target_id = m.reply_to_message.from_user.id
        user_balances[target_id] = user_balances.get(target_id, 0) + amount
        bot.reply_to(m, f"✅ تم إضافة {amount} لرصيد العضو.")
    except:
        bot.reply_to(m, "❌ تأكد من كتابة الأمر بشكل صحيح: اضافة [المبلغ]")





@bot.message_handler(func=lambda m: m.text and m.text.lower() == "تصفير توب" and m.from_user.id == DEVELOPER_ID)
def reset_top(m):
    for uid in list(user_balances.keys()):
        user_balances[uid] = 0
    bot.reply_to(m, "✅ تم تصفير جميع الأرصدة.")


import heapq
last_top_time = 0
top_list = []

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "توب")
def top_users(m):
    global last_top_time, top_list
    now = time.time()
    if now - last_top_time > 600:
        sorted_balances = heapq.nlargest(20, user_balances.items(), key=lambda x: x[1])
        top_list = []
        for uid, balance in sorted_balances:
            try:
                name = bot.get_chat(uid).first_name
            except:
                name = f"مستخدم {uid}"
            top_list.append((name, uid, balance))
        last_top_time = now

    if not top_list:
        bot.reply_to(m, "لا يوجد أي مستخدم يمتلك رصيد.")
        return

message = "🏆 قائمة أغنى 20 مستخدم:"

for i, (name, uid, balance) in enumerate(top_list, 1):
    message += f"{i}. {name} | {balance} نجمة\n"
bot.reply_to(m, message)


# --- Start the bot ---
if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
