import streamlit as st
import streamlit.components.v1 as components
import urllib.request
from datetime import datetime
from supabase import create_client, Client
import base64

st.set_page_config(page_title="أكاديمية كابتن محسن", page_icon="⚽", layout="wide")

# ============================================================
# 🔥 إعدادات Supabase الخاصة بك
# ============================================================
SUPABASE_URL = "https://sqbcijzmwswrebucnipx.supabase.co"
SUPABASE_KEY = "sb_publishable_hByTqR-E6255Nh2_xrxMyA_K4Y9vyDS"
TABLE_NAME = "coach_data"

ADMIN_PASSWORD = "mohsen123"

COACH_PHOTO_URL = "https://i.postimg.cc/1XBwfr7M/Screenshot-20261017-210359-Google.jpg"
TRAINER_PHOTO_URL = "https://i.postimg.cc/1XBwfr7M/Screenshot-20261017-210359-Google.jpg"
AUDIO_URL = "https://github.com/bebo-12712/ya-wala/raw/refs/heads/main/WhatsApp%20Audio%202026-10-23%20at%208.49.32%20PM.mpeg"


# ============================================================
# الاتصال بـ Supabase
# ============================================================
@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_supabase()


# ============================================================
# دوال قاعدة البيانات
# ============================================================
def get_default_data():
    return {
        "coach": {"name": "كابتن محسن", "photo": COACH_PHOTO_URL},
        "trainer": {"name": "المدرب المساعد", "photo": TRAINER_PHOTO_URL},
        "schedule": [
            {"day": "الإثنين", "time": "6:00 مساءً - 8:00 مساءً", "place": "الملعب الرئيسي"},
            {"day": "الأربعاء", "time": "5:00 مساءً - 7:00 مساءً", "place": "ملعب التدريب ب"},
        ],
        "users": {},
        "last_update_msg": "",
        "last_update_time": ""
    }


def load_data():
    try:
        response = supabase.table(TABLE_NAME).select("*").eq("id", 1).execute()
        if response.data:
            return response.data[0]["content"]
        else:
            default_data = get_default_data()
            supabase.table(TABLE_NAME).insert({"id": 1, "content": default_data}).execute()
            return default_data
    except Exception as e:
        st.error(f"مشكلة في الاتصال بقاعدة البيانات: {e}")
        return get_default_data()


def save_data(data):
    try:
        supabase.table(TABLE_NAME).update({"content": data}).eq("id", 1).execute()
    except Exception as e:
        st.error(f"فشل حفظ البيانات: {e}")


if "data" not in st.session_state:
    st.session_state.data = load_data()
if "user" not in st.session_state:
    st.session_state.user = None
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "editing_index" not in st.session_state:
    st.session_state.editing_index = None


# ============================================================
# دوال مساعدة
# ============================================================
def image_to_base64(uploaded_file):
    """تحويل الصورة المرفوعة إلى نص Base64 عشان تتحفظ في الداتابيز"""
    bytes_data = uploaded_file.getvalue()
    base64_str = base64.b64encode(bytes_data).decode()
    return f"data:image/jpeg;base64,{base64_str}"


def bg_image_css(src):
    if not src: return
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(15,23,42,0.85), rgba(15,23,42,0.95)), url("{src}");
        background-size: contain; background-repeat: no-repeat;
        background-position: center center; background-attachment: fixed;
        background-color: #0f172a; direction: rtl;
    }}
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# STYLING
# ============================================================
st.markdown("""
<style>
    .stApp { background-color: #0f172a; direction: rtl; text-align: right; }
    h1, h2, h3 { color: #38bdf8 !important; }
    .plan-card { background: rgba(30,41,59,0.9); border-right: 5px solid #38bdf8; border-left: none; border-radius: 12px; padding: 18px 22px; margin-bottom: 14px; }
    .plan-card .day { color: #38bdf8; font-weight: 700; font-size: 1.2rem; }
    .plan-card .meta { color: #cbd5e1; font-size: 0.95rem; }
    .big-title { font-size: 2.2rem; font-weight: 800; color: #38bdf8; }
    .sub { color: #94a3b8; }
    .profile-pic { width: 150px; height: 150px; border-radius: 50%; object-fit: cover; border: 4px solid #38bdf8; margin-bottom: 10px; }
    .wa-btn { display: inline-block; background-color: #25D366; color: white !important; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 10px; text-align: center; width: 100%; }
    .wa-btn:hover { background-color: #128C7E; }
    .stTextInput > div > div > input { direction: rtl; }
    .alert-box { background-color: #ef4444; color: white; padding: 15px; border-radius: 8px; font-weight: bold; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
</style>
""", unsafe_allow_html=True)


# ============================================================
# AUTH
# ============================================================
def show_auth_screen():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<div class='big-title'>⚽ كابتن محسن</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub'>سجل دخولك أو أنشئ حساباً جديداً للمتابعة</div><br>", unsafe_allow_html=True)

        role = st.radio("أنا...", ["لاعب", "أدمن (مسؤول)"], horizontal=True)
        tab_in, tab_up = st.tabs(["تسجيل الدخول", "حساب جديد"])

        with tab_in:
            email = st.text_input("البريد الإلكتروني", key="in_email")
            pw = st.text_input("كلمة المرور", type="password", key="in_pw")
            if st.button("دخول", type="primary", use_container_width=True):
                if role == "أدمن (مسؤول)":
                    if pw == ADMIN_PASSWORD:
                        st.session_state.admin_logged = True
                        st.rerun()
                    else:
                        st.error("كلمة مرور الأدمن غير صحيحة.")
                else:
                    u = st.session_state.data["users"].get(email.lower())
                    if not u:
                        st.error("لا يوجد حساب بهذا البريد. يرجى إنشاء حساب.")
                    elif u["password"] != pw:
                        st.error("كلمة المرور غير صحيحة.")
                    else:
                        st.session_state.user = {"email": email.lower(), **u}
                        st.rerun()

        with tab_up:
            n = st.text_input("الاسم بالكامل", key="up_n")
            e = st.text_input("البريد الإلكتروني", key="up_e")
            p = st.text_input("كلمة المرور", type="password", key="up_p")
            if st.button("إنشاء الحساب", type="primary", use_container_width=True):
                if not (n and e and p):
                    st.error("يرجى ملء جميع الحقول.")
                elif e.lower() in st.session_state.data["users"]:
                    st.error("هذا البريد مسجل بالفعل. سجل دخولك.")
                else:
                    st.session_state.data["users"][e.lower()] = {
                        "name": n, "password": p,
                        "phone": "", "age": "", "foot": "",
                        "info_complete": False, "profile_pic": ""
                    }
                    save_data(st.session_state.data)
                    st.session_state.user = {"email": e.lower(), **st.session_state.data["users"][e.lower()]}
                    st.rerun()


# ============================================================
# PERSONAL INFO
# ============================================================
def show_info_screen():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<div class='big-title'>📋 بياناتك الشخصية</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub'>أخبر الكابتن محسن بمعلومات عنك</div><br>", unsafe_allow_html=True)

        phone = st.text_input("رقم الهاتف")
        age = st.number_input("العمر", 5, 99, 16)
        foot = st.radio("القدم المسيطرة", ["يمين", "شمال"], horizontal=True)

        if st.button("متابعة إلى التدريب ←", type="primary", use_container_width=True):
            em = st.session_state.user["email"]
            u = st.session_state.data["users"][em]
            u.update({"phone": phone.strip(), "age": str(age), "foot": foot, "info_complete": True})
            st.session_state.user = {"email": em, **u}
            save_data(st.session_state.data)
            st.rerun()


# ============================================================
# DASHBOARD (شاشة اللاعب)
# ============================================================
def show_dashboard():
    data = st.session_state.data
    bg_image_css(data["coach"]["photo"])

    if data.get("last_update_msg"):
        st.markdown(f"""
        <div class="alert-box">
            📢 {data['last_update_msg']} <br>
            <span style="font-size: 0.8rem; font-weight: normal;">(بتاريخ: {data['last_update_time']})</span>
        </div>
        """, unsafe_allow_html=True)

    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown("<div class='big-title'>خطط التدريب</div>", unsafe_allow_html=True)
    with c2:
        if st.button("تسجيل خروج", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    st.markdown("---")

    # --- قسم البروفايل ---
    u = st.session_state.user
    col_pic, col_info, col_wa = st.columns([1.5, 2, 2])

    with col_pic:
        if u.get("profile_pic"):
            st.markdown(f'<img src="{u["profile_pic"]}" class="profile-pic">', unsafe_allow_html=True)
        else:
            st.markdown(f'<img src="https://www.w3schools.com/howto/img_avatar.png" class="profile-pic">',
                        unsafe_allow_html=True)

    with col_info:
        st.markdown(f"### {u['name']}")
        st.markdown(f"<div class='sub'>العمر: {u['age']} | القدم المسيطرة: {u['foot']}</div><br>",
                    unsafe_allow_html=True)

        # رفع الصورة من الجهاز
        uploaded_file = st.file_uploader("📷 غير صورتك الشخصية", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            if st.button("حفظ الصورة الجديدة", type="primary"):
                new_pic_b64 = image_to_base64(uploaded_file)
                st.session_state.data["users"][u["email"]]["profile_pic"] = new_pic_b64
                st.session_state.user["profile_pic"] = new_pic_b64
                save_data(st.session_state.data)
                st.success("تم حفظ صورتك بنجاح!")
                st.rerun()
    with col_wa:
        st.markdown("### محتاج مساعدة؟")
        st.markdown("<div class='sub'>تواصل مع الكابتن محسن مباشرة على تليجرام</div>", unsafe_allow_html=True)

        # كلمة start دي هي اللي بتخلي الشات يفتح فوراً
        telegram_link = "https://t.me/Coashmaher1bot?start=hello"

        st.markdown(
            f'<a href="{telegram_link}" target="_blank" class="wa-btn" style="background-color: #0088cc;">✈️ تواصل عبر تليجرام</a>',
            unsafe_allow_html=True)
    st.subheader("📅 الخطط القادمة")

    if not data["schedule"]:
        st.info("لا توجد خطط تدريبية حالياً.")
        return

    for i, s in enumerate(data["schedule"]):
        st.markdown(f"""
        <div class="plan-card">
            <div class="day">{s['day']}</div>
            <div class="meta">🕒 {s['time']}<br>📍 {s['place']}</div>
        </div>""", unsafe_allow_html=True)

        html_button = f"""
            <audio id="myAudio_{i}" src="{AUDIO_URL}"></audio>
            <button onclick="playAndBook('{i}')" style="
                background-color: #38bdf8; color: #0f172a; border: none; 
                padding: 10px 20px; border-radius: 8px; font-weight: bold; 
                font-size: 16px; cursor: pointer; width: 100%; margin-bottom: 20px;">
                احجز في تدريب {s['day']}
            </button>
            <script>
            function playAndBook(id) {{
                var audio = document.getElementById('myAudio_' + id);
                audio.play();
                alert('تم الحجز بنجاح! استعد للتمرين 💪');
            }}
            </script>
        """
        components.html(html_button, height=80)


# ============================================================
# ADMIN (لوحة التحكم)
# ============================================================
def show_admin():
    data = st.session_state.data
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown("<div class='big-title'>🔒 لوحة تحكم الأدمن</div>", unsafe_allow_html=True)
    with c2:
        if st.button("تسجيل خروج", use_container_width=True):
            st.session_state.admin_logged = False
            st.rerun()

    st.subheader("📢 إرسال تنبيه للاعبين")
    with st.form("alert_form"):
        alert_msg = st.text_input("نص التنبيه (مثلاً: تم تغيير موعد الإثنين!)")
        if st.form_submit_button("إرسال التنبيه", type="primary"):
            data["last_update_msg"] = alert_msg
            data["last_update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_data(data)
            st.success("تم إرسال التنبيه للمتدربين!")
            st.rerun()

    if data.get("last_update_msg"):
        if st.button("🗑️ مسح التنبيه الحالي"):
            data["last_update_msg"] = ""
            data["last_update_time"] = ""
            save_data(data)
            st.rerun()

    st.divider()
    st.subheader("➕ إضافة خطة تدريب جديدة")
    c1, c2, c3 = st.columns(3)
    with c1:
        day = st.selectbox("اليوم", ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"])
    with c2:
        time = st.text_input("الوقت", placeholder="6:00 مساءً - 8:00 مساءً")
    with c3:
        place = st.text_input("المكان", placeholder="الملعب الرئيسي")
    if st.button("إضافة الخطة", type="primary"):
        if time.strip() and place.strip():
            data["schedule"].append({"day": day, "time": time.strip(), "place": place.strip()})
            save_data(data)
            st.rerun()
        else:
            st.error("يرجى إدخال الوقت والمكان.")

    st.divider()
    st.subheader("📝 إدارة وتعديل الخطط")
    if not data["schedule"]:
        st.info("لا توجد خطط حالياً.")

    for i, s in enumerate(data["schedule"]):
        if st.session_state.editing_index == i:
            st.markdown(f"**تعديل خطة: {s['day']}**")
            ec1, ec2, ec3 = st.columns(3)
            days_list = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
            try:
                day_idx = days_list.index(s["day"])
            except:
                day_idx = 0

            with ec1:
                new_day = st.selectbox("اليوم", days_list, index=day_idx, key=f"edit_day_{i}")
            with ec2:
                new_time = st.text_input("الوقت", value=s["time"], key=f"edit_time_{i}")
            with ec3:
                new_place = st.text_input("المكان", value=s["place"], key=f"edit_place_{i}")

            btn1, btn2, _ = st.columns([1, 1, 3])
            with btn1:
                if st.button("حفظ التعديلات", type="primary", key=f"save_edit_{i}"):
                    data["schedule"][i] = {"day": new_day, "time": new_time.strip(), "place": new_place.strip()}
                    save_data(data)
                    st.session_state.editing_index = None
                    st.rerun()
            with btn2:
                if st.button("إلغاء", key=f"cancel_edit_{i}"):
                    st.session_state.editing_index = None
                    st.rerun()
            st.divider()
        else:
            cc1, cc2, cc3 = st.columns([4, 1, 1])
            with cc1:
                st.markdown(f"**{s['day']}** — {s['time']} — {s['place']}")
            with cc2:
                if st.button("تعديل ✏️", key=f"edit_btn_{i}"):
                    st.session_state.editing_index = i
                    st.rerun()
            with cc3:
                if st.button("حذف 🗑️", key=f"del_{i}"):
                    data["schedule"].pop(i)
                    save_data(data)
                    st.session_state.editing_index = None
                    st.rerun()


# ============================================================
# ROUTER
# ============================================================
if st.session_state.admin_logged:
    show_admin()
elif st.session_state.user is None:
    show_auth_screen()
elif not st.session_state.user.get("info_complete"):
    show_info_screen()
else:
    show_dashboard()