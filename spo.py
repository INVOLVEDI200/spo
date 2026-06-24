python
import os
import re
import json
import asyncio
from datetime import datetime, timezone
from typing import List, Tuple, Optional
from urllib.parse import urlparse, parse_qs, unquote

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from telethon.tl import types

try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None


# ============================================================
# ENV HELPERS - برای Railway و اجرای لوکال
# ============================================================

def get_env_value(name: str, default=None):
    value = os.getenv(name)

    if value is None or value == "":
        return default

    return value


def get_env_int(name: str, default: int = 0) -> int:
    value = os.getenv(name)

    if value is None or value == "":
        return default

    try:
        return int(value)
    except Exception:
        return default


def get_env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None or value == "":
        return default

    return str(value).strip().lower() in ["1", "true", "yes", "y", "on"]


# ============================================================
# CONFIG - مقادیر اصلی
# ============================================================

API_ID = get_env_int("API_ID", 23150376)

# روی Railway بهتره API_HASH را داخل Variables بگذاری.
API_HASH = get_env_value("API_HASH", "554e038dcc59b1ad19f598a63686dcf8")

SESSION_NAME = get_env_value("SESSION_NAME", "my_telegram_account")

# برای Railway:
# مقدار TELEGRAM_SESSION_STRING را از generate_session.py بگیر و داخل Railway Variables بگذار.
TELEGRAM_SESSION_STRING = get_env_value("TELEGRAM_SESSION_STRING", "1BJWap1wBuwHcPNX6yKA-1nAMxO189YymXgt_8sDZjcIPgvLvMeqiDqeM2iv1HGpEwU6dV3JbSAd1jkJHD6E_G5KQE1VxzAC88PdCOK0AO4Vb5GTdwAaBS6thDDQN7zKVJdrueh1UrzhPVRVd9QVbCRGsUqGmkapzMPZrbVPwyNl7xpj8rQWNx-2TnIP2XSwkrU52rXPRda8pFnJaEQdcbK8ABZS69abTXhQU7x-cqxuePYnVC2-Bh4EfoRZJiI56Q0Pj_ax-cPsAjuTzDuSwQpUk0x3Lerg3MzNbROO_E5IsIzrX2mDCp8x53pILdrGv2UMeeFrRmDrUO-apA6ZQrnQzfC_rKVA=")

# کانال مبدا A - جایی که عکس + کپشن می‌گذارد
SOURCE_CHANNEL = get_env_value("SOURCE_CHANNEL", "@xniceshop")

# کانال مقصد B - کانال شما
DEST_CHANNEL = get_env_value("DEST_CHANNEL", "@PUBGbuyselll")

# حالت اجرا:
# "RUN" برای اجرای اصلی
# "EMOJI_IDS" برای گرفتن document_id ایموجی‌های پرمیوم از Saved Messages
RUN_MODE = get_env_value("RUN_MODE", "RUN")

# در این پروژه پست مبدا ممکن است ویدیو نباشد، عکس + کپشن است.
ONLY_VIDEO = False

# ویدیو از لینک مخفی داخل کپشن پست مبدا استخراج می‌شود.
SOURCE_CAPTION_HAS_LINKED_VIDEO = True

USE_TRANSLATOR = get_env_bool("USE_TRANSLATOR", True)
SKIP_IF_DESCRIPTION_EMPTY = get_env_bool("SKIP_IF_DESCRIPTION_EMPTY", True)

# کپشن ویدیو در تلگرام محدودیت دارد.
MAX_CAPTION_LENGTH = get_env_int("MAX_CAPTION_LENGTH", 1024)

# برای Railway اگر Volume ساختی، DATA_DIR را بگذار /data
DATA_DIR = get_env_value("DATA_DIR", ".")

TEMP_DOWNLOAD_DIR = os.path.join(DATA_DIR, "temp_downloads")
PROCESSED_FILE = os.path.join(DATA_DIR, "processed_messages.json")

# شمارنده اکانت
ACCOUNT_COUNTER_START = get_env_int("ACCOUNT_COUNTER_START", 9071)
ACCOUNT_COUNTER_FILE = os.path.join(DATA_DIR, "account_counter.json")


# ============================================================
# LINKED VIDEO SETTINGS
# ============================================================

VIDEO_LINK_KEYWORDS = [
    "لینک کامل ویدیو",
    "کامل ویدیو",
    "ویدیو کامل",
    "لینک ویدیو",
    "فیلم کامل",
    "کامل فیلم",
    "video",
    "full video",
]

# اگر لینک دقیقاً به پیام ویدیو نبود، چند پیام اطراف لینک هم چک می‌شود.
LINKED_VIDEO_NEARBY_RANGE = get_env_int("LINKED_VIDEO_NEARBY_RANGE", 4)


# ============================================================
# LINKS - لینک‌های آبی فرم PUBG
# ============================================================
# اگر لینکی نمی‌خواهی، مقدار را خالی بگذار: ""

GROUP_USERNAME = get_env_value("GROUP_USERNAME", "@PUBG_MARKETING")
GROUP_URL = get_env_value("GROUP_URL", "https://t.me/PUBG_MARKETING")

MM_USERNAME = get_env_value("MM_USERNAME", "@buyer_sellerr")
MM_URL = get_env_value("MM_URL", "https://t.me/buyer_sellerr")

WEBSITE_TEXT = get_env_value("WEBSITE_TEXT", "Website")
WEBSITE_URL = get_env_value("WEBSITE_URL", "https://pubgmarketing.netlify.app/")

BUY_NOW_TEXT = get_env_value("BUY_NOW_TEXT", "BUY NOW")
BUY_NOW_URL = get_env_value("BUY_NOW_URL", "https://t.me/buyer_sellerr")

SELL_YOUR_ACCOUNT_TEXT = get_env_value("SELL_YOUR_ACCOUNT_TEXT", "SELL YOUR ACCOUNT")
SELL_YOUR_ACCOUNT_URL = get_env_value("SELL_YOUR_ACCOUNT_URL", "https://t.me/buyer_sellerr")

PUBG_BUY_SELL_TEXT = get_env_value("PUBG_BUY_SELL_TEXT", "PUBG_BUY_SELL")
PUBG_BUY_SELL_URL = get_env_value("PUBG_BUY_SELL_URL", "https://t.me/PUBGbuyselll")


# ============================================================
# QUOTE SETTINGS
# ============================================================

QUOTE_HASHTAGS = get_env_bool("QUOTE_HASHTAGS", True)
QUOTE_ACTION_BUTTONS = get_env_bool("QUOTE_ACTION_BUTTONS", True)


# ============================================================
# CUSTOM PREMIUM EMOJI IDS
# ============================================================
# فقط document_id ها را عوض کن.
# اگر ایموجی پرمیوم نمی‌خواهی، مقدار را 0 بگذار.

CUSTOM_EMOJI_IDS = {
    "red_triangle": get_env_int("EMOJI_RED_TRIANGLE", 5972290052451994935),      # 🔻
    "green_circle": get_env_int("EMOJI_GREEN_CIRCLE", 5215685881989442149),      # 🟢
    "link": get_env_int("EMOJI_LINK", 5215441850537618106),                      # 🔗
    "outbox": get_env_int("EMOJI_OUTBOX", 5873225338984599714),                  # 📤
    "money": get_env_int("EMOJI_MONEY", 5213094908608392768),                    # 💰
    "chat": get_env_int("EMOJI_CHAT", 5872886929921413168),                      # 💬
    "person": get_env_int("EMOJI_PERSON", 5870994129244131212),                  # 👤
    "card": get_env_int("EMOJI_CARD", 6041815299412463725),                      # 💳
    "globe": get_env_int("EMOJI_GLOBE", 5870718740236079262),                    # 🌐

    # اگر کنار MM یک ایموجی خاص خواستی
    "mm_badge": get_env_int("EMOJI_MM_BADGE", 0),
}


# ============================================================
# PUBG LOGO - 12 CUSTOM EMOJI PIECES
# ============================================================
# اگر لوگوی پرمیوم PUBG داری، با RUN_MODE=EMOJI_IDS آیدی‌ها را بگیر و اینجا بگذار.
# اگر نداری، همین 0 بماند و با 🎮 نمایش داده می‌شود.

PUBG_LOGO_FALLBACK_EMOJI = get_env_value("PUBG_LOGO_FALLBACK_EMOJI", "🎮")

PUBG_LOGO_CUSTOM_EMOJI_IDS = [
    get_env_int("PUBG_LOGO_01", 5319029967726584656),
    get_env_int("PUBG_LOGO_02", 5319029967726584656),
    get_env_int("PUBG_LOGO_03", 5319029967726584656),
    get_env_int("PUBG_LOGO_04", 5319029967726584656),
    get_env_int("PUBG_LOGO_05", 5319029967726584656),
    get_env_int("PUBG_LOGO_06", 5319029967726584656),

    get_env_int("PUBG_LOGO_07", 5319029967726584656),
    get_env_int("PUBG_LOGO_08", 5319029967726584656),
    get_env_int("PUBG_LOGO_09", 5319029967726584656),
    get_env_int("PUBG_LOGO_10", 5319029967726584656),
    get_env_int("PUBG_LOGO_11", 5319029967726584656),
    get_env_int("PUBG_LOGO_12", 5319029967726584656),
]


# ============================================================
# FORM SETTINGS
# ============================================================

ACCOUNT_NUMBER_TAG = get_env_value("ACCOUNT_NUMBER_TAG", "#account_number")

HASHTAGS = get_env_value(
    "HASHTAGS",
    "#PUBG #PUBGBUY #PUBGSELL #PUBGMOBILE #PUBG_MOBILE #ACCOUNTPUBG"
)

ACCOUNT_PRICE_TEXT = get_env_value("ACCOUNT_PRICE_TEXT", "DM for price")


# ============================================================
# SOURCE CAPTION FILTER SETTINGS - PUBG
# ============================================================

DESCRIPTION_MARKERS = [
    "توضیحات اکانت",
    "توضیحات",
    "مشخصات اکانت",
    "مشخصات",
    "📄 توضیحات اکانت",
    "📄 توضیحات",
]

FORBIDDEN_LINE_KEYWORDS = [
    # فروش / قیمت / ارتباط
    "قیمت",
    "تومان",
    "رنج قیمت",
    "خرید",
    "فروش",
    "جهت خرید",
    "آیدی",
    "ایدی",
    "آیدی فروشنده",
    "ایدی فروشنده",
    "واسطه",
    "قانونی",
    "نماد اعتماد",

    # لینک و منبع
    "لینک کامل ویدیو",
    "کامل ویدیو",
    "لینک ویدیو",
    "فیلم کامل",
    "لینک",
    "لینک شده",
    "لینک‌شده",
    "قابل چنج",
    "قابل تغییر",

    # متادیتای پست
    "شماره اکانت",
    "شماره اکانت:",
    "بازی:",
    "#پابجی",
    "#pubg",

    # لاگین / اتصال اکانت
    "جیمیل",
    "ایمیل",
    "ایمیل اصلی",
    "گوگل",
    "google",
    "gmail",
    "فیسبوک",
    "فیس بوک",
    "facebook",
    "fb",
    "توییتر",
    "توئیتر",
    "twitter",
    "x.com",
    "ایکس",
    "اپل",
    "apple",
    "گیم سنتر",
    "game center",
    "vk",
    "وی کی",
    "شماره",
    "شماره موبایل",
    "phone",
    "login",
    "linked",
    "link",

    # انگلیسی فروش
    "price",
    "buy",
    "sell",
    "seller",
    "middleman",
    "mm",
]

END_SECTION_KEYWORDS = [
    "جهت خرید",
    "آیدی",
    "ایدی",
    "آیدی فروشنده",
    "ایدی فروشنده",
    "واسطه",
    "خرید یوسی",
    "خرید uc",
]


# ============================================================
# BASIC UTILITIES
# ============================================================

def parse_entity_ref(value):
    if isinstance(value, int):
        return value

    if isinstance(value, str):
        value = value.strip()
        if re.fullmatch(r"-?\d+", value):
            return int(value)
        return value

    return value


SOURCE_ENTITY = parse_entity_ref(SOURCE_CHANNEL)
DEST_ENTITY = parse_entity_ref(DEST_CHANNEL)


def ensure_parent_dir(file_path: str) -> None:
    directory = os.path.dirname(file_path)

    if directory:
        os.makedirs(directory, exist_ok=True)


def load_processed_ids() -> set:
    if not os.path.exists(PROCESSED_FILE):
        return set()

    try:
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data)
    except Exception:
        return set()


def save_processed_ids(processed_ids: set) -> None:
    ensure_parent_dir(PROCESSED_FILE)

    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(processed_ids), f, ensure_ascii=False, indent=2)


def load_account_counter() -> int:
    if not os.path.exists(ACCOUNT_COUNTER_FILE):
        return ACCOUNT_COUNTER_START

    try:
        with open(ACCOUNT_COUNTER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            value = int(data.get("next_account_number", ACCOUNT_COUNTER_START))
            return value
    except Exception:
        return ACCOUNT_COUNTER_START


def save_account_counter(next_number: int) -> None:
    ensure_parent_dir(ACCOUNT_COUNTER_FILE)

    with open(ACCOUNT_COUNTER_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"next_account_number": int(next_number)},
            f,
            ensure_ascii=False,
            indent=2,
        )


def increment_account_counter(current_number: int) -> None:
    save_account_counter(int(current_number) + 1)


def normalize_text(text: str) -> str:
    if not text:
        return ""

    replacements = {
        "ي": "ی",
        "ك": "ک",
        "\u200c": " ",
        "\u200f": "",
        "\u200e": "",
        "\ufeff": "",
        "‌": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ============================================================
# CUSTOM GAME TERMS GLOSSARY - PUBG
# ============================================================

CUSTOM_TERM_REPLACEMENTS = [
    # Account quality
    (r"\bاکانت\s+گاد\b", "God account"),
    (r"\bاک\s+گاد\b", "God account"),
    (r"\bاک\s+خوب\b", "Good account"),
    (r"\bاکانت\s+خوب\b", "Good account"),
    (r"\bاک\s+خفن\b", "Great account"),
    (r"\bاکانت\s+خفن\b", "Great account"),
    (r"\bاک\s+تمیز\b", "Clean account"),
    (r"\bاکانت\s+تمیز\b", "Clean account"),
    (r"\bاک\s+فول\b", "Full account"),
    (r"\bاکانت\s+فول\b", "Full account"),
    (r"\bاک\s+پر\s+آیتم\b", "High item account"),
    (r"\bاکانت\s+پر\s+آیتم\b", "High item account"),
    (r"\bاکانت\b", "Account"),
    (r"\bاک\b", "Account"),
    (r"\bگادلی\b", "Godly"),
    (r"\bگاد\b", "God"),
    (r"\bخفن\b", "Great"),
    (r"\bتمیز\b", "Clean"),
    (r"\bارزشمند\b", "Valuable"),
    (r"\bارزون\b", "Cheap"),
    (r"\bارزان\b", "Cheap"),
    (r"\bاقتصادی\b", "Budget"),
    (r"\bفول\s+آیتم\b", "Full item"),
    (r"\bپر\s+آیتم\b", "High item"),
    (r"\bپرایتم\b", "High item"),
    (r"\bفولایتم\b", "Full item"),

    # PUBG names
    (r"\bپابجی\s+موبایل\b", "PUBG Mobile"),
    (r"\bپابجی\b", "PUBG"),
    (r"\bپابگ\b", "PUBG"),
    (r"\bpubg\s+mobile\b", "PUBG Mobile"),
    (r"\bpubg\b", "PUBG"),

    # Currency
    (r"\bیوسی\b", "UC"),
    (r"\bیو\s*سی\b", "UC"),
    (r"\buc\b", "UC"),
    (r"\bبی\s*پی\b", "BP"),
    (r"\bbp\b", "BP"),
    (r"\bای\s*جی\b", "AG"),
    (r"\bag\b", "AG"),
    (r"\bسیلور\b", "Silver"),
    (r"\bنقره\b", "Silver"),
    (r"\bکوپن\b", "Coupon"),
    (r"\bاسکرپ\b", "Scrap"),

    # Rarity
    (r"\bمتیک\b", "Mythic"),
    (r"\bمیتیک\b", "Mythic"),
    (r"\bمایتیک\b", "Mythic"),
    (r"\bمیثیک\b", "Mythic"),
    (r"\bمتیک\s+ها\b", "Mythics"),
    (r"\bمتیکها\b", "Mythics"),
    (r"\bمتیک‌ها\b", "Mythics"),
    (r"\bتعداد\s+کل\s+متیک\b", "Total Mythics"),
    (r"\bلجندری\b", "Legendary"),
    (r"\bلجنری\b", "Legendary"),
    (r"\bلجند\b", "Legendary"),
    (r"\bلجند\s+ها\b", "Legendaries"),
    (r"\bلجندها\b", "Legendaries"),
    (r"\bلجند‌ها\b", "Legendaries"),
    (r"\bاولتیمیت\b", "Ultimate"),
    (r"\bآلتیمیت\b", "Ultimate"),
    (r"\bاپیک\b", "Epic"),
    (r"\bایپک\b", "Epic"),
    (r"\bریر\b", "Rare"),
    (r"\bکامن\b", "Common"),

    # Outfits / X-Suits
    (r"\bایکس\s+سوت\b", "X-Suit"),
    (r"\bایکسسوت\b", "X-Suit"),
    (r"\bx\s*suit\b", "X-Suit"),
    (r"\bلباس\s+آپگریدی\b", "Upgradeable outfit"),
    (r"\bلباس\s+اپگریدی\b", "Upgradeable outfit"),
    (r"\bلباس\s+ارتقایی\b", "Upgradeable outfit"),
    (r"\bلباس\b", "Outfit"),
    (r"\bاوتفیت\b", "Outfit"),
    (r"\bاسکین\s+ها\b", "Skins"),
    (r"\bاسکین‌ها\b", "Skins"),
    (r"\bاسکینها\b", "Skins"),
    (r"\bاسکین\b", "Skin"),
    (r"\bسکین\b", "Skin"),

    # Famous PUBG items
    (r"\bمومیایی\b", "Mummy Set"),
    (r"\bمامی\b", "Mummy Set"),
    (r"\bفرعون\b", "Pharaoh X-Suit"),
    (r"\bفراعون\b", "Pharaoh X-Suit"),
    (r"\bپوسایدون\b", "Poseidon X-Suit"),
    (r"\bپوزایدون\b", "Poseidon X-Suit"),
    (r"\bبلادرون\b", "Blood Raven X-Suit"),
    (r"\bبلاد\s+ریون\b", "Blood Raven X-Suit"),
    (r"\bسیلوانوس\b", "Silvanus X-Suit"),
    (r"\bاوالانچ\b", "Avalanche X-Suit"),
    (r"\bمارموریس\b", "Marmoris X-Suit"),
    (r"\bایگنیس\b", "Ignis X-Suit"),
    (r"\bفیوره\b", "Fiore X-Suit"),

    # Guns
    (r"\bگان\s+آپگریدی\b", "Upgradeable gun"),
    (r"\bگان\s+اپگریدی\b", "Upgradeable gun"),
    (r"\bگان\s+ارتقایی\b", "Upgradeable gun"),
    (r"\bگانلب\b", "Gun Lab"),
    (r"\bگان\s+لب\b", "Gun Lab"),
    (r"\bگان\s+ها\b", "Guns"),
    (r"\bگان‌ها\b", "Guns"),
    (r"\bگانها\b", "Guns"),
    (r"\bگانا\b", "Guns"),
    (r"\bگان\b", "Gun"),
    (r"\bگن\b", "Gun"),
    (r"\bاسلحه\s+ها\b", "Weapons"),
    (r"\bاسلحه‌ها\b", "Weapons"),
    (r"\bاسلحه\b", "Weapon"),
    (r"\bسلاح\b", "Weapon"),
    (r"\bام\s*فور\b", "M416"),
    (r"\bامفور\b", "M416"),
    (r"\bm416\b", "M416"),
    (r"\bگلیشر\b", "Glacier M416"),
    (r"\bگلاسیر\b", "Glacier M416"),
    (r"\bglacier\b", "Glacier"),
    (r"\bای\s*کی\s*ام\b", "AKM"),
    (r"\bایکی\s*ام\b", "AKM"),
    (r"\bakm\b", "AKM"),
    (r"\bاسکار\b", "SCAR-L"),
    (r"\bاسکارل\b", "SCAR-L"),
    (r"\bscar\b", "SCAR-L"),
    (r"\bscar-l\b", "SCAR-L"),
    (r"\bام\s*هفت\b", "M762"),
    (r"\bامسون\b", "M762"),
    (r"\bm762\b", "M762"),
    (r"\bاوزی\b", "UZI"),
    (r"\buzi\b", "UZI"),
    (r"\bای\s*دبلیو\s*ام\b", "AWM"),
    (r"\bawm\b", "AWM"),
    (r"\bکارنودوهشت\b", "Kar98k"),
    (r"\bkar98\b", "Kar98k"),
    (r"\bام\s*تو\s*فور\b", "M24"),
    (r"\bm24\b", "M24"),
    (r"\bدی\s*بی\s*اس\b", "DBS"),
    (r"\bdbs\b", "DBS"),

    # Upgrade / level
    (r"\bفول\s+مکس\b", "Fully maxed"),
    (r"\bفولمکس\b", "Fully maxed"),
    (r"\bمکس\s+شده\b", "Maxed"),
    (r"\bمکس\b", "Max"),
    (r"\bآپگرید\s+شده\b", "Upgraded"),
    (r"\bاپگرید\s+شده\b", "Upgraded"),
    (r"\bآپگرید\b", "Upgrade"),
    (r"\bاپگرید\b", "Upgrade"),
    (r"\bمتریال\b", "Material"),
    (r"\bمتریال\s+ها\b", "Materials"),
    (r"\bمتریال‌ها\b", "Materials"),
    (r"\bپینت\b", "Paint"),
    (r"\bپینت\s+ها\b", "Paints"),
    (r"\bلول\s+بالا\b", "High level"),
    (r"\bلول\s+مکس\b", "Max level"),
    (r"\bلول\s+اکانت\b", "Account level"),
    (r"\bلول\b", "Level"),
    (r"\bلفل\b", "Level"),

    # Royale Pass / seasons
    (r"\bرویال\s+پس\b", "Royale Pass"),
    (r"\bرویالپس\b", "Royale Pass"),
    (r"\bرويال\s+پس\b", "Royale Pass"),
    (r"\bارپی\b", "RP"),
    (r"\brp\b", "RP"),
    (r"\bالیت\s+پس\b", "Elite Pass"),
    (r"\bالیتپس\b", "Elite Pass"),
    (r"\bالایت\s+پس\b", "Elite Pass"),
    (r"\bسیزن\s+های\s+الیت\s+شده\b", "Elite Pass seasons"),
    (r"\bسیزن\s+های\s+الیت\s+مکس\b", "Maxed Elite Pass seasons"),
    (r"\bالیت\s+مکس\b", "Maxed Elite Pass"),
    (r"\bالیت\b", "Elite Pass"),
    (r"\bسیزن\b", "Season"),

    # Rank / modes
    (r"\bکانکورر\b", "Conqueror"),
    (r"\bکانکور\b", "Conqueror"),
    (r"\bکانکر\b", "Conqueror"),
    (r"\bکانکو\b", "Conqueror"),
    (r"\bایس\s+مستر\b", "Ace Master"),
    (r"\bایس\s+دامینیتور\b", "Ace Dominator"),
    (r"\bایس\b", "Ace"),
    (r"\bکراون\b", "Crown"),
    (r"\bدایموند\b", "Diamond"),
    (r"\bدیاموند\b", "Diamond"),
    (r"\bپلاتینیوم\b", "Platinum"),
    (r"\bگلد\b", "Gold"),
    (r"\bرنک\b", "Rank"),
    (r"\bرنکد\b", "Ranked"),
    (r"\bکلاسیک\b", "Classic"),
    (r"\bمترو\s+رویال\b", "Metro Royale"),
    (r"\bمترو\b", "Metro Royale"),
    (r"\bتی\s*دی\s*ام\b", "TDM"),
    (r"\btdm\b", "TDM"),
    (r"\bآرنا\b", "Arena"),
    (r"\bارنا\b", "Arena"),

    # Crates / spins / collections
    (r"\bکریت\s+ها\b", "Crates"),
    (r"\bکریت‌ها\b", "Crates"),
    (r"\bکریتها\b", "Crates"),
    (r"\bکریت\b", "Crate"),
    (r"\bکرت\b", "Crate"),
    (r"\bکلاسیک\s+کریت\b", "Classic Crate"),
    (r"\bپرمیوم\s+کریت\b", "Premium Crate"),
    (r"\bساپلای\s+کریت\b", "Supply Crate"),
    (r"\bاسپشیال\s+کریت\b", "Special Crate"),
    (r"\bلاکی\s+اسپین\b", "Lucky Spin"),
    (r"\bلاکی\s+اسپن\b", "Lucky Spin"),
    (r"\bاسپین\b", "Spin"),
    (r"\bاسپن\b", "Spin"),
    (r"\bگردونه\b", "Spin"),
    (r"\bکالکشن\b", "Collection"),
    (r"\bکالکشن\s+ها\b", "Collections"),
    (r"\bکالکشن‌ها\b", "Collections"),

    # Inventory / misc
    (r"\bاینونتوری\b", "Inventory"),
    (r"\bاینوینتوری\b", "Inventory"),
    (r"\bایونتوری\b", "Inventory"),
    (r"\bانباری\b", "Inventory"),
    (r"\bآیتم\s+ها\b", "Items"),
    (r"\bآیتم‌ها\b", "Items"),
    (r"\bآیتمها\b", "Items"),
    (r"\bآیتم\b", "Item"),
    (r"\bایتم\s+ها\b", "Items"),
    (r"\bایتم‌ها\b", "Items"),
    (r"\bایتمها\b", "Items"),
    (r"\bایتم\b", "Item"),
    (r"\bمحبوبیت\b", "Popularity"),
    (r"\bپاپولاریتی\b", "Popularity"),
    (r"\bچیکن\b", "Chicken"),
    (r"\bچیکن\s+دینر\b", "Chicken Dinner"),
    (r"\bاموت\b", "Emote"),
    (r"\bایموت\b", "Emote"),
    (r"\bایموت\s+ها\b", "Emotes"),
    (r"\bایموتها\b", "Emotes"),
    (r"\bاموتها\b", "Emotes"),
    (r"\bکلاه\b", "Helmet"),
    (r"\bهلمت\b", "Helmet"),
    (r"\bبک\s+پک\b", "Backpack"),
    (r"\bبکپک\b", "Backpack"),
    (r"\bچتر\b", "Parachute"),
    (r"\bپاراشوت\b", "Parachute"),
    (r"\bهواپیما\b", "Plane"),
    (r"\bپلین\b", "Plane"),
    (r"\bماشین\b", "Vehicle"),
    (r"\bماشین\s+ها\b", "Vehicles"),
    (r"\bماشین‌ها\b", "Vehicles"),
    (r"\bوسایل\s+نقلیه\b", "Vehicles"),
    (r"\bدنس\b", "Dance"),
    (r"\bتایتل\b", "Title"),
    (r"\bاچیومنت\b", "Achievement"),

    # Safety / account status
    (r"\bسیف\b", "Safe"),
    (r"\bامن\b", "Safe"),
    (r"\bکلین\b", "Clean"),
    (r"\bتمیزه\b", "Clean"),
    (r"\bبدون\s+مشکل\b", "No issues"),
    (r"\bبدون\s+بن\b", "No ban"),
    (r"\bبن\s+نیست\b", "Not banned"),
    (r"\bبن\s+نشده\b", "Not banned"),
    (r"\bبند\s+نیست\b", "Not banned"),
    (r"\bبن\b", "Ban"),
    (r"\bریجن\b", "Region"),
    (r"\bگلوبال\b", "Global"),
    (r"\bکره\b", "Korea"),
    (r"\bویتنام\b", "Vietnam"),

    # Common words
    (r"\bچندتا\b", "Several"),
    (r"\bچنتا\b", "Several"),
    (r"\bزیاد\b", "Many"),
    (r"\bخیلی\s+زیاد\b", "A lot of"),
    (r"\bتعداد\s+بالا\b", "High amount of"),
    (r"\bتعداد\s+کل\b", "Total"),
    (r"\bکامل\b", "Complete"),
    (r"\bنسبتا\b", "Relatively"),
    (r"\bتقریبا\b", "Almost"),
    (r"\bباز\s+است\b", "is unlocked"),
    (r"\bباز\s+شده\b", "unlocked"),
    (r"\bباز\b", "unlocked"),
    (r"\bداره\b", "has"),
    (r"\bداراست\b", "has"),
    (r"\bموجوده\b", "available"),
    (r"\bموجود\b", "available"),
]


POST_TRANSLATION_FIXES = [
    (r"\bgad account\b", "God account"),
    (r"\bgodly account\b", "Godly account"),
    (r"\bgad\b", "God"),
    (r"\bgodly\b", "Godly"),

    (r"\bpubji\b", "PUBG"),
    (r"\bpubg mobile mobile\b", "PUBG Mobile"),
    (r"\bpubg pubg\b", "PUBG"),

    (r"\buc uc\b", "UC"),
    (r"\bbp bp\b", "BP"),
    (r"\bag ag\b", "AG"),

    (r"\bmetik\b", "Mythic"),
    (r"\bmatic\b", "Mythic"),
    (r"\bmytic\b", "Mythic"),
    (r"\bmythik\b", "Mythic"),
    (r"\bmitic\b", "Mythic"),
    (r"\bmythics\b", "Mythics"),

    (r"\blegend\b", "Legendary"),
    (r"\blegendaryy\b", "Legendary"),

    (r"\bx suit\b", "X-Suit"),
    (r"\bxsuit\b", "X-Suit"),
    (r"\bupgradeable outfit outfit\b", "Upgradeable outfit"),

    (r"\bgun lab\b", "Gun Lab"),
    (r"\bgun h?a\b", "Guns"),
    (r"\bskin h?a\b", "Skins"),
    (r"\bitem h?a\b", "Items"),

    (r"\bm 416\b", "M416"),
    (r"\bm4 16\b", "M416"),
    (r"\bglacier m416\b", "Glacier M416"),
    (r"\bak m\b", "AKM"),
    (r"\bscar l\b", "SCAR-L"),
    (r"\bm 762\b", "M762"),
    (r"\bkar 98k\b", "Kar98k"),
    (r"\bm 24\b", "M24"),

    (r"\broyal pass\b", "Royale Pass"),
    (r"\broyale pass pass\b", "Royale Pass"),
    (r"\belite pass pass\b", "Elite Pass"),
    (r"\bmaxed elite pass pass\b", "Maxed Elite Pass"),

    (r"\bconquerer\b", "Conqueror"),
    (r"\bconqueror season season\b", "Conqueror season"),
    (r"\bace master master\b", "Ace Master"),
    (r"\bace dominator dominator\b", "Ace Dominator"),

    (r"\bcrite\b", "Crate"),
    (r"\bcrites\b", "Crates"),
    (r"\bcratees\b", "Crates"),
    (r"\blucky spin spin\b", "Lucky Spin"),

    (r"\baccount account\b", "Account"),
    (r"\bgod account account\b", "God account"),
    (r"\bclean account account\b", "Clean account"),
    (r"\bgreat account account\b", "Great account"),
    (r"\bfull item account account\b", "Full item account"),
    (r"\bhas has\b", "has"),
    (r"\bis unlocked unlocked\b", "is unlocked"),
]


def apply_custom_game_glossary(text: str) -> str:
    text = normalize_text(text)

    if not text:
        return ""

    for pattern, replacement in CUSTOM_TERM_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return normalize_text(text)


def apply_post_translation_fixes(text: str) -> str:
    text = normalize_text(text)

    if not text:
        return ""

    for pattern, replacement in POST_TRANSLATION_FIXES:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    text = re.sub(r"([,.!?;:])([^\s])", r"\1 \2", text)

    text = re.sub(r"\bUC UC\b", "UC", text, flags=re.IGNORECASE)
    text = re.sub(r"\bBP BP\b", "BP", text, flags=re.IGNORECASE)
    text = re.sub(r"\bAG AG\b", "AG", text, flags=re.IGNORECASE)
    text = re.sub(r"\bPUBG PUBG\b", "PUBG", text, flags=re.IGNORECASE)

    return normalize_text(text)


def remove_source_mentions_hashtags_links(text: str) -> str:
    text = re.sub(r"@\w{3,}", "", text)
    text = re.sub(r"#\w+", "", text)
    text = re.sub(r"https?://\S+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"t\.me/\S+", "", text, flags=re.IGNORECASE)

    return normalize_text(text)


def contains_forbidden_keyword(line: str) -> bool:
    low = line.lower()
    return any(keyword.lower() in low for keyword in FORBIDDEN_LINE_KEYWORDS)


def is_uid_line(line: str) -> bool:
    low = line.lower()

    if "uid" in low:
        return True

    if "آیدی عددی" in low or "ایدی عددی" in low:
        return True

    if re.search(r"\d{10,}", line):
        return True

    return False


def is_end_section_line(line: str) -> bool:
    low = line.lower()

    if is_uid_line(line):
        return True

    return any(keyword.lower() in low for keyword in END_SECTION_KEYWORDS)


def clean_description_line(line: str) -> str:
    line = normalize_text(line)

    if not line:
        return ""

    if is_uid_line(line):
        return ""

    if contains_forbidden_keyword(line):
        return ""

    line = remove_source_mentions_hashtags_links(line)

    return normalize_text(line)


def extract_description_from_source_caption(caption: str) -> str:
    caption = normalize_text(caption)

    if not caption:
        return ""

    lines = caption.splitlines()

    start_index: Optional[int] = None
    seed_line = ""

    for i, line in enumerate(lines):
        clean_line = normalize_text(line)

        for marker in DESCRIPTION_MARKERS:
            if marker in clean_line:
                start_index = i + 1

                after_marker = clean_line.split(marker, 1)[1].strip()
                after_marker = after_marker.strip(":：-–—| ")

                if after_marker:
                    seed_line = after_marker

                break

        if start_index is not None:
            break

    description_lines: List[str] = []

    # حالت اول: کپشن مارکر توضیحات دارد
    if start_index is not None:
        if seed_line:
            cleaned_seed = clean_description_line(seed_line)
            if cleaned_seed:
                description_lines.append(cleaned_seed)

        for line in lines[start_index:]:
            line = normalize_text(line)

            if not line:
                continue

            if is_end_section_line(line):
                break

            cleaned = clean_description_line(line)

            if cleaned:
                description_lines.append(cleaned)

    # حالت دوم: کپشن مثل عکس ارسالی، مارکر توضیحات ندارد
    else:
        for line in lines:
            line = normalize_text(line)

            if not line:
                continue

            cleaned = clean_description_line(line)

            if cleaned:
                description_lines.append(cleaned)

    result = "\n".join(description_lines)
    result = normalize_text(result)

    result_lines = [line.strip() for line in result.splitlines() if line.strip()]

    return "\n".join(result_lines).strip()


def translate_to_english(text: str) -> str:
    if not text:
        return ""

    text = apply_custom_game_glossary(text)

    if not USE_TRANSLATOR:
        return apply_post_translation_fixes(text)

    if GoogleTranslator is None:
        print("Package deep-translator نصب نیست. متن بدون ترجمه ارسال می‌شود.")
        return apply_post_translation_fixes(text)

    try:
        translator = GoogleTranslator(source="auto", target="en")
        translated_lines = []

        for line in text.splitlines():
            line = line.strip()

            if not line:
                translated_lines.append("")
                continue

            line = apply_custom_game_glossary(line)

            try:
                translated = translator.translate(line)
                translated = apply_post_translation_fixes(translated)
                translated_lines.append(translated)
            except Exception:
                translated_lines.append(apply_post_translation_fixes(line))

        final_text = normalize_text("\n".join(translated_lines))
        final_text = apply_post_translation_fixes(final_text)

        return final_text

    except Exception as e:
        print(f"Translation error: {e}")
        return apply_post_translation_fixes(text)


def utf16_length(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def substring_by_utf16(text: str, offset: int, length: int) -> str:
    data = text.encode("utf-16-le")
    part = data[offset * 2:(offset + length) * 2]
    return part.decode("utf-16-le", errors="ignore")


def is_valid_url(url: str) -> bool:
    if not url:
        return False

    url = url.strip()

    return (
        url.startswith("http://")
        or url.startswith("https://")
        or url.startswith("tg://")
    )


# ============================================================
# CAPTION BUILDER WITH CUSTOM EMOJI, LINKS, QUOTES
# ============================================================

class CaptionBuilder:
    def __init__(self):
        self.text_parts: List[str] = []
        self.entities: List[object] = []

    @property
    def text(self) -> str:
        return "".join(self.text_parts)

    def append(self, value: str) -> None:
        self.text_parts.append(value)

    def append_custom_emoji(self, emoji: str, key: str) -> None:
        document_id = int(CUSTOM_EMOJI_IDS.get(key, 0) or 0)
        self.append_custom_emoji_by_id(emoji, document_id)

    def append_custom_emoji_by_id(self, emoji: str, document_id: int) -> None:
        offset = utf16_length(self.text)
        length = utf16_length(emoji)

        self.text_parts.append(emoji)

        if document_id:
            self.entities.append(
                types.MessageEntityCustomEmoji(
                    offset=offset,
                    length=length,
                    document_id=int(document_id),
                )
            )

    def append_text_link(self, text: str, url: str = "") -> None:
        offset = utf16_length(self.text)
        length = utf16_length(text)

        self.text_parts.append(text)

        if is_valid_url(url):
            self.entities.append(
                types.MessageEntityTextUrl(
                    offset=offset,
                    length=length,
                    url=url.strip(),
                )
            )

    def append_blockquote(self, text: str, url: str = "") -> None:
        offset = utf16_length(self.text)
        length = utf16_length(text)

        self.text_parts.append(text)

        if is_valid_url(url):
            self.entities.append(
                types.MessageEntityTextUrl(
                    offset=offset,
                    length=length,
                    url=url.strip(),
                )
            )

        blockquote_class = getattr(types, "MessageEntityBlockquote", None)

        if blockquote_class is not None:
            try:
                self.entities.append(
                    blockquote_class(
                        offset=offset,
                        length=length,
                    )
                )
            except TypeError:
                try:
                    self.entities.append(
                        blockquote_class(
                            offset=offset,
                            length=length,
                            collapsed=False,
                        )
                    )
                except Exception:
                    pass

    def append_pubg_logo(self) -> None:
        ids = PUBG_LOGO_CUSTOM_EMOJI_IDS[:]

        while len(ids) < 12:
            ids.append(0)

        for i in range(6):
            self.append_custom_emoji_by_id(PUBG_LOGO_FALLBACK_EMOJI, ids[i])

        self.append("\n")

        for i in range(6, 12):
            self.append_custom_emoji_by_id(PUBG_LOGO_FALLBACK_EMOJI, ids[i])


# ============================================================
# FINAL CAPTION - FORM PUBG
# ============================================================

def build_caption_no_trim(description_en: str, account_number: int) -> Tuple[str, List[object]]:
    now_text = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    b = CaptionBuilder()

    b.append_custom_emoji("🔻", "red_triangle")
    b.append(" Has a barcode to prevent abuse & fraud\n\n")

    b.append(f"{ACCOUNT_NUMBER_TAG}{account_number}\n\n")

    b.append("Status")
    b.append_custom_emoji("🟢", "green_circle")
    b.append("\n\n")

    b.append_custom_emoji("🔗", "link")
    b.append(f" | Synced on: {now_text}\n\n")

    b.append_custom_emoji("📤", "outbox")
    b.append("| Description:\n\n")

    if description_en.strip():
        b.append(description_en.strip())
        b.append("\n\n")

    b.append_pubg_logo()
    b.append("\n\n")

    if QUOTE_HASHTAGS:
        b.append_blockquote(HASHTAGS)
    else:
        b.append(HASHTAGS)

    b.append("\n\n")

    if is_valid_url(PUBG_BUY_SELL_URL):
        b.append_text_link(PUBG_BUY_SELL_TEXT, PUBG_BUY_SELL_URL)
    else:
        b.append(PUBG_BUY_SELL_TEXT)

    b.append("\n\n")

    b.append_custom_emoji("💰", "money")
    b.append("| Account Price: ")
    b.append(ACCOUNT_PRICE_TEXT)
    b.append("\n\n")

    b.append_custom_emoji("💬", "chat")
    b.append("Group ")
    b.append_text_link(GROUP_USERNAME, GROUP_URL)
    b.append("\n\n")

    b.append_custom_emoji("👤", "person")
    b.append("MM ")
    b.append_text_link(MM_USERNAME, MM_URL)
    b.append_custom_emoji("💳", "card")

    if int(CUSTOM_EMOJI_IDS.get("mm_badge", 0) or 0):
        b.append(" ")
        b.append_custom_emoji("💀", "mm_badge")

    b.append("\n\n")

    b.append_custom_emoji("🌐", "globe")
    b.append_text_link(WEBSITE_TEXT, WEBSITE_URL)
    b.append("\n\n")

    if QUOTE_ACTION_BUTTONS:
        b.append_blockquote(BUY_NOW_TEXT, BUY_NOW_URL)
    else:
        b.append_text_link(BUY_NOW_TEXT, BUY_NOW_URL)

    b.append("\n\n")

    if QUOTE_ACTION_BUTTONS:
        b.append_blockquote(SELL_YOUR_ACCOUNT_TEXT, SELL_YOUR_ACCOUNT_URL)
    else:
        b.append_text_link(SELL_YOUR_ACCOUNT_TEXT, SELL_YOUR_ACCOUNT_URL)

    return b.text, b.entities


def build_final_caption(description_en: str, account_number: int) -> Tuple[str, List[object]]:
    description_en = normalize_text(description_en)

    text, entities = build_caption_no_trim(description_en, account_number)

    if MAX_CAPTION_LENGTH <= 0:
        return text, entities

    if len(text) <= MAX_CAPTION_LENGTH:
        return text, entities

    ellipsis = "\n..."

    low = 0
    high = len(description_en)
    best_description = ""

    while low <= high:
        mid = (low + high) // 2
        candidate = description_en[:mid].rstrip()

        if candidate:
            candidate = candidate + ellipsis

        candidate_text, _ = build_caption_no_trim(candidate, account_number)

        if len(candidate_text) <= MAX_CAPTION_LENGTH:
            best_description = candidate
            low = mid + 1
        else:
            high = mid - 1

    return build_caption_no_trim(best_description, account_number)


# ============================================================
# MESSAGE / MEDIA HELPERS
# ============================================================

def message_has_video(message) -> bool:
    if not message:
        return False

    if getattr(message, "video", None):
        return True

    document = getattr(message, "document", None)
    if not document:
        return False

    mime_type = getattr(document, "mime_type", "") or ""
    return mime_type.startswith("video/")


def get_message_unique_key(message) -> str:
    chat_id = getattr(message, "chat_id", None) or "unknown"
    return f"{chat_id}:{message.id}"


def ensure_temp_dir() -> None:
    os.makedirs(TEMP_DOWNLOAD_DIR, exist_ok=True)


def safe_remove_file(path: Optional[str]) -> None:
    if not path:
        return

    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def entity_text_from_message(message, entity) -> str:
    text = message.message or ""

    try:
        return substring_by_utf16(text, entity.offset, entity.length).strip()
    except Exception:
        return ""


def looks_like_wanted_video_link_text(text: str) -> bool:
    text = normalize_text(text).lower()

    if not text:
        return False

    return any(keyword.lower() in text for keyword in VIDEO_LINK_KEYWORDS)


def extract_video_link_urls_from_caption_entities(message) -> List[str]:
    """
    لینک‌های مخفی داخل کپشن را از entities تلگرام استخراج می‌کند.
    مخصوص متن‌های آبی مثل: لینک کامل ویدیو
    """
    urls: List[str] = []

    text = message.message or ""
    entities = message.entities or []

    for entity in entities:
        entity_visible_text = entity_text_from_message(message, entity)

        if isinstance(entity, types.MessageEntityTextUrl):
            url = getattr(entity, "url", "") or ""

            if not url:
                continue

            if looks_like_wanted_video_link_text(entity_visible_text):
                urls.insert(0, url)
            else:
                urls.append(url)

        elif isinstance(entity, types.MessageEntityUrl):
            url = entity_visible_text

            if url:
                urls.append(url)

    if not urls and text:
        found_urls = re.findall(r"(https?://\S+|t\.me/\S+)", text, flags=re.IGNORECASE)
        urls.extend(found_urls)

    cleaned_urls = []

    for url in urls:
        url = url.strip().rstrip(").,،؛;")
        if url.startswith("t.me/"):
            url = "https://" + url

        if url and url not in cleaned_urls:
            cleaned_urls.append(url)

    return cleaned_urls


def parse_telegram_message_link(url: str):
    """
    خروجی:
    entity_ref, message_id

    پشتیبانی:
    https://t.me/username/123
    https://t.me/s/username/123
    https://t.me/c/1234567890/123
    tg://resolve?domain=username&post=123
    """
    if not url:
        return None, None

    url = url.strip()

    if url.startswith("t.me/"):
        url = "https://" + url

    parsed = urlparse(url)

    if parsed.scheme == "tg" and parsed.netloc == "resolve":
        query = parse_qs(parsed.query)

        domain = query.get("domain", [None])[0]
        post = query.get("post", [None])[0]

        if domain and post and str(post).isdigit():
            return domain, int(post)

        return None, None

    if parsed.netloc not in ["t.me", "telegram.me", "www.t.me", "www.telegram.me"]:
        return None, None

    path = unquote(parsed.path or "").strip("/")

    if not path:
        return None, None

    parts = [p for p in path.split("/") if p]

    if not parts:
        return None, None

    if parts[0] == "s":
        parts = parts[1:]

    if len(parts) < 2:
        return None, None

    if parts[0] == "c":
        if len(parts) < 3:
            return None, None

        internal_channel_id = parts[1]
        message_id = parts[2]

        if not internal_channel_id.isdigit() or not message_id.isdigit():
            return None, None

        entity_ref = int("-100" + internal_channel_id)

        return entity_ref, int(message_id)

    username = parts[0]
    message_id = parts[1]

    if not message_id.isdigit():
        return None, None

    return username, int(message_id)


# ============================================================
# TELEGRAM CLIENT
# ============================================================

if TELEGRAM_SESSION_STRING:
    client = TelegramClient(StringSession(TELEGRAM_SESSION_STRING), API_ID, API_HASH)
else:
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

processed_ids = load_processed_ids()

account_counter_lock = asyncio.Lock()


async def find_video_message_near_link(entity_ref, message_id: int):
    """
    اگر لینک دقیقاً به پیام ویدیو بود، همان را برمی‌گرداند.
    اگر لینک به آلبوم یا پیام کناری بود، چند پیام اطراف را هم چک می‌کند.
    """
    if not entity_ref or not message_id:
        return None

    try:
        entity = await client.get_entity(entity_ref)
    except Exception as e:
        print(f"Cannot resolve linked entity {entity_ref}: {e}")
        return None

    start_id = max(1, int(message_id) - LINKED_VIDEO_NEARBY_RANGE)
    end_id = int(message_id) + LINKED_VIDEO_NEARBY_RANGE

    ids = list(range(start_id, end_id + 1))

    try:
        messages = await client.get_messages(entity, ids=ids)
    except Exception as e:
        print(f"Cannot get linked messages around {entity_ref}/{message_id}: {e}")
        return None

    if not isinstance(messages, list):
        messages = [messages]

    valid_messages = [m for m in messages if m]

    for msg in valid_messages:
        if msg.id == message_id and message_has_video(msg):
            return msg

    video_messages = [m for m in valid_messages if message_has_video(m)]

    if not video_messages:
        return None

    video_messages.sort(key=lambda m: abs(int(m.id) - int(message_id)))

    return video_messages[0]


async def get_linked_video_message_from_source_caption(source_message):
    """
    از کپشن پست عکس‌دار کانال A لینک ویدیو را پیدا می‌کند
    و پیام ویدیویی مقصد را برمی‌گرداند.
    """
    urls = extract_video_link_urls_from_caption_entities(source_message)

    if not urls:
        print("No linked video URL found in source caption entities.")
        return None

    print("Candidate video URLs:")
    for url in urls:
        print(f"- {url}")

    for url in urls:
        entity_ref, message_id = parse_telegram_message_link(url)

        if not entity_ref or not message_id:
            print(f"Skipped invalid Telegram message link: {url}")
            continue

        video_message = await find_video_message_near_link(entity_ref, message_id)

        if video_message and message_has_video(video_message):
            print(f"Linked video found: {entity_ref}/{video_message.id}")
            return video_message

    print("No video message found from linked URLs.")

    return None


async def print_custom_emoji_ids_from_saved_messages(limit: int = 30) -> None:
    """
    از آخرین پیام‌های Saved Messages ایموجی‌های پرمیوم را پیدا می‌کند
    و document_id آن‌ها را چاپ می‌کند.
    """
    await client.start()

    messages = await client.get_messages("me", limit=limit)

    print("\nChecking Saved Messages for premium custom emojis...\n")

    found = False

    for msg in messages:
        if not msg.message or not msg.entities:
            continue

        for entity in msg.entities:
            if isinstance(entity, types.MessageEntityCustomEmoji):
                found = True
                emoji_text = substring_by_utf16(
                    msg.message,
                    entity.offset,
                    entity.length,
                )

                print("=" * 60)
                print(f"Emoji Text : {emoji_text}")
                print(f"Document ID: {entity.document_id}")
                print(f"Offset     : {entity.offset}")
                print(f"Length     : {entity.length}")

    if not found:
        print("هیچ Premium Custom Emoji در آخرین پیام‌های Saved Messages پیدا نشد.")
        print("یک پیام شامل ایموجی‌های پرمیوم داخل Saved Messages بفرست و دوباره اجرا کن.")

    print("\nDone.\n")


async def send_video_with_new_caption(video_message, final_caption: str, entities: List[object]) -> None:
    ensure_temp_dir()

    downloaded_path = None

    try:
        print("Downloading linked video media...")
        downloaded_path = await client.download_media(video_message, file=TEMP_DOWNLOAD_DIR)

        if not downloaded_path:
            raise RuntimeError("Download failed. downloaded_path is empty.")

        print("Uploading video to destination channel...")

        await client.send_file(
            entity=DEST_ENTITY,
            file=downloaded_path,
            caption=final_caption,
            formatting_entities=entities,
            supports_streaming=True,
            force_document=False,
        )

    finally:
        safe_remove_file(downloaded_path)


async def process_message(message) -> None:
    unique_key = get_message_unique_key(message)

    if unique_key in processed_ids:
        print(f"Already processed: {unique_key}")
        return

    source_caption = message.message or ""

    if not source_caption:
        print(f"Skipped message without caption: {unique_key}")
        return

    video_message = None

    if message_has_video(message):
        video_message = message
        print(f"Source message itself has video: {unique_key}")

    elif SOURCE_CAPTION_HAS_LINKED_VIDEO:
        print(f"Source message has no video. Trying to extract linked video: {unique_key}")
        video_message = await get_linked_video_message_from_source_caption(message)

    if ONLY_VIDEO and not video_message:
        print(f"Skipped because no video found: {unique_key}")
        return

    if not video_message:
        print(f"Skipped because linked video was not found: {unique_key}")
        return

    description = extract_description_from_source_caption(source_caption)

    print("\n" + "=" * 60)
    print(f"New source message: {unique_key}")
    print("- Extracted Description:")
    print(description if description else "[EMPTY]")

    if SKIP_IF_DESCRIPTION_EMPTY and not description:
        print(f"Skipped because description is empty after filtering: {unique_key}")
        return

    description_en = translate_to_english(description)

    print("- Translated Description:")
    print(description_en if description_en else "[EMPTY]")

    if SKIP_IF_DESCRIPTION_EMPTY and not description_en:
        print(f"Skipped because translated description is empty: {unique_key}")
        return

    try:
        async with account_counter_lock:
            if unique_key in processed_ids:
                print(f"Already processed inside lock: {unique_key}")
                return

            account_number = load_account_counter()
            final_caption, entities = build_final_caption(description_en, account_number)

            print("- Account Number:", account_number)
            print("- Final Caption Length:", len(final_caption))
            print("- Entities Count:", len(entities))

            await send_video_with_new_caption(video_message, final_caption, entities)

            processed_ids.add(unique_key)
            save_processed_ids(processed_ids)

            increment_account_counter(account_number)

            print(f"Posted successfully: {unique_key}")
            print(f"Account number used: {account_number}")
            print(f"Next account number: {account_number + 1}")

    except FloodWaitError as e:
        print(f"FloodWait: sleeping for {e.seconds} seconds")
        await asyncio.sleep(e.seconds + 5)
        await process_message(message)

    except Exception as e:
        print(f"Error while processing {unique_key}: {e}")


@client.on(events.NewMessage(chats=SOURCE_ENTITY))
async def new_message_handler(event):
    await process_message(event.message)


async def main() -> None:
    if not API_ID:
        raise RuntimeError("API_ID را داخل کد یا Railway Variables وارد کن.")

    if not API_HASH or API_HASH == "PUT_YOUR_API_HASH_HERE":
        raise RuntimeError("API_HASH را داخل کد یا Railway Variables وارد کن.")

    if RUN_MODE == "EMOJI_IDS":
        await print_custom_emoji_ids_from_saved_messages()
        return

    if not SOURCE_ENTITY:
        raise RuntimeError("SOURCE_CHANNEL را داخل کد یا Railway Variables وارد کن.")

    if not DEST_ENTITY:
        raise RuntimeError("DEST_CHANNEL را داخل کد یا Railway Variables وارد کن.")

    await client.start()

    me = await client.get_me()

    print("\nTelegram client started.")
    print(f"Logged in as: {me.first_name} / ID: {me.id}")
    print(f"Source channel: {SOURCE_ENTITY}")
    print(f"Destination channel: {DEST_ENTITY}")
    print(f"Data dir: {DATA_DIR}")
    print(f"Counter file: {ACCOUNT_COUNTER_FILE}")
    print(f"Processed file: {PROCESSED_FILE}")
    print(f"Next account number: {load_account_counter()}")
    print("Listening for new PUBG source posts with linked videos...\n")

    await client.run_until_disconnected()


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())