import streamlit as st
import pandas as pd
from PIL import Image
import os
import re
import base64
import time

# --- إعدادات الصفحة (يجب أن تكون أول أمر) ---
st.set_page_config(
    page_title="ديوان عائلة الأسطل الرسمي",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 1. الإعدادات والتحميل (Backend Logic)
# ==============================================================================

@st.cache_data
def load_data():
    """تحميل بيانات العائلة للبحث"""
    df = None
    
    # قائمة بأسماء الملفات المحتملة (للتعامل مع أي ملف قمت برفعه)
    possible_files = [
        "data.xlsx", "data.csv",
        "عائلة الاسطل20.11.2025.xlsx - ورقة1.csv",
        "alastal family.xlsx - ورقة1.csv"
    ]
    
    file_path = ""
    for name in possible_files:
        if os.path.exists(name):
            file_path = name
            break
            
    if not file_path: return None

    try:
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path, engine='openpyxl', header=0)
        else:
            encodings = ['utf-8', 'utf-8-sig', 'windows-1256', 'iso-8859-6']
            for enc in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=enc, on_bad_lines='skip', engine='python', header=0)
                    break
                except: continue
        
        if df is None: return None
        
        # تنظيف وتوحيد البيانات
        df.columns = df.columns.astype(str).str.replace('\n', ' ').str.strip()
        
        # خريطة لتوحيد أسماء الأعمدة المختلفة
        col_map = {
            "رقم الهوية": ["رقم الهوية", "الهوية"],
            "الاسم": ["الاسم", "الاسم الرباعي"],
            "رقم الهاتف": ["رقم الهاتف", "رقم الموبايل", "الجوال"],
            "الحالة الاجتماعية": ["الحالة الاجتماعية"],
            "عدد الافراد": ["عدد افراد الاسرة", "عدد الافراد"],
            "هوية الزوجة": ["هوية الزوجة", "رقم هوية الزوجة"],
            "اسم الزوجة": ["اسم الزوجة"]
        }
        
        final_cols = {}
        for key, candidates in col_map.items():
            for cand in candidates:
                if cand in df.columns:
                    final_cols[cand] = key
                    break
        
        df = df.rename(columns=final_cols)
        # التأكد من وجود عمود الهوية وتنظيفه
        if 'رقم الهوية' in df.columns:
            df['رقم الهوية'] = df['رقم الهوية'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            
        return df
    except: return None

df = load_data()

def get_image_base64(path):
    """تحويل الشعار لـ Base64 للخلفية"""
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except: return ""
    return ""

logo_b64 = get_image_base64("logo.jpg") # يرجى التأكد من وجود صورة logo.jpg

# ==============================================================================
# 2. التصميم المتقدم (Advanced CSS Styles)
# ==============================================================================

# خلفية متدرجة ملكية (أخضر وذهبي) مع الشعار الشفاف
css_background = ""
if logo_b64:
    css_background = f"""
        .stApp {{
            background-image: linear-gradient(rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.92)), 
                              url('data:image/jpeg;base64,{logo_b64}');
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}
    """
else:
    css_background = ".stApp { background-color: #f9f9f9; }"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');
    
    /* الأساسيات */
    {css_background}
    * {{ font-family: 'Cairo', sans-serif; }}
    .main {{ direction: rtl; }}
    .block-container {{ padding-top: 0rem; padding-bottom: 4rem; max-width: 100%; }}
    
    /* إخفاء عناصر Streamlit */
    #MainMenu, footer, header, .stDecoration {{ visibility: hidden; }}
    
    /* === الهيدر (Header) === */
    .custom-header {{
        background: linear-gradient(90deg, #004d00 0%, #006400 100%);
        padding: 15px 30px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 9999;
        border-bottom: 3px solid #c5a059;
    }}
    
    /* === قسم البطل (Hero) === */
    .hero-section {{
        text-align: center;
        padding: 80px 20px;
        background: linear-gradient(135deg, #004d00 0%, #002b00 100%);
        color: white;
        border-bottom-left-radius: 50px;
        border-bottom-right-radius: 50px;
        margin-bottom: 50px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
    }}
    .hero-section::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23c5a059' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    }}
    
    /* === العناوين === */
    .section-header {{
        text-align: center;
        margin: 60px 0 40px 0;
    }}
    .section-header h2 {{
        color: #004d00;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 10px;
    }}
    .section-header .line {{
        width: 80px;
        height: 4px;
        background: #c5a059;
        margin: 0 auto;
        border-radius: 2px;
    }}
    
    /* === البطاقات (Cards) === */
    .news-card {{
        background: white;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        border: 1px solid #eee;
        transition: transform 0.3s;
        height: 100%;
    }}
    .news-card:hover {{ transform: translateY(-10px); box-shadow: 0 15px 30px rgba(0,0,0,0.1); border-bottom: 5px solid #c5a059; }}
    .news-img {{ height: 200px; background-color: #e0e0e0; background-size: cover; background-position: center; }}
    .news-content {{ padding: 20px; }}
    .news-tag {{ background: #e8f5e9; color: #004d00; padding: 3px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }}
    
    /* === زر البحث المخصص === */
    .stButton button {{
        background: #c5a059 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        box-shadow: 0 4px 10px rgba(197, 160, 89, 0.3) !important;
        width: 100%;
    }}
    .stButton button:hover {{ background: #b08d4d !important; transform: scale(1.02); }}
    
    /* === الفوتر === */
    .footer {{
        background: #1a1a1a;
        color: #ccc;
        padding: 40px 20px;
        text-align: center;
        margin-top: 80px;
        border-top: 5px solid #004d00;
    }}
    
    /* === تنسيق التنقل === */
    .nav-btn-container {{ display: flex; justify-content: center; gap: 20px; margin-bottom: 20px; }}
    
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. الهيكل والتنقل (Navigation Logic)
# ==============================================================================

if 'active_page' not in st.session_state:
    st.session_state.active_page = 'home'

def navigate_to(page):
    st.session_state.active_page = page

# --- الشريط العلوي (Header) ---
st.markdown(f"""
<div class="custom-header">
    <div style="font-size:1.5rem; font-weight:900;">ديوان عائلة الأسطل</div>
    <div style="font-size:0.9rem; opacity:0.9;">الأصالة • التاريخ • المستقبل</div>
</div>
""", unsafe_allow_html=True)

# أزرار التنقل (كأزرار Streamlit لسهولة التحكم)
col_n1, col_n2, col_n3, col_n4 = st.columns([1, 1, 1, 3])
with col_n4: st.write("") # مسافة فارغة
with col_n3: 
    if st.button("🏠 الرئيسية", use_container_width=True): navigate_to('home')
with col_n2: 
    if st.button("🔍 الخدمات الإلكترونية", use_container_width=True): navigate_to('services')
with col_n1: 
    if st.button("📜 أرشيف العائلة", use_container_width=True): navigate_to('archive')

# ==============================================================================
# 4. المحتوى (Content Pages)
# ==============================================================================

# --- الصفحة الرئيسية (Home) ---
if st.session_state.active_page == 'home':
    
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <h1 style="margin-bottom: 15px;">بوابة عائلة الأسطل الرسمية</h1>
        <p style="font-size: 1.2rem; max-width: 600px; margin: 0 auto;">
        المنصة الجامعة لتوثيق تاريخنا العريق، وتعزيز أواصر المحبة والتواصل بين جميع أفراد العائلة في الداخل والمهجر.
        </p>
        <br>
    </div>
    """, unsafe_allow_html=True)
    
    # قسم البحث السريع (Call to Action)
    st.markdown("""
    <div style="background: white; padding: 40px; border-radius: 20px; box-shadow: 0 15px 40px rgba(0,0,0,0.1); max-width: 800px; margin: -100px auto 50px auto; position: relative; border-top: 5px solid #c5a059;">
        <h3 style="text-align:center; color:#004d00; margin-bottom:20px;">🔍 الوصول السريع لبيانات الأفراد</h3>
        <p style="text-align:center; color:#666; margin-bottom:20px;">خدمة حصرية لأبناء العائلة للتحقق من البيانات وتحديثها</p>
    </div>
    """, unsafe_allow_html=True)
    
    # وضع زر البحث داخل Streamlit Column ليكون تفاعلياً
    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c2:
        if st.button("اضغط هنا للدخول إلى خدمة الاستعلام", use_container_width=True):
            navigate_to('services')
            st.rerun()

    # قسم آخر الأخبار (News Grid)
    st.markdown("""
    <div class="section-header">
        <h2>أحدث أخبار وفعاليات العائلة</h2>
        <div class="line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="news-card">
            <div class="news-img" style="background-image: url('https://via.placeholder.com/400x250/004d00/ffffff?text=مجلس+العائلة');"></div>
            <div class="news-content">
                <span class="news-tag">أخبار المجلس</span>
                <h4 style="color:#004d00; margin:10px 0;">اجتماع الجمعية العمومية السنوي</h4>
                <p style="color:#666; font-size:0.9rem;">ناقش المجلس في اجتماعه الأخير سبل تطوير صندوق التكافل ومشاريع العائلة المستقبلية.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="news-card">
            <div class="news-img" style="background-image: url('https://via.placeholder.com/400x250/c5a059/ffffff?text=تكريم+المتفوقين');"></div>
            <div class="news-content">
                <span class="news-tag">تفوق ونجاح</span>
                <h4 style="color:#004d00; margin:10px 0;">حفل تكريم أوائل الطلبة 2025</h4>
                <p style="color:#666; font-size:0.9rem;">تتشرف العائلة بدعوتكم لحضور الحفل السنوي لتكريم كوكبة من أبنائنا المتفوقين في الثانوية العامة.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="news-card">
            <div class="news-img" style="background-image: url('https://via.placeholder.com/400x250/333/ffffff?text=زيارات+اجتماعية');"></div>
            <div class="news-content">
                <span class="news-tag">اجتماعيات</span>
                <h4 style="color:#004d00; margin:10px 0;">وفد العائلة يزور حجاج بيت الله</h4>
                <p style="color:#666; font-size:0.9rem;">نظم مجلس العائلة سلسلة زيارات لتهنئة حجاج العائلة الكرام بمناسبة عودتهم سالمين.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # قسم شخصيات (Featured Person)
    st.markdown("""
    <div class="section-header">
        <h2>شخصيات في ذاكرة العائلة</h2>
        <div class="line"></div>
    </div>
    <div style="background: white; padding: 40px; border-radius: 20px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); display: flex; gap: 30px; align-items: center; max-width: 900px; margin: 0 auto; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 200px;">
            <img src="https://via.placeholder.com/300x350?text=القاضي+أحمد+الأسطل" style="width:100%; border-radius: 15px; border: 5px solid #c5a059;">
        </div>
        <div style="flex: 2;">
            <h3 style="color: #004d00; font-size: 1.8rem;">القاضي أحمد علي الأسطل (رحمه الله)</h3>
            <p style="font-size: 1.1rem; line-height: 1.8; color: #555;">
                علم من أعلام فلسطين وركن ركين من أركان العائلة. شغل منصب قاضي المحكمة الشرعية، وكان له باع طويل في إصلاح ذات البين ونشر العلم. 
                يعتبر من المؤسسين الأوائل الذين وضعوا اللبنات الأولى للعمل العائلي المنظم. ترك إرثاً من الحكمة والمواقف النبيلة التي لا تزال نبراساً للأجيال.
            </p>
            <br>
            <a href="#" style="color: #c5a059; font-weight: bold; text-decoration: none;">اقرأ المزيد عن سيرته ←</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


# --- صفحة الخدمات (Services / Search) ---
elif st.session_state.active_page == 'services':
    
    st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <h2 style="color: #004d00;">خدمة الاستعلام عن بيانات الأفراد</h2>
        <p style="color: #666;">قاعدة بيانات شاملة ومحدثة لتوثيق شجرة العائلة</p>
        <div style="width: 60px; height: 3px; background: #c5a059; margin: 20px auto;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    col_main, col_side = st.columns([2, 1])
    
    with col_side:
        st.info("""
        **تعليمات الاستخدام:**
        1. أدخل رقم الهوية (9 خانات) في الحقل المخصص.
        2. اضغط على زر "بحث".
        3. تأكد من صحة بياناتك وتواصل معنا للتحديث.
        """)
        if df is None:
            st.error("⚠️ تنبيه: جاري تحديث قاعدة البيانات، يرجى المحاولة لاحقاً.")
            
    with col_main:
        # نموذج البحث
        search_id = st.text_input("رقم الهوية", placeholder="أدخل رقم الهوية هنا...", max_chars=9).strip()
        
        if st.button("بحث في السجل المدني للعائلة", use_container_width=True):
            if df is not None and search_id:
                if not re.fullmatch(r'\d+', search_id) or len(search_id) != 9:
                    st.warning("⚠️ يرجى إدخال رقم هوية صحيح مكون من 9 أرقام.")
                else:
                    # البحث
                    res = df[df['رقم الهوية'] == search_id]
                    if not res.empty:
                        row = res.iloc[0]
                        st.balloons() # تأثير احتفالي عند العثور
                        # بطاقة النتيجة
                        st.markdown(f"""
                        <div style="background: white; border: 2px solid #004d00; border-radius: 15px; padding: 30px; margin-top: 20px; position: relative;">
                            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 8px; background: #c5a059;"></div>
                            <h3 style="color: #004d00; text-align: center; margin-bottom: 25px;">بطاقة تعريف فردية</h3>
                            
                            <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 15px; font-size: 1.1rem;">
                                <div style="font-weight: bold; color: #666;">الاسم الكامل:</div>
                                <div style="color: #000; font-weight: 700;">{row.get('الاسم', '-')}</div>
                                
                                <div style="border-bottom: 1px dashed #eee; grid-column: 1 / -1;"></div>

                                <div style="font-weight: bold; color: #666;">رقم الهوية:</div>
                                <div>{row.get('رقم الهوية', '-')}</div>
                                
                                <div style="font-weight: bold; color: #666;">رقم الهاتف:</div>
                                <div>{row.get('رقم الهاتف', '-')}</div>
                                
                                <div style="font-weight: bold; color: #666;">الفرع:</div>
                                <div>{row.get('الفرع', 'غير محدد')}</div>
                                
                                <div style="font-weight: bold; color: #666;">الحالة الاجتماعية:</div>
                                <div>{row.get('الحالة الاجتماعية', '-')}</div>
                                
                                <div style="font-weight: bold; color: #666;">الزوجة:</div>
                                <div>{row.get('اسم الزوجة', '-')}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"❌ لم يتم العثور على سجل برقم الهوية: {search_id}")
            elif not search_id:
                st.warning("الرجاء إدخال رقم الهوية.")

# --- صفحة الأرشيف (Archive) ---
elif st.session_state.active_page == 'archive':
    st.markdown("""
    <div class="section-header">
        <h2>الأرشيف التاريخي للعائلة</h2>
        <div class="line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: white; padding: 40px; border-radius: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); margin-bottom: 30px;">
        <h3 style="color: #004d00;">📜 جذورنا التاريخية</h3>
        <p style="font-size: 1.1rem; line-height: 2; color: #444;">
        تعتبر عائلة الأسطل من العائلات العريقة والمتجذرة في مدينة خان يونس الصمود. يعود نسب العائلة إلى... [نص توثيقي طويل ومفصل يمكن جلبه من الموقع القديم].
        تميز أبناء العائلة عبر العقود بمشاركتهم الفاعلة في الحياة السياسية والاجتماعية، وقدمت العائلة خيرة أبنائها شهداء وأسرى على طريق الحرية.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # معرض الصور
    st.markdown("### 📷 صور من عبق الماضي")
    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1: st.image("https://via.placeholder.com/400x300?text=وثائق+عثمانية", use_column_width=True, caption="وثائق ملكية أراضي قديمة")
    with col_g2: st.image("https://via.placeholder.com/400x300?text=ديوان+المختار", use_column_width=True, caption="ديوان المختار القديم - 1950")
    with col_g3: st.image("https://via.placeholder.com/400x300?text=رجال+العائلة", use_column_width=True, caption="صورة جماعية لرجال العائلة - 1970")


# ==============================================================================
# 5. الفوتر (Footer)
# ==============================================================================
st.markdown("""
    <div class="footer">
        <img src="https://via.placeholder.com/50/ffffff/000000?text=Logo" style="border-radius:50%; margin-bottom:10px; opacity:0.5;">
        <p style="margin-bottom: 5px;">جميع الحقوق محفوظة © لمجلس عائلة الأسطل 2025</p>
        <p style="font-size: 0.8rem; opacity: 0.6;">تم التصميم والتطوير بجهود: <b>أ. قصي صبحي الأسطل</b></p>
        <br>
        <a href="#" style="color:#c5a059; text-decoration:none; margin:0 10px;">اتصل بنا</a>
        <a href="#" style="color:#c5a059; text-decoration:none; margin:0 10px;">سياسة الخصوصية</a>
    </div>
""", unsafe_allow_html=True)