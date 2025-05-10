import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

TELEGRAM_TOKEN = "8195582384:AAEqMSrcqTRLtRHAC2oYU8dGynMHOnvzIJQ"
BINANCE_API_URL = "https://api.binance.com/api/v3"

CANDLE_PATTERNS = {
    # أنماط صعودية
    "المطرقة": {  # hammer
        "emoji": "🔨",
        "direction": "صعودي قوي",
        "condition": lambda o, h, l, c: (c > o) and ((h-l) > 3*(c-o)) and ((o-l)/(0.001+h-l) > 0.6)
    },
    "المطرقة المقلوبة": {  # inverted_hammer
        "emoji": "🔄",
        "direction": "صعودي",
        "condition": lambda o, h, l, c: (c > o) and ((h-l) > 3*(c-o)) and ((h-c)/(0.001+h-l) > 0.6)
    },
    "الابتلاع الصعودي": {  # bullish_engulfing
        "emoji": "🟢",
        "direction": "صعودي قوي",
        "condition": lambda o1, h1, l1, c1, o2, h2, l2, c2: (c1 < o1) and (c2 > o2) and (c2 > o1) and (o2 < c1)
    },
    "خط الاختراق": {  # piercing_line
        "emoji": "🧵",
        "direction": "صعودي",
        "condition": lambda o1, h1, l1, c1, o2, h2, l2, c2: (c1 < o1) and (o2 < l1) and (c2 > (o1+c1)/2)
    },
    "النجمة الصباحية": {  # morning_star
        "emoji": "🌅",
        "direction": "صعودي قوي",
        "condition": lambda o1, h1, l1, c1, o2, h2, l2, c2, o3, h3, l3, c3: (c1 < o1) and (abs(c2-o2) < (h2-l2)*0.3) and (c3 > o3) and (c3 > (o1+c1)/2)
    },
    "الجنود الثلاثة البيض": {  # three_white_soldiers
        "emoji": "💂💂💂",
        "direction": "صعودي قوي",
        "condition": lambda o1, h1, l1, c1, o2, h2, l2, c2, o3, h3, l3, c3: all(c > o for c, o in [(c1,o1),(c2,o2),(c3,o3)]) and all(o < prev_c for o, prev_c in [(o2,c1),(o3,c2)]) and all(c < next_h for c, next_h in [(c1,h2),(c2,h3)])
    },
    "طريقة الصعود": {  # rising_method
        "emoji": "📈",
        "direction": "صعودي",
        "condition": lambda o1, h1, l1, c1, o2, h2, l2, c2, o3, h3, l3, c3: (c1 > o1) and (c2 > o2) and (c3 > o3) and (l1 < l2 < l3) and (h1 < h2 < h3)
    },
    "حزام التثبيت الصعودي": {  # belt_hold_bullish
        "emoji": "🔼",
        "direction": "صعودي",
        "condition": lambda o, h, l, c: (c > o) and ((h - c) < 0.1 * (h - l)) and ((o - l) < 0.1 * (h - l))
    },
    "تاسوكي الصاعد": {  # upside_tasuki
        "emoji": "🎎",
        "direction": "صعودي",
        "condition": lambda o1, h1, l1, c1, o2, h2, l2, c2, o3, h3, l3, c3: (c1 > o1) and (c2 > o2) and (c3 < o3) and (o3 > c2) and (c3 > o1)
    },
    "الحمل الصعودي": {  # harami_bullish
        "emoji": "🤰",
        "direction": "صعودي",
        "condition": lambda o1, h1, l1, c1, o2, h2, l2, c2: (c1 < o1) and (c2 > o2) and (o2 > c1) and (c2 < o1)
    },
    "ذبابة التنين": {  # dragonfly_doji
        "emoji": "🦟",
        "direction": "صعودي",
        "condition": lambda o, h, l, c: abs(o - c) < 0.1 * (h - l) and ((min(o,c) - l) > 0.7*(h-l))
    },

    # أنماط هبوطية
    "المشنوق": {  # hanging_man
        "emoji": "👨‍🦳",
        "direction": "هبوطي قوي",
        "condition": lambda o, h, l, c: (o > c) and ((h-l) > 3*(o-c)) and ((o-l)/(0.001+h-l) > 0.6)
    },
    "النجمة الهابطة": {  # shooting_star
        "emoji": "⭐",
        "direction": "هبوطي قوي",
        "condition": lambda o, h, l, c: (o > c) and ((h-l) > 3*(o-c)) and ((h-o)/(0.001+h-l) > 0.6)
    },
    "الابتلاع الهبوطي": {  # bearish_engulfing
        "emoji": "🔴",
        "direction": "هبوطي قوي",
        "condition": lambda o1, h1, l1, c1, o2, h2, l2, c2: (c1 > o1) and (c2 < o2) and (c2 < o1) and (o2 > c1)
    },
    "السحابة المظلمة": {  # dark_cloud_cover
        "emoji": "☁️",
        "direction": "هبوطي",
        "condition": lambda o1, h1, l1, c1, o2, h2, l2, c2: (c1 > o1) and (o2 > h1) and (c2 < (o1+c1)/2) and (c2 > o2*0.9)
    },
    "النجمة المسائية": {  # evening_star
        "emoji": "🌇",
        "direction": "هبوطي قوي",
        "condition": lambda o1, h1, l1, c1, o2, h2, l2, c2, o3, h3, l3, c3: (c1 > o1) and (abs(c2-o2) < (h2-l2)*0.3) and (c3 < o3) and (c3 < (o1+c1)/2)
    },
    "الغربان الثلاثة السوداء": {  # three_black_crows
        "emoji": "🐦‍⬛🐦‍⬛🐦‍⬛",
        "direction": "هبوطي قوي",
        "condition": lambda o1, h1, l1, c1, o2, h2, l2, c2, o3, h3, l3, c3: all(c < o for c, o in [(c1,o1),(c2,o2),(c3,o3)]) and all(o > prev_c for o, prev_c in [(o2,c1),(o3,c2)]) and all(c > next_l for c, next_l in [(c1,l2),(c2,l3)])
    },
    "طريقة الهبوط": {  # falling_method
        "emoji": "📉",
        "direction": "هبوطي",
        "condition": lambda o1, h1, l1, c1, o2, h2, l2, c2, o3, h3, l3, c3: (c1 < o1) and (c2 < o2) and (c3 < o3) and (h1 > h2 > h3) and (l1 > l2 > l3)
    },
    "حزام التثبيت الهبوطي": {  # belt_hold_bearish
        "emoji": "🔽",
        "direction": "هبوطي",
        "condition": lambda o, h, l, c: (c < o) and ((h - o) < 0.1 * (h - l)) and ((c - l) < 0.1 * (h - l))
    },
    "تاسوكي الهابط": {  # downside_tasuki
        "emoji": "🎎",
        "direction": "هبوطي",
        "condition": lambda o1, h1, l1, c1, o2, h2, l2, c2, o3, h3, l3, c3: (c1 < o1) and (c2 < o2) and (c3 > o3) and (o3 < c2) and (c3 < o1)
    },
    "الحمل الهبوطي": {  # harami_bearish
        "emoji": "🤰",
        "direction": "هبوطي",
        "condition": lambda o1, h1, l1, c1, o2, h2, l2, c2: (c1 > o1) and (c2 < o2) and (o2 < c1) and (c2 > o1)
    },
    "شاهد القبر": {  # gravestone_doji
        "emoji": "🪦",
        "direction": "هبوطي",
        "condition": lambda o, h, l, c: abs(o - c) < 0.1 * (h - l) and ((h - max(o,c)) > 0.7*(h-l))
    },

    # أنماط خاصة
    "الماروبوزو": {  # marubozu
        "emoji": "🔷",
        "direction": "حاسم",
        "condition": lambda o, h, l, c: abs(o - c) > 0.9 * (h - l) and (abs(h - max(o,c)) < 0.1 * (h-l)) and (abs(l - min(o,c)) < 0.1 * (h-l))
    },
    "الدوجي": {  # doji
        "emoji": "➕",
        "direction": "محايد",
        "condition": lambda o, h, l, c: abs(o - c) < 0.1 * (h - l)
    },
    "الدوجي طويل الأرجل": {  # long_legged_doji
        "emoji": "🦵",
        "direction": "محايد",
        "condition": lambda o, h, l, c: abs(o - c) < 0.1 * (h - l) and ((h - max(o,c)) > 0.4*(h-l)) and ((min(o,c) - l) > 0.4*(h-l))
    },
    "الملقط العلوي": {  # tweezer_top
        "emoji": "✂️",
        "direction": "هبوطي",
        "condition": lambda o1, h1, l1, c1, o2, h2, l2, c2: abs(h1 - h2) < 0.005 * h1 and c1 > o1 and c2 < o2
    },
    "الملقط السفلي": {  # tweezer_bottom
        "emoji": "✂️",
        "direction": "صعودي",
        "condition": lambda o1, h1, l1, c1, o2, h2, l2, c2: abs(l1 - l2) < 0.005 * l1 and c1 < o1 and c2 > o2
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 تحليل عملة", callback_data="select_currency")],
        [InlineKeyboardButton("ℹ️ مساعدة", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            "📈 بوت التحليل الفني المتقدم\n\n"
            "مرحباً! أنا بوت التحليل الفني الذكي الذي يساعدك في تحليل العملات الرقمية.\n"
            "اضغط على الزر أدناه لبدء التحليل:",
            reply_markup=reply_markup
        )
    else:
        await update.callback_query.edit_message_text(
            "📈 بوت التحليل الفني المتقدم\n\n"
            "مرحباً! أنا بوت التحليل الفني الذكي الذي يساعدك في تحليل العملات الرقمية.\n"
            "اضغط على الزر أدناه لبدء التحليل:",
            reply_markup=reply_markup
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "select_currency":
        await query.edit_message_text(
            "🔍 الرجاء إدخال رمز العملة التي تريد تحليلها (مثال: BTC أو ETH أو BTCUSDT):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]])
        )
        context.user_data["awaiting_currency"] = True
        return
    
    elif data == "main_menu":
        await start(update, context)
        return
    
    elif data.startswith("timeframe_"):
        symbol = context.user_data.get("selected_symbol")
        timeframe = data.split("_")[1]
        await perform_analysis(update, symbol, timeframe, is_callback=True)
        return
    
    elif data.startswith("refresh_"):
        symbol = context.user_data.get("selected_symbol")
        timeframe = data.split("_")[1]
        await perform_analysis(update, symbol, timeframe, is_callback=True, refresh=True)
        return
    
    elif data.startswith("full_"):
        symbol = data.split("_")[1]
        await full_analysis(update, context)
        return
    
    elif data == "help":
        await query.edit_message_text(
            "📚 مساعدة:\n\n"
            "1. اضغط على زر 'تحليل عملة'\n"
            "2. أدخل رمز العملة (مثال: BTC أو ETH)\n"
            "3. اختر الفترة الزمنية للتحليل\n"
            "4. استعرض النتائج واتخذ قرارك\n\n"
            "المميزات:\n"
            "- توقع الأسعار مع نسبة ثقة\n"
            "- تحليل 35+ نمط شمعة\n"
            "- 10 مؤشرات فنية\n"
            "- توصيات ذكية",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]])
        )
        return

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_currency"):
        symbol = update.message.text.upper()
        
        # إذا لم يكن الرمز يحتوي على USDT، نضيفه تلقائياً
        if not symbol.endswith("USDT") and len(symbol) <= 5:
            symbol += "USDT"
        
        context.user_data["selected_symbol"] = symbol
        context.user_data["awaiting_currency"] = False
        
        keyboard = [
            [
                InlineKeyboardButton("15 دقيقة", callback_data="timeframe_15m"),
                InlineKeyboardButton("1 ساعة", callback_data="timeframe_1h"),
            ],
            [
                InlineKeyboardButton("4 ساعات", callback_data="timeframe_4h"),
                InlineKeyboardButton("1 يوم", callback_data="timeframe_1d"),
            ],
            [
                InlineKeyboardButton("🔙 رجوع", callback_data="select_currency"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"⏳ اختر الفترة الزمنية لتحليل {symbol}:",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "🚫 لم أفهم طلبك. الرجاء استخدام الأزرار للتفاعل مع البوت.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("القائمة الرئيسية", callback_data="main_menu")]])
        )

async def perform_analysis(update: Update, symbol: str, timeframe: str, is_callback=False, refresh=False):
    if is_callback:
        query = update.callback_query
        await query.answer()
    
    analysis = get_analysis_data(symbol, timeframe)
    if not analysis:
        error_msg = "❌ فشل في جلب البيانات. الرجاء المحاولة لاحقاً."
        if is_callback:
            await query.edit_message_text(error_msg)
        else:
            await update.message.reply_text(error_msg)
        return
    
    report = generate_analysis_report(analysis)
    
    # أزرار بعد التحليل
    keyboard = [
        [
            InlineKeyboardButton("🔄 تحديث التحليل", callback_data=f"refresh_{timeframe}"),
            InlineKeyboardButton("⏳ تغيير الإطار الزمني", callback_data="select_currency"),
        ],
        [
            InlineKeyboardButton("📊 تحليل شامل", callback_data=f"full_{symbol}"),
            InlineKeyboardButton("🔙 رجوع", callback_data="main_menu"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if refresh:
        await query.edit_message_text(report, reply_markup=reply_markup)
    elif is_callback:
        await query.edit_message_text(report, reply_markup=reply_markup)
    else:
        await update.message.reply_text(report, reply_markup=reply_markup)

async def full_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    symbol = query.data.split("_")[1]
    timeframes = ["15m", "1h", "4h", "1d"]
    reports = []
    
    for tf in timeframes:
        analysis = get_analysis_data(symbol, tf)
        if analysis:
            recommendation = generate_recommendation(analysis)
            prediction = calculate_price_prediction(analysis, analysis['timeframe'])
            reports.append({
                'timeframe': tf,
                'price': analysis['indicators']['current_price'],
                'prediction': prediction['predicted_price'],
                'confidence': prediction['confidence'],
                'trend': analysis['trend'],
                'recommendation': recommendation['decision'],
                'patterns': analysis['candle_patterns']
            })
    
    if not reports:
        await query.edit_message_text("❌ فشل في جلب البيانات")
        return
    
    report = "📊 التحليل الشامل\n\n"
    for r in reports:
        report += f"""⏳ {r['timeframe']}:
💰 السعر: {r['price']:.4f}
🎯 التوقع: {r['prediction']:.4f} (ثقة: {r['confidence']}%)
📈 الاتجاه: {r['trend']}
💡 التوصية: {r['recommendation']}
🔍 أنماط الشموع:
"""
        if r['patterns'] and r['patterns'][0] != "🔍 لا توجد أنماط واضحة":
            for pattern in r['patterns']:
                report += f"  - {pattern}\n"
        else:
            report += "  - لا توجد أنماط واضحة\n"
        report += "────────────────────\n"
    
    keyboard = [
        [InlineKeyboardButton("🔙 رجوع", callback_data=f"timeframe_1d_{symbol}")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(report, reply_markup=reply_markup)

def get_analysis_data(symbol: str, timeframe: str):
    klines = get_klines(symbol, timeframe, limit=100)
    if not klines:
        return None
    
    candles = {
        'open': [float(k[1]) for k in klines],
        'high': [float(k[2]) for k in klines],
        'low': [float(k[3]) for k in klines],
        'close': [float(k[4]) for k in klines],
        'volume': [float(k[5]) for k in klines]
    }
    
    indicators = calculate_technical_indicators(candles)
    candle_patterns = detect_candle_patterns(candles)
    trend_analysis = analyze_trend(candles, indicators, candle_patterns)
    
    return {
        'symbol': symbol,
        'timeframe': timeframe,
        'candles': candles,
        'candle_patterns': candle_patterns,
        'trend': trend_analysis['direction'],
        'trend_details': trend_analysis['details'],
        'support_resistance': calculate_support_resistance(candles),
        'volume_analysis': analyze_volume(candles),
        'indicators': indicators
    }

def analyze_trend(candles, indicators, candle_patterns):
    """
    تحليل الاتجاه باستخدام المؤشرات الفنية وأنماط الشموع مع التركيز على الإشارات الأقوى
    """
    closes = candles['close']
    highs = candles['high']
    lows = candles['low']
    volumes = candles['volume']
    
    # 1. تحليل المتوسطات المتحركة (وزن عالي)
    ma_short = sum(closes[-5:]) / 5
    ma_medium = sum(closes[-13:]) / 13
    ma_long = sum(closes[-50:]) / 50
    
    ma_bullish = ma_short > ma_medium > ma_long
    ma_bearish = ma_short < ma_medium < ma_long
    
    # 2. تحليل MACD (وزن عالي)
    macd_bullish = indicators['macd_line'] > indicators['signal_line']
    macd_strength = abs(indicators['macd_line'] - indicators['signal_line'])
    
    # 3. تحليل RSI (وزن متوسط)
    rsi = indicators['rsi']
    rsi_bullish = rsi < 30
    rsi_bearish = rsi > 70
    
    # 4. تحليل بولينجر باند (وزن متوسط)
    price = indicators['current_price']
    bb = indicators['bollinger']
    bb_bullish = price < bb['lower']
    bb_bearish = price > bb['upper']
    
    # 5. تحليل أنماط الشموع (وزن عالي إذا كانت أنماط قوية)
    strong_bullish_patterns = [p for p in candle_patterns if "صعودي قوي" in p or "hammer" in p or "bullish_engulfing" in p]
    strong_bearish_patterns = [p for p in candle_patterns if "هبوطي قوي" in p or "shooting_star" in p or "bearish_engulfing" in p]
    
    # 6. تحليل الحجم (وزن منخفض إلا إذا كان مرتفع جداً)
    volume_ratio = indicators['volume_ratio']
    high_volume = volume_ratio > 2.0
    
    # 7. تحليل Stochastic (وزن منخفض)
    stoch = indicators['stochastic']
    stoch_bullish = stoch < 20
    stoch_bearish = stoch > 80
    
    # تحديد أقوى الإشارات
    strong_bullish_signals = 0
    strong_bearish_signals = 0
    
    # إشارات صعودية قوية
    if ma_bullish: strong_bullish_signals += 1.5
    if macd_bullish and macd_strength > 0.002 * price: strong_bullish_signals += 1.5
    if rsi_bullish: strong_bullish_signals += 1
    if bb_bullish: strong_bullish_signals += 1
    if len(strong_bullish_patterns) > 0: strong_bullish_signals += len(strong_bullish_patterns) * 0.8
    if stoch_bullish: strong_bullish_signals += 0.5
    
    # إشارات هبوطية قوية
    if ma_bearish: strong_bearish_signals += 1.5
    if not macd_bullish and macd_strength > 0.002 * price: strong_bearish_signals += 1.5
    if rsi_bearish: strong_bearish_signals += 1
    if bb_bearish: strong_bearish_signals += 1
    if len(strong_bearish_patterns) > 0: strong_bearish_signals += len(strong_bearish_patterns) * 0.8
    if stoch_bearish: strong_bearish_signals += 0.5
    
    # تأثير الحجم (يعزز الاتجاه الحالي إذا كان مرتفعاً)
    if high_volume:
        if strong_bullish_signals > strong_bearish_signals:
            strong_bullish_signals *= 1.3
        elif strong_bearish_signals > strong_bullish_signals:
            strong_bearish_signals *= 1.3
    
    # تحديد الاتجاه النهائي بناء على أقوى الإشارات
    trend_difference = strong_bullish_signals - strong_bearish_signals
    
    if trend_difference >= 3:
        return {
            "direction": "صعودي قوي جداً 🟢🟢",
            "strength": trend_difference,
            "details": {
                "moving_averages": "صعودية قوية" if ma_bullish else "صعودية",
                "macd": "إشارة شراء قوية" if macd_bullish else "إشارة شراء",
                "rsi": "تشبع بيعي" if rsi_bullish else "في النطاق الطبيعي",
                "bollinger": "سعر عند النطاق السفلي (تشبع بيعي)" if bb_bullish else "سعر في النطاق الأوسط",
                "candle_patterns": "\n".join(strong_bullish_patterns) if strong_bullish_patterns else "لا توجد أنماط صعودية قوية",
                "volume": "حجم تداول مرتفع جداً" if high_volume else "حجم تداول عادي",
                "stochastic": "تشبع بيعي" if stoch_bullish else "في النطاق الطبيعي"
            }
        }
    elif trend_difference >= 1.5:
        return {
            "direction": "صعودي قوي 🟢",
            "strength": trend_difference,
            "details": {
                "moving_averages": "صعودية",
                "macd": "إشارة شراء",
                "rsi": "تشبع بيعي" if rsi_bullish else "في النطاق الطبيعي",
                "bollinger": "سعر في النطاق السفلي" if bb_bullish else "سعر في النطاق الأوسط",
                "candle_patterns": "\n".join(strong_bullish_patterns) if strong_bullish_patterns else "لا توجد أنماط صعودية قوية",
                "volume": "حجم تداول مرتفع" if high_volume else "حجم تداول عادي",
                "stochastic": "تشبع بيعي" if stoch_bullish else "في النطاق الطبيعي"
            }
        }
    elif trend_difference <= -3:
        return {
            "direction": "هبوطي قوي جداً 🔴🔴",
            "strength": trend_difference,
            "details": {
                "moving_averages": "هبوطية قوية" if ma_bearish else "هبوطية",
                "macd": "إشارة بيع قوية" if not macd_bullish else "إشارة بيع",
                "rsi": "تشبع شرائي" if rsi_bearish else "في النطاق الطبيعي",
                "bollinger": "سعر عند النطاق العلوي (تشبع شرائي)" if bb_bearish else "سعر في النطاق الأوسط",
                "candle_patterns": "\n".join(strong_bearish_patterns) if strong_bearish_patterns else "لا توجد أنماط هبوطية قوية",
                "volume": "حجم تداول مرتفع جداً" if high_volume else "حجم تداول عادي",
                "stochastic": "تشبع شرائي" if stoch_bearish else "في النطاق الطبيعي"
            }
        }
    elif trend_difference <= -1.5:
        return {
            "direction": "هبوطي قوي 🔴",
            "strength": trend_difference,
            "details": {
                "moving_averages": "هبوطية",
                "macd": "إشارة بيع",
                "rsi": "تشبع شرائي" if rsi_bearish else "في النطاق الطبيعي",
                "bollinger": "سعر في النطاق العلوي" if bb_bearish else "سعر في النطاق الأوسط",
                "candle_patterns": "\n".join(strong_bearish_patterns) if strong_bearish_patterns else "لا توجد أنماط هبوطية قوية",
                "volume": "حجم تداول مرتفع" if high_volume else "حجم تداول عادي",
                "stochastic": "تشبع شرائي" if stoch_bearish else "في النطاق الطبيعي"
            }
        }
    else:
        return {
            "direction": "محايد ⚪",
            "strength": trend_difference,
            "details": {
                "moving_averages": "غير واضحة",
                "macd": "محايد",
                "rsi": "في النطاق الطبيعي",
                "bollinger": "سعر في النطاق الأوسط",
                "candle_patterns": "لا توجد أنماط واضحة",
                "volume": "حجم تداول عادي",
                "stochastic": "في النطاق الطبيعي"
            }
        }

def detect_candle_patterns(candles):
    detected = []
    o = candles['open']
    h = candles['high']
    l = candles['low']
    c = candles['close']
    
    for name, pattern in CANDLE_PATTERNS.items():
        if pattern['condition'].__code__.co_argcount == 4:
            if pattern["condition"](o[-1], h[-1], l[-1], c[-1]):
                detected.append(f"{pattern['emoji']} {name} ({pattern['direction']})")
    
    if len(o) > 1:
        for name, pattern in CANDLE_PATTERNS.items():
            if pattern['condition'].__code__.co_argcount == 8:
                if pattern["condition"](o[-2], h[-2], l[-2], c[-2], o[-1], h[-1], l[-1], c[-1]):
                    detected.append(f"{pattern['emoji']} {name} ({pattern['direction']})")
    
    if len(o) > 2:
        for name, pattern in CANDLE_PATTERNS.items():
            if pattern['condition'].__code__.co_argcount == 12:
                if pattern["condition"](o[-3], h[-3], l[-3], c[-3], o[-2], h[-2], l[-2], c[-2], o[-1], h[-1], l[-1], c[-1]):
                    detected.append(f"{pattern['emoji']} {name} ({pattern['direction']})")
    
    return detected if detected else ["🔍 لا توجد أنماط واضحة"]

def calculate_support_resistance(candles):
    recent_lows = candles['low'][-20:]
    recent_highs = candles['high'][-20:]
    
    support = min(recent_lows)
    resistance = max(recent_highs)
    
    return {
        'support': support,
        'resistance': resistance,
        'pivot': (support + resistance + candles['close'][-1]) / 3
    }

def analyze_volume(candles):
    avg_volume = sum(candles['volume'][-20:])/20
    last_volume = candles['volume'][-1]
    
    if last_volume > avg_volume * 2:
        return "حجم عالي جداً 📈"
    elif last_volume > avg_volume * 1.5:
        return "حجم مرتفع 📈"
    elif last_volume < avg_volume * 0.5:
        return "حجم منخفض 📉"
    else:
        return "حجم طبيعي ↔️"

def calculate_technical_indicators(candles):
    closes = candles['close']
    highs = candles['high']
    lows = candles['low']
    
    macd_line, signal_line = calculate_macd(closes)
    
    return {
        'rsi': calculate_rsi(closes),
        'macd': macd_line[-1] - signal_line[-1],
        'macd_line': macd_line[-1],
        'signal_line': signal_line[-1],
        'stochastic': calculate_stochastic(highs, lows, closes),
        'bollinger': calculate_bollinger_bands(closes),
        'fibonacci': calculate_fibonacci_levels(highs, lows),
        'volume_ratio': candles['volume'][-1] / (sum(candles['volume'][-20:])/20),
        'current_price': closes[-1],
        'price_change': (closes[-1] - closes[-2]) / closes[-2] * 100,
        'macd_crossover': "صعودي" if macd_line[-1] > signal_line[-1] else "هبوطي"
    }

def calculate_rsi(prices, period=14):
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [delta if delta > 0 else 0 for delta in deltas]
    losses = [-delta if delta < 0 else 0 for delta in deltas]
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period if sum(losses[-period:]) != 0 else 0.001
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices, fast=12, slow=26, signal=9):
    def ema(data, period):
        multiplier = 2 / (period + 1)
        ema_values = [data[0]]
        for price in data[1:]:
            ema_values.append((price - ema_values[-1]) * multiplier + ema_values[-1])
        return ema_values
    
    fast_ema = ema(prices, fast)
    slow_ema = ema(prices, slow)
    macd_line = [fast_ema[i] - slow_ema[i] for i in range(len(prices))]
    signal_line = ema(macd_line, signal)
    
    return macd_line, signal_line

def calculate_stochastic(highs, lows, closes, period=14):
    k_values = []
    for i in range(len(closes)-period, len(closes)):
        highest_high = max(highs[i-period:i+1])
        lowest_low = min(lows[i-period:i+1])
        k = 100 * (closes[i] - lowest_low) / (highest_high - lowest_low) if (highest_high - lowest_low) != 0 else 50
        k_values.append(k)
    return sum(k_values) / len(k_values)

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    sma = sum(prices[-period:]) / period
    squared_diffs = [(price - sma) ** 2 for price in prices[-period:]]
    std = (sum(squared_diffs) / period) ** 0.5
    return {
        'upper': sma + std_dev * std,
        'middle': sma,
        'lower': sma - std_dev * std
    }

def calculate_fibonacci_levels(highs, lows):
    high = max(highs[-50:])
    low = min(lows[-50:])
    return {
        '23.6%': high - (high - low) * 0.236,
        '38.2%': high - (high - low) * 0.382,
        '61.8%': high - (high - low) * 0.618
    }

def calculate_price_prediction(analysis, timeframe):
    candles = analysis['candles']
    indicators = analysis['indicators']
    closes = candles['close'][-50:]  # زيادة الفترة لتحليل أفضل
    highs = candles['high'][-50:]
    lows = candles['low'][-50:]
    volumes = candles['volume'][-50:]
    
    # 1. تحليل الاتجاه باستخدام متعددة المتوسطات المتحركة
    ma_short = sum(closes[-5:]) / 5
    ma_medium = sum(closes[-13:]) / 13
    ma_long = sum(closes[-50:]) / 50
    
    # تحديد قوة الاتجاه (0.1 إلى 2.0)
    trend_strength = 0
    if ma_short > ma_medium > ma_long:
        trend_strength = 1.5 + (closes[-1] - ma_short) / ma_short * 100
    elif ma_short < ma_medium < ma_long:
        trend_strength = -1.5 + (closes[-1] - ma_short) / ma_short * 100
    
    # 2. تحليل RSI مع مناطق التشبع الدقيقة
    rsi = indicators['rsi']
    rsi_factor = 0
    if rsi < 25:
        rsi_factor = 0.5
    elif rsi < 30:
        rsi_factor = 0.3
    elif rsi > 75:
        rsi_factor = -0.5
    elif rsi > 70:
        rsi_factor = -0.3
    
    # 3. تحليل MACD عميق
    macd_strength = 0
    if indicators['macd_line'] > indicators['signal_line'] and indicators['macd'] > 0:
        macd_strength = 0.3 + min(0.2, indicators['macd'] / indicators['current_price'] * 100)
    elif indicators['macd_line'] < indicators['signal_line'] and indicators['macd'] < 0:
        macd_strength = -0.3 + max(-0.2, indicators['macd'] / indicators['current_price'] * 100)
    
    # 4. تحليل أنماط الشموع مع الأوزان
    pattern_factor = 0
    if analysis['candle_patterns']:
        for pattern in analysis['candle_patterns']:
            if "صعودي قوي" in pattern:
                pattern_factor += 0.4
            elif "صعودي" in pattern:
                pattern_factor += 0.2
            elif "هبوطي قوي" in pattern:
                pattern_factor -= 0.4
            elif "هبوطي" in pattern:
                pattern_factor -= 0.2
    
    # 5. تحليل الحجم مع الاتجاه
    volume_factor = 0
    avg_volume = sum(volumes[-20:]) / 20
    if volumes[-1] > avg_volume * 2:
        volume_factor = 0.3 if trend_strength > 0 else -0.3
    
    # 6. تحليل بولينجر باند
    bb_factor = 0
    bb = indicators['bollinger']
    price = indicators['current_price']
    if price < bb['lower']:
        bb_factor = 0.4
    elif price > bb['upper']:
        bb_factor = -0.4
    elif price > bb['middle']:
        bb_factor = 0.1
    else:
        bb_factor = -0.1
    
    # 7. دمج العوامل مع أوزان ديناميكية
    base_prediction = price * (1 + 
        (trend_strength * 0.015) +
        (rsi_factor * 0.4) +
        (macd_strength * 0.3) +
        (pattern_factor * 0.25) +
        (volume_factor * 0.2) +
        (bb_factor * 0.2)
    )
    
    # 8. ضبط حسب المدى الزمني
    timeframe_factors = {
        "15m": 0.005,
        "30m": 0.008,
        "1h": 0.012,
        "4h": 0.018,
        "1d": 0.025,
        "1w": 0.04
    }
    timeframe_factor = timeframe_factors.get(timeframe, 0.01)
    
    # 9. تطبيق حدود الدعم والمقاومة الذكية
    support = analysis['support_resistance']['support']
    resistance = analysis['support_resistance']['resistance']
    
    # حساب القنوات السعرية
    price_channel = max(highs[-20:]) - min(lows[-20:])
    dynamic_support = support - price_channel * 0.05
    dynamic_resistance = resistance + price_channel * 0.05
    
    adjusted_prediction = max(dynamic_support, min(dynamic_resistance, 
                                price + (base_prediction - price) * timeframe_factor))
    
    # 10. حساب ثقة التوقع (0-100%) بناء على توافق المؤشرات
    confidence_factors = [
        abs(trend_strength) * 25,
        (100 - abs(rsi - 50)) * 0.5,
        abs(macd_strength) * 30,
        abs(pattern_factor) * 20,
        min(100, indicators['volume_ratio'] * 20)
    ]
    
    confidence = sum(confidence_factors) / len(confidence_factors)
    confidence = max(10, min(95, confidence))
    
    return {
        "predicted_price": round(adjusted_prediction, 6 if price < 1 else 4),
        "confidence": round(confidence, 1),
        "trend": "صعودي قوي" if trend_strength >= 1.5 else "صعودي" if trend_strength > 0.5 
                else "هبوطي قوي" if trend_strength <= -1.5 else "هبوطي" if trend_strength < -0.5 
                else "محايد",
        "rsi_status": "تشبع بيعي قوي" if rsi < 25 else "تشبع بيعي" if rsi < 30 
                     else "تشبع شرائي قوي" if rsi > 75 else "تشبع شرائي" if rsi > 70 
                     else "محايد",
        "macd_status": "شراء قوي" if macd_strength > 0.4 else "شراء" if macd_strength > 0.2
                      else "بيع قوي" if macd_strength < -0.4 else "بيع" if macd_strength < -0.2
                      else "محايد"
    }

def generate_recommendation(analysis):
    """
    توليد توصية بناء على أقوى الإشارات من جميع المؤشرات
    """
    indicators = analysis['indicators']
    trend = analysis['trend']
    candle_patterns = analysis['candle_patterns']
    
    # تحديد أقوى الإشارات
    strong_signals = {
        'bullish': 0,
        'bearish': 0
    }
    
    # 1. تحليل الاتجاه العام (وزن عالي)
    if "صعودي قوي جداً" in trend:
        strong_signals['bullish'] += 2.5
    elif "صعودي قوي" in trend:
        strong_signals['bullish'] += 2.0
    elif "هبوطي قوي جداً" in trend:
        strong_signals['bearish'] += 2.5
    elif "هبوطي قوي" in trend:
        strong_signals['bearish'] += 2.0
    
    # 2. تحليل أنماط الشموع (وزن عالي للأنماط القوية)
    strong_bullish_patterns = [p for p in candle_patterns if "صعودي قوي" in p or "hammer" in p or "bullish_engulfing" in p]
    strong_bearish_patterns = [p for p in candle_patterns if "هبوطي قوي" in p or "shooting_star" in p or "bearish_engulfing" in p]
    
    strong_signals['bullish'] += len(strong_bullish_patterns) * 1.2
    strong_signals['bearish'] += len(strong_bearish_patterns) * 1.2
    
    # 3. تحليل RSI (وزن متوسط)
    rsi = indicators['rsi']
    if rsi < 30:
        strong_signals['bullish'] += 1.5
    elif rsi > 70:
        strong_signals['bearish'] += 1.5
    
    # 4. تحليل MACD (وزن عالي)
    if indicators['macd_line'] > indicators['signal_line']:
        macd_strength = indicators['macd_line'] - indicators['signal_line']
        strong_signals['bullish'] += min(2.0, macd_strength / indicators['current_price'] * 10000)
    else:
        macd_strength = indicators['signal_line'] - indicators['macd_line']
        strong_signals['bearish'] += min(2.0, macd_strength / indicators['current_price'] * 10000)
    
    # 5. تحليل بولينجر باند (وزن متوسط)
    price = indicators['current_price']
    bb = indicators['bollinger']
    if price < bb['lower']:
        strong_signals['bullish'] += 1.5
    elif price > bb['upper']:
        strong_signals['bearish'] += 1.5
    
    # 6. تحليل Stochastic (وزن منخفض)
    stoch = indicators['stochastic']
    if stoch < 20:
        strong_signals['bullish'] += 0.8
    elif stoch > 80:
        strong_signals['bearish'] += 0.8
    
    # 7. تحليل الحجم (يعزز الاتجاه الحالي إذا كان مرتفعاً)
    if indicators['volume_ratio'] > 2.0:
        if strong_signals['bullish'] > strong_signals['bearish']:
            strong_signals['bullish'] *= 1.3
        elif strong_signals['bearish'] > strong_signals['bullish']:
            strong_signals['bearish'] *= 1.3
    
    # تحديد التوصية النهائية بناء على أقوى الإشارات
    signal_diff = strong_signals['bullish'] - strong_signals['bearish']
    
    if signal_diff >= 5:
        return {
            "decision": "شراء قوي جداً 🟢🟢",
            "reason": "إشارات شراء قوية من معظم المؤشرات وأنماط الشموع"
        }
    elif signal_diff >= 3:
        return {
            "decision": "شراء قوي 🟢",
            "reason": "إشارات شراء قوية من عدة مؤشرات"
        }
    elif signal_diff >= 1.5:
        return {
            "decision": "شراء 🟢",
            "reason": "إشارات شراء من بعض المؤشرات"
        }
    elif signal_diff <= -5:
        return {
            "decision": "بيع قوي جداً 🔴🔴",
            "reason": "إشارات بيع قوية من معظم المؤشرات وأنماط الشموع"
        }
    elif signal_diff <= -3:
        return {
            "decision": "بيع قوي 🔴",
            "reason": "إشارات بيع قوية من عدة مؤشرات"
        }
    elif signal_diff <= -1.5:
        return {
            "decision": "بيع 🔴",
            "reason": "إشارات بيع من بعض المؤشرات"
        }
    else:
        return {
            "decision": "محايد ⚪",
            "reason": "إشارات متضاربة، يفضل الانتظار لمزيد من التأكيد"
        }

def generate_analysis_report(analysis):
    indicators = analysis['indicators']
    sr = analysis['support_resistance']
    recommendation = generate_recommendation(analysis)
    prediction = calculate_price_prediction(analysis, analysis['timeframe'])
    
    report = f"""
📊 تحليل {analysis['symbol']} - {analysis['timeframe']}
────────────────────
📈 تحليل الاتجاه:
- الاتجاه: {analysis['trend']}
- المتوسطات المتحركة: {analysis['trend_details']['moving_averages']}
- مؤشر MACD: {analysis['trend_details']['macd']}
- مؤشر RSI: {analysis['trend_details']['rsi']}
- أنماط الشموع:
"""
    if analysis['candle_patterns'] and analysis['candle_patterns'][0] != "🔍 لا توجد أنماط واضحة":
        for pattern in analysis['candle_patterns']:
            report += f"  - {pattern}\n"
    else:
        report += "  - لا توجد أنماط واضحة\n"
    
    report += f"""- الحجم: {analysis['trend_details']['volume']}
────────────────────
💰 السعر الحالي: {indicators['current_price']:.4f}
🎯 السعر المتوقع: {prediction['predicted_price']:.4f} (ثقة: {prediction['confidence']}%)
────────────────────
📌 المؤشرات الفنية:
- RSI: {indicators['rsi']:.2f}
- MACD: {indicators['macd']:.4f} (الخط: {indicators['macd_line']:.4f}, الإشارة: {indicators['signal_line']:.4f})
- Stochastic: {indicators['stochastic']:.2f}
- بولينجر باند:
  العلوي: {indicators['bollinger']['upper']:.4f}
  الأوسط: {indicators['bollinger']['middle']:.4f}
  السفلي: {indicators['bollinger']['lower']:.4f}
────────────────────
📌 المستويات الرئيسية:
- الدعم: {sr['support']:.4f}
- المقاومة: {sr['resistance']:.4f}
- النقطة المحورية: {sr['pivot']:.4f}
────────────────────
💡 التوصية: {recommendation['decision']}
🔍 السبب: {recommendation['reason']}
"""
    return report

def get_klines(symbol, interval, limit=100):
    try:
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        response = requests.get(f"{BINANCE_API_URL}/klines", params=params, timeout=10)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching klines: {e}")
        return None

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ البوت يعمل بنجاح...")
    application.run_polling()

if __name__ == '__main__':
    main()