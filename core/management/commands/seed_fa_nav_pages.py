"""
Management command to seed Persian navigation menu items and content pages.

Usage:
    python manage.py seed_fa_nav_pages [--clear]

This creates the main menu structure with submenus and corresponding
content pages for each submenu item.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from core.models import FaNavMenuItem
from apps.persian_cms.models import PersianPage


# ═══════════════════════════════════════════════════════════════════════════════
# Menu Structure Definition
# ═══════════════════════════════════════════════════════════════════════════════

MENU_STRUCTURE = [
    {
        "label": "اقامت یونان",
        "order": 1,
        "children": [
            {"label": "گلدن ویزای یونان با خرید ملک", "slug": "golden-visa-property"},
            {"label": "اقامت تمکن مالی (FIP) یونان", "slug": "fip-residency"},
            {"label": "اقامت دیجیتال نومد یونان", "slug": "digital-nomad"},
            {"label": "مراحل دریافت اقامت", "slug": "residency-process"},
            {"label": "سوالات متداول", "slug": "residency-faq"},
            {"label": "مقایسه روش‌های اقامت", "slug": "residency-comparison"},
        ],
    },
    {
        "label": "پروژه‌های ساختمانی",
        "order": 2,
        "children": [
            {"label": "پروژه‌های در حال فروش", "slug": "projects-for-sale"},
            {"label": "پروژه‌های تکمیل‌شده", "slug": "completed-projects"},
            {"label": "پروژه‌های در حال ساخت", "slug": "projects-under-construction"},
        ],
    },
    {
        "label": "زندگی در یونان",
        "order": 3,
        "children": [
            {"label": "هزینه زندگی", "slug": "cost-of-living"},
            {"label": "تحصیل فرزندان", "slug": "education"},
            {"label": "سیستم درمانی", "slug": "healthcare"},
            {"label": "افتتاح حساب بانکی", "slug": "bank-account"},
            {"label": "مالیات در یونان", "slug": "taxation"},
            {"label": "راهنمای شهرهای یونان", "slug": "city-guide"},
        ],
    },
    {
        "label": "خدمات آدونیس",
        "order": 4,
        "children": [
            {"label": "انواع اقامت یونان", "slug": "residency-types"},
            {"label": "خرید ملک", "slug": "property-purchase"},
            {"label": "ثبت شرکت", "slug": "company-registration"},
            {"label": "افتتاح حساب بانکی", "slug": "bank-account-services"},
            {"label": "خدمات حقوقی", "slug": "legal-services"},
            {"label": "مدیریت املاک", "slug": "property-management"},
        ],
    },
    {
        "label": "درباره ما",
        "order": 5,
        "children": [
            {"label": "معرفی ADONIS", "slug": "about-adonis"},
            {"label": "تیم ما", "slug": "our-team"},
            {"label": "مجوزها و افتخارات", "slug": "licenses-awards"},
            {"label": "رضایتمندی مشتریان", "slug": "testimonials"},
            {"label": "بروشور مجازی", "slug": "virtual-brochure"},
        ],
    },
    {
        "label": "بلاگ",
        "order": 6,
        "children": [
            {"label": "اخبار گلدن ویزا", "slug": "golden-visa-news"},
            {"label": "اخبار بازار املاک", "slug": "real-estate-news"},
            {"label": "راهنمای مهاجرت", "slug": "immigration-guide"},
            {"label": "مقالات سرمایه‌گذاری", "slug": "investment-articles"},
        ],
    },
    {
        "label": "تماس با ما",
        "order": 7,
        "children": [
            {"label": "رزرو مشاوره", "slug": "book-consultation"},
            {"label": "دفاتر آتن و تهران", "slug": "offices"},
            {"label": "فرم تماس", "slug": "contact-form"},
        ],
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
# Page Content Templates
# ═══════════════════════════════════════════════════════════════════════════════

def get_page_content(slug: str, title: str) -> dict:
    """Generate initial page content based on the page slug and title."""
    
    content_templates = {
        # ── اقامت یونان ────────────────────────────────────────────────────────
        "golden-visa-property": {
            "body": """
<div class="page-content">
    <h2>گلدن ویزای یونان با خرید ملک</h2>
    <p>برنامه گلدن ویزای یونان یکی از محبوب‌ترین برنامه‌های اقامت سرمایه‌گذاری در اروپاست. با خرید ملک به ارزش حداقل ۲۵۰,۰۰۰ یورو، شما و خانواده‌تان می‌توانید اقامت دائم یونان را دریافت کنید.</p>
    
    <h3>مزایای گلدن ویزای یونان</h3>
    <ul>
        <li>اقامت دائم برای کل خانواده</li>
        <li>دسترسی آزاد به کشورهای شنگن</li>
        <li>بدون الزام به اقامت فیزیکی</li>
        <li>امکان اجاره ملک و کسب درآمد</li>
        <li>مسیر به شهروندی اروپا</li>
    </ul>
</div>
""",
            "meta_description": "گلدن ویزای یونان با خرید ملک - دریافت اقامت دائم اروپا برای شما و خانواده با سرمایه‌گذاری در ملک یونان",
        },
        "fip-residency": {
            "body": """
<div class="page-content">
    <h2>اقامت تمکن مالی (FIP) یونان</h2>
    <p>برنامه اقامت تمکن مالی یونان (Financially Independent Person) برای افرادی طراحی شده که بدون نیاز به خرید ملک، با اثبات درآمد پایدار می‌توانند اقامت یونان را دریافت کنند.</p>
    
    <h3>شرایط اقامت FIP</h3>
    <ul>
        <li>اثبات درآمد سالانه حداقل ۲,۰۰۰ یورو در ماه</li>
        <li>بیمه درمانی معتبر</li>
        <li>عدم سابقه کیفری</li>
        <li>اثبات محل اقامت در یونان</li>
    </ul>
</div>
""",
            "meta_description": "اقامت تمکن مالی یونان FIP - دریافت اقامت بدون خرید ملک با اثبات درآمد پایدار",
        },
        "digital-nomad": {
            "body": """
<div class="page-content">
    <h2>اقامت دیجیتال نومد یونان</h2>
    <p>ویزای دیجیتال نومد یونان برای افرادی است که به صورت دورکاری برای شرکت‌های خارج از یونان کار می‌کنند و می‌خواهند در این کشور زیبا زندگی کنند.</p>
    
    <h3>مزایای ویزای دیجیتال نومد</h3>
    <ul>
        <li>اقامت قانونی تا ۲ سال قابل تمدید</li>
        <li>معافیت مالیاتی ویژه</li>
        <li>دسترسی به سیستم درمانی یونان</li>
        <li>امکان سفر آزاد در شنگن</li>
    </ul>
</div>
""",
            "meta_description": "ویزای دیجیتال نومد یونان - اقامت برای دورکاران و فریلنسرها با معافیت مالیاتی ویژه",
        },
        "residency-process": {
            "body": """
<div class="page-content">
    <h2>مراحل دریافت اقامت یونان</h2>
    <p>فرآیند دریافت اقامت یونان شامل چند مرحله اصلی است که تیم آدونیس در تمام مراحل همراه شماست.</p>
    
    <h3>مراحل کلی</h3>
    <ol>
        <li><strong>مشاوره اولیه:</strong> بررسی شرایط و انتخاب بهترین مسیر اقامتی</li>
        <li><strong>جمع‌آوری مدارک:</strong> آماده‌سازی مدارک لازم</li>
        <li><strong>سفر به یونان:</strong> بازدید از ملک و امضای قرارداد</li>
        <li><strong>ثبت‌نام:</strong> ارائه درخواست به اداره مهاجرت</li>
        <li><strong>دریافت کارت اقامت:</strong> صدور کارت اقامت دائم</li>
    </ol>
</div>
""",
            "meta_description": "مراحل دریافت اقامت یونان - راهنمای گام به گام فرآیند اخذ ویزا و اقامت دائم یونان",
        },
        "residency-faq": {
            "body": """
<div class="page-content">
    <h2>سوالات متداول اقامت یونان</h2>
    
    <div class="faq-item">
        <h3>حداقل سرمایه لازم برای گلدن ویزا چقدر است؟</h3>
        <p>حداقل ۲۵۰,۰۰۰ یورو برای مناطق غیرتوریستی و ۵۰۰,۰۰۰ یورو برای مناطق توریستی مانند آتن.</p>
    </div>
    
    <div class="faq-item">
        <h3>آیا باید در یونان زندگی کنم؟</h3>
        <p>خیر، گلدن ویزا الزام اقامت فیزیکی ندارد و فقط برای تمدید نیاز به حضور کوتاه است.</p>
    </div>
    
    <div class="faq-item">
        <h3>مدت زمان صدور ویزا چقدر است؟</h3>
        <p>معمولاً ۲ تا ۴ ماه از زمان ارائه درخواست کامل.</p>
    </div>
</div>
""",
            "meta_description": "سوالات متداول اقامت یونان - پاسخ به سوالات رایج درباره گلدن ویزا و اقامت دائم",
        },
        "residency-comparison": {
            "body": """
<div class="page-content">
    <h2>مقایسه روش‌های اقامت یونان</h2>
    <p>یونان چندین مسیر برای دریافت اقامت ارائه می‌دهد. در این جدول مقایسه‌ای، ویژگی‌های هر روش را بررسی می‌کنیم.</p>
    
    <table class="comparison-table">
        <tr>
            <th>ویژگی</th>
            <th>گلدن ویزا</th>
            <th>FIP</th>
            <th>دیجیتال نومد</th>
        </tr>
        <tr>
            <td>سرمایه لازم</td>
            <td>€250K-€500K</td>
            <td>€2,000/ماه</td>
            <td>€3,500/ماه</td>
        </tr>
        <tr>
            <td>الزام اقامت</td>
            <td>خیر</td>
            <td>بله</td>
            <td>بله</td>
        </tr>
        <tr>
            <td>شامل خانواده</td>
            <td>بله</td>
            <td>بله</td>
            <td>بله</td>
        </tr>
    </table>
</div>
""",
            "meta_description": "مقایسه روش‌های اقامت یونان - گلدن ویزا، FIP و دیجیتال نومد",
        },
        
        # ── پروژه‌های ساختمانی ─────────────────────────────────────────────────
        "projects-for-sale": {
            "body": """
<div class="page-content">
    <h2>پروژه‌های در حال فروش</h2>
    <p>پروژه‌های ملکی واجد شرایط گلدن ویزا که در حال حاضر برای فروش موجود هستند. تمام این پروژه‌ها توسط تیم آدونیس بررسی و تأیید شده‌اند.</p>
    
    <div class="projects-list">
        <!-- لیست پروژه‌ها اینجا نمایش داده می‌شود -->
        <p class="note">برای مشاهده پروژه‌های موجود، با ما تماس بگیرید.</p>
    </div>
</div>
""",
            "meta_description": "پروژه‌های ملکی در حال فروش یونان - آپارتمان و ویلا واجد شرایط گلدن ویزا",
        },
        "completed-projects": {
            "body": """
<div class="page-content">
    <h2>پروژه‌های تکمیل‌شده</h2>
    <p>پروژه‌هایی که توسط آدونیس به مشتریان ارائه شده و به بهره‌برداری رسیده‌اند.</p>
    
    <div class="projects-gallery">
        <p class="note">گالری پروژه‌های تکمیل‌شده به زودی اضافه می‌شود.</p>
    </div>
</div>
""",
            "meta_description": "پروژه‌های تکمیل‌شده آدونیس - نمونه کارهای موفق سرمایه‌گذاری ملکی در یونان",
        },
        "projects-under-construction": {
            "body": """
<div class="page-content">
    <h2>پروژه‌های در حال ساخت</h2>
    <p>پروژه‌های ملکی که در مرحله ساخت هستند و فرصت سرمایه‌گذاری با قیمت پیش‌فروش دارند.</p>
    
    <h3>مزایای خرید پیش‌فروش</h3>
    <ul>
        <li>قیمت پایین‌تر نسبت به پروژه‌های آماده</li>
        <li>امکان انتخاب واحد دلخواه</li>
        <li>پرداخت مرحله‌ای</li>
        <li>افزایش ارزش ملک تا زمان تحویل</li>
    </ul>
</div>
""",
            "meta_description": "پروژه‌های در حال ساخت یونان - خرید پیش‌فروش ملک با قیمت ویژه",
        },
        
        # ── زندگی در یونان ─────────────────────────────────────────────────────
        "cost-of-living": {
            "body": """
<div class="page-content">
    <h2>هزینه زندگی در یونان</h2>
    <p>یونان یکی از ارزان‌ترین کشورهای اروپای غربی برای زندگی است. در این صفحه، هزینه‌های تقریبی زندگی در آتن و سایر شهرها را بررسی می‌کنیم.</p>
    
    <h3>هزینه‌های ماهانه تقریبی (یورو)</h3>
    <ul>
        <li>اجاره آپارتمان یک خوابه: ۵۰۰-۸۰۰</li>
        <li>خوراک و خرید روزانه: ۳۰۰-۵۰۰</li>
        <li>حمل و نقل عمومی: ۳۰</li>
        <li>قبوض (آب، برق، گاز): ۱۰۰-۱۵۰</li>
        <li>بیمه درمانی: ۵۰-۱۰۰</li>
    </ul>
</div>
""",
            "meta_description": "هزینه زندگی در یونان - راهنمای کامل هزینه‌های ماهانه آتن و شهرهای یونان",
        },
        "education": {
            "body": """
<div class="page-content">
    <h2>تحصیل فرزندان در یونان</h2>
    <p>سیستم آموزشی یونان برای دارندگان اقامت، دسترسی رایگان به مدارس دولتی فراهم می‌کند. همچنین مدارس بین‌المللی متعددی در آتن و سایر شهرها وجود دارد.</p>
    
    <h3>گزینه‌های آموزشی</h3>
    <ul>
        <li><strong>مدارس دولتی:</strong> رایگان برای مقیمان</li>
        <li><strong>مدارس بین‌المللی:</strong> با برنامه IB یا آمریکایی</li>
        <li><strong>مدارس خصوصی یونانی:</strong> کیفیت بالا با هزینه معقول</li>
        <li><strong>دانشگاه‌ها:</strong> تحصیل رایگان برای مقیمان EU</li>
    </ul>
</div>
""",
            "meta_description": "تحصیل فرزندان در یونان - مدارس بین‌المللی و دولتی برای خانواده‌های مقیم",
        },
        "healthcare": {
            "body": """
<div class="page-content">
    <h2>سیستم درمانی یونان</h2>
    <p>یونان دارای سیستم بهداشتی جامع با بیمارستان‌های مجهز و پزشکان متخصص است.</p>
    
    <h3>خدمات درمانی</h3>
    <ul>
        <li>بیمارستان‌های دولتی با خدمات رایگان/کم‌هزینه</li>
        <li>کلینیک‌های خصوصی با کیفیت بالا</li>
        <li>داروخانه‌های ۲۴ ساعته</li>
        <li>خدمات اورژانس رایگان</li>
    </ul>
</div>
""",
            "meta_description": "سیستم درمانی یونان - بیمارستان‌ها، بیمه سلامت و خدمات پزشکی برای مقیمان",
        },
        "bank-account": {
            "body": """
<div class="page-content">
    <h2>افتتاح حساب بانکی در یونان</h2>
    <p>افتتاح حساب بانکی در یونان برای خرید ملک و امور مالی ضروری است. آدونیس در این فرآیند همراه شماست.</p>
    
    <h3>مدارک لازم</h3>
    <ul>
        <li>پاسپورت معتبر</li>
        <li>شماره مالیاتی یونان (AFM)</li>
        <li>اثبات آدرس</li>
        <li>مدرک منبع درآمد</li>
    </ul>
</div>
""",
            "meta_description": "افتتاح حساب بانکی در یونان - مدارک و مراحل لازم برای سرمایه‌گذاران",
        },
        "taxation": {
            "body": """
<div class="page-content">
    <h2>مالیات در یونان</h2>
    <p>آشنایی با سیستم مالیاتی یونان برای سرمایه‌گذاران و مقیمان ضروری است.</p>
    
    <h3>انواع مالیات</h3>
    <ul>
        <li><strong>مالیات بر درآمد:</strong> ۲۲٪ تا ۴۴٪ پلکانی</li>
        <li><strong>مالیات ملک:</strong> ENFIA سالانه</li>
        <li><strong>مالیات انتقال:</strong> ۳٪ هنگام خرید</li>
        <li><strong>مالیات اجاره:</strong> ۱۵٪ تا ۴۵٪</li>
    </ul>
</div>
""",
            "meta_description": "مالیات در یونان - راهنمای کامل نرخ‌های مالیاتی برای مقیمان و سرمایه‌گذاران",
        },
        "city-guide": {
            "body": """
<div class="page-content">
    <h2>راهنمای شهرهای یونان</h2>
    <p>معرفی شهرهای اصلی یونان برای زندگی و سرمایه‌گذاری.</p>
    
    <h3>آتن</h3>
    <p>پایتخت و بزرگترین شهر یونان با امکانات کامل شهری و فرصت‌های سرمایه‌گذاری متنوع.</p>
    
    <h3>تسالونیکی</h3>
    <p>دومین شهر بزرگ با فضای دانشگاهی و هزینه زندگی پایین‌تر.</p>
    
    <h3>جزایر</h3>
    <p>سانتورینی، میکونوس و کرت برای سرمایه‌گذاری گردشگری.</p>
</div>
""",
            "meta_description": "راهنمای شهرهای یونان - آتن، تسالونیکی و جزایر برای زندگی و سرمایه‌گذاری",
        },
        
        # ── خدمات آدونیس ───────────────────────────────────────────────────────
        "residency-types": {
            "body": """
<div class="page-content">
    <h2>انواع اقامت یونان</h2>
    <p>آدونیس در همه انواع اقامت یونان به شما خدمات ارائه می‌دهد.</p>
    
    <h3>خدمات ما</h3>
    <ul>
        <li>مشاوره انتخاب بهترین نوع اقامت</li>
        <li>آماده‌سازی مدارک</li>
        <li>پیگیری درخواست</li>
        <li>خدمات پس از صدور</li>
    </ul>
</div>
""",
            "meta_description": "خدمات اقامت یونان آدونیس - مشاوره و پیگیری انواع ویزا و اقامت",
        },
        "property-purchase": {
            "body": """
<div class="page-content">
    <h2>خدمات خرید ملک</h2>
    <p>آدونیس به عنوان مشاور املاک معتبر، شما را در تمام مراحل خرید ملک در یونان همراهی می‌کند.</p>
    
    <h3>خدمات ما</h3>
    <ul>
        <li>جستجو و معرفی ملک‌های مناسب</li>
        <li>بازدید حضوری با ترجمه فارسی</li>
        <li>مذاکره قیمت</li>
        <li>بررسی حقوقی ملک</li>
        <li>همراهی در دفتر اسناد</li>
    </ul>
</div>
""",
            "meta_description": "خدمات خرید ملک در یونان - مشاوره، بازدید و پیگیری قانونی توسط آدونیس",
        },
        "company-registration": {
            "body": """
<div class="page-content">
    <h2>ثبت شرکت در یونان</h2>
    <p>ثبت شرکت در یونان برای فعالیت تجاری و کارآفرینی با همراهی آدونیس.</p>
    
    <h3>انواع شرکت</h3>
    <ul>
        <li>IKE (شرکت خصوصی): رایج‌ترین نوع</li>
        <li>EPE (شرکت با مسئولیت محدود)</li>
        <li>AE (شرکت سهامی)</li>
    </ul>
</div>
""",
            "meta_description": "ثبت شرکت در یونان - راه‌اندازی کسب‌وکار و شرکت با مشاوره آدونیس",
        },
        "bank-account-services": {
            "body": """
<div class="page-content">
    <h2>خدمات افتتاح حساب بانکی</h2>
    <p>آدونیس شما را در افتتاح حساب بانکی در یونان همراهی می‌کند.</p>
    
    <h3>خدمات</h3>
    <ul>
        <li>راهنمایی انتخاب بانک مناسب</li>
        <li>آماده‌سازی مدارک</li>
        <li>همراهی در شعبه بانک</li>
        <li>فعال‌سازی اینترنت بانک</li>
    </ul>
</div>
""",
            "meta_description": "خدمات افتتاح حساب بانکی یونان - همراهی کامل آدونیس در تمام مراحل",
        },
        "legal-services": {
            "body": """
<div class="page-content">
    <h2>خدمات حقوقی</h2>
    <p>تیم حقوقی آدونیس در تمام امور قانونی مربوط به اقامت و سرمایه‌گذاری در یونان همراه شماست.</p>
    
    <h3>خدمات حقوقی</h3>
    <ul>
        <li>مشاوره حقوقی خرید ملک</li>
        <li>بررسی سند مالکیت</li>
        <li>تنظیم قرارداد</li>
        <li>وکالت در اداره مهاجرت</li>
        <li>حل اختلافات</li>
    </ul>
</div>
""",
            "meta_description": "خدمات حقوقی آدونیس در یونان - وکالت، مشاوره و پیگیری امور قانونی",
        },
        "property-management": {
            "body": """
<div class="page-content">
    <h2>مدیریت املاک</h2>
    <p>آدونیس خدمات مدیریت ملک را برای سرمایه‌گذارانی که در یونان حضور ندارند ارائه می‌دهد.</p>
    
    <h3>خدمات مدیریت</h3>
    <ul>
        <li>اجاره کوتاه‌مدت (Airbnb)</li>
        <li>اجاره بلندمدت</li>
        <li>نگهداری و تعمیرات</li>
        <li>پرداخت قبوض و مالیات</li>
        <li>گزارش‌دهی مالی</li>
    </ul>
</div>
""",
            "meta_description": "مدیریت املاک در یونان - اجاره، نگهداری و گزارش‌دهی توسط آدونیس",
        },
        
        # ── درباره ما ──────────────────────────────────────────────────────────
        "about-adonis": {
            "body": """
<div class="page-content">
    <h2>معرفی آدونیس (ADONIS)</h2>
    <p>آدونیس گروپ یکی از معتبرترین شرکت‌های مشاوره اقامت و سرمایه‌گذاری در یونان است که با دفاتر رسمی در آتن و تهران به هموطنان ایرانی خدمات ارائه می‌دهد.</p>
    
    <h3>چرا آدونیس؟</h3>
    <ul>
        <li>دفتر رسمی در آتن یونان</li>
        <li>تیم متخصص فارسی‌زبان</li>
        <li>بیش از ۵۰۰ پرونده موفق</li>
        <li>پشتیبانی ۲۴/۷</li>
    </ul>
</div>
""",
            "meta_description": "معرفی آدونیس گروپ - شرکت مشاوره اقامت و سرمایه‌گذاری یونان با دفتر در آتن",
        },
        "our-team": {
            "body": """
<div class="page-content">
    <h2>تیم ما</h2>
    <p>تیم آدونیس متشکل از متخصصان با تجربه در زمینه مهاجرت، املاک و حقوق است.</p>
    
    <div class="team-grid">
        <p class="note">معرفی اعضای تیم به زودی اضافه می‌شود.</p>
    </div>
</div>
""",
            "meta_description": "تیم آدونیس - متخصصان مهاجرت و سرمایه‌گذاری یونان",
        },
        "licenses-awards": {
            "body": """
<div class="page-content">
    <h2>مجوزها و افتخارات</h2>
    <p>آدونیس دارای تمام مجوزهای قانونی لازم برای فعالیت در یونان است.</p>
    
    <h3>مجوزها</h3>
    <ul>
        <li>پروانه مشاور املاک یونان</li>
        <li>عضویت در انجمن مشاوران مهاجرت</li>
        <li>گواهی ISO 9001</li>
    </ul>
</div>
""",
            "meta_description": "مجوزها و افتخارات آدونیس - پروانه‌های رسمی فعالیت در یونان",
        },
        "testimonials": {
            "body": """
<div class="page-content">
    <h2>رضایتمندی مشتریان</h2>
    <p>نظرات مشتریانی که با کمک آدونیس اقامت یونان را دریافت کرده‌اند.</p>
    
    <div class="testimonials-grid">
        <p class="note">نظرات مشتریان به زودی اضافه می‌شود.</p>
    </div>
</div>
""",
            "meta_description": "نظرات مشتریان آدونیس - تجربه موفق دریافت اقامت یونان",
        },
        "virtual-brochure": {
            "body": """
<div class="page-content">
    <h2>بروشور مجازی آدونیس</h2>
    <p>بروشور دیجیتال خدمات آدونیس را مشاهده کنید.</p>
    
    <div class="brochure-viewer">
        <p class="note">بروشور مجازی به زودی در دسترس قرار می‌گیرد.</p>
    </div>
</div>
""",
            "meta_description": "بروشور مجازی آدونیس - معرفی خدمات اقامت و سرمایه‌گذاری یونان",
        },
        
        # ── بلاگ ────────────────────────────────────────────────────────────────
        "golden-visa-news": {
            "body": """
<div class="page-content">
    <h2>اخبار گلدن ویزا</h2>
    <p>آخرین اخبار و تغییرات برنامه گلدن ویزای یونان و سایر کشورها.</p>
    
    <div class="news-list">
        <p class="note">اخبار به‌روز به زودی اضافه می‌شود.</p>
    </div>
</div>
""",
            "meta_description": "اخبار گلدن ویزا - آخرین تغییرات برنامه‌های اقامت سرمایه‌گذاری اروپا",
        },
        "real-estate-news": {
            "body": """
<div class="page-content">
    <h2>اخبار بازار املاک یونان</h2>
    <p>تحلیل بازار مسکن و روند قیمت‌ها در یونان.</p>
    
    <div class="news-list">
        <p class="note">تحلیل‌های بازار به زودی اضافه می‌شود.</p>
    </div>
</div>
""",
            "meta_description": "اخبار بازار املاک یونان - تحلیل قیمت مسکن و فرصت‌های سرمایه‌گذاری",
        },
        "immigration-guide": {
            "body": """
<div class="page-content">
    <h2>راهنمای مهاجرت</h2>
    <p>مقالات آموزشی درباره مهاجرت به یونان و زندگی در اروپا.</p>
    
    <div class="articles-list">
        <p class="note">مقالات راهنما به زودی اضافه می‌شود.</p>
    </div>
</div>
""",
            "meta_description": "راهنمای مهاجرت به یونان - مقالات آموزشی زندگی و کار در اروپا",
        },
        "investment-articles": {
            "body": """
<div class="page-content">
    <h2>مقالات سرمایه‌گذاری</h2>
    <p>راهنمای سرمایه‌گذاری در ملک و کسب‌وکار یونان.</p>
    
    <div class="articles-list">
        <p class="note">مقالات سرمایه‌گذاری به زودی اضافه می‌شود.</p>
    </div>
</div>
""",
            "meta_description": "مقالات سرمایه‌گذاری یونان - راهنمای خرید ملک و راه‌اندازی کسب‌وکار",
        },
        
        # ── تماس با ما ─────────────────────────────────────────────────────────
        "book-consultation": {
            "body": """
<div class="page-content">
    <h2>رزرو مشاوره</h2>
    <p>برای دریافت مشاوره رایگان با کارشناسان آدونیس، فرم زیر را تکمیل کنید یا تماس بگیرید.</p>
    
    <div class="consultation-form">
        <p class="note">فرم رزرو مشاوره به زودی فعال می‌شود.</p>
        
        <h3>راه‌های ارتباطی</h3>
        <ul>
            <li>واتس‌اپ: +۳۰ ۶۹۸ ۵۹۸ ۹۵۹۶</li>
            <li>ایمیل: info@adonisgroup.gr</li>
        </ul>
    </div>
</div>
""",
            "meta_description": "رزرو مشاوره رایگان آدونیس - مشاوره اقامت و سرمایه‌گذاری یونان",
        },
        "offices": {
            "body": """
<div class="page-content">
    <h2>دفاتر آدونیس</h2>
    
    <div class="office-card">
        <h3>دفتر آتن</h3>
        <p>آدرس: خیابان پوزیدوناس، شماره ۷۸، آلیموس، آتن</p>
        <p>تلفن: +30 698 598 9596</p>
    </div>
    
    <div class="office-card">
        <h3>دفتر تهران</h3>
        <p>برای اطلاع از آدرس دفتر تهران با ما تماس بگیرید.</p>
    </div>
</div>
""",
            "meta_description": "دفاتر آدونیس در آتن و تهران - آدرس و اطلاعات تماس",
        },
        "contact-form": {
            "body": """
<div class="page-content">
    <h2>فرم تماس</h2>
    <p>پیام خود را برای ما ارسال کنید و در اسرع وقت پاسخ خواهیم داد.</p>
    
    <div class="contact-form">
        <p class="note">فرم تماس به زودی فعال می‌شود.</p>
        
        <h3>تماس فوری</h3>
        <p>واتس‌اپ: +۳۰ ۶۹۸ ۵۹۸ ۹۵۹۶</p>
        <p>ایمیل: info@adonisgroup.gr</p>
    </div>
</div>
""",
            "meta_description": "فرم تماس آدونیس - ارسال پیام و درخواست مشاوره",
        },
    }
    
    template = content_templates.get(slug, {})
    return {
        "body": template.get("body", f"<div class='page-content'><h2>{title}</h2><p>محتوای این صفحه به زودی اضافه می‌شود.</p></div>"),
        "meta_description": template.get("meta_description", f"{title} - آدونیس گروپ مشاور اقامت و سرمایه‌گذاری یونان"),
    }


class Command(BaseCommand):
    help = 'Seed Persian navigation menu items and content pages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing menu items and pages before seeding',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('\n═══════════════════════════════════════════════════════════'))
        self.stdout.write(self.style.NOTICE('  Seeding Persian Navigation Menu & Content Pages'))
        self.stdout.write(self.style.NOTICE('═══════════════════════════════════════════════════════════\n'))

        dry_run = options['dry_run']
        
        if options['clear']:
            if dry_run:
                self.stdout.write(self.style.WARNING('[DRY RUN] Would delete all FaNavMenuItem and related pages'))
            else:
                self.stdout.write(self.style.WARNING('Clearing existing menu items...'))
                FaNavMenuItem.objects.all().delete()
                # Don't delete pages - they might have custom content
                self.stdout.write(self.style.SUCCESS('✓ Cleared existing menu items'))

        created_menus = 0
        created_pages = 0
        updated_pages = 0

        for menu_data in MENU_STRUCTURE:
            # Create parent menu item
            parent_label = menu_data['label']
            parent_order = menu_data['order']
            
            if dry_run:
                self.stdout.write(f'\n[DRY RUN] Would create menu: {parent_label}')
            else:
                parent_item, created = FaNavMenuItem.objects.get_or_create(
                    label=parent_label,
                    parent=None,
                    defaults={
                        'url': '',  # Parent items don't need URLs
                        'order': parent_order,
                        'is_active': True,
                    }
                )
                if created:
                    created_menus += 1
                    self.stdout.write(f'\n✓ Created menu: {parent_label}')
                else:
                    parent_item.order = parent_order
                    parent_item.save()
                    self.stdout.write(f'\n• Updated menu: {parent_label}')

            # Create child menu items and pages
            for child_order, child_data in enumerate(menu_data.get('children', []), start=1):
                child_label = child_data['label']
                child_slug = child_data['slug']
                page_url = f'/fa-new/p/{child_slug}/'
                
                if dry_run:
                    self.stdout.write(f'  [DRY RUN] Would create submenu: {child_label} → {page_url}')
                else:
                    # Create submenu item
                    child_item, created = FaNavMenuItem.objects.get_or_create(
                        label=child_label,
                        parent=parent_item,
                        defaults={
                            'url': page_url,
                            'order': child_order,
                            'is_active': True,
                        }
                    )
                    if created:
                        created_menus += 1
                        self.stdout.write(f'  ✓ Created submenu: {child_label}')
                    else:
                        child_item.url = page_url
                        child_item.order = child_order
                        child_item.save()
                        self.stdout.write(f'  • Updated submenu: {child_label}')
                    
                    # Create or update page
                    page_content = get_page_content(child_slug, child_label)
                    page, page_created = PersianPage.objects.get_or_create(
                        slug=child_slug,
                        defaults={
                            'title': child_label,
                            'page_type': 'custom',
                            'body': page_content['body'],
                            'meta_description': page_content['meta_description'],
                            'is_published': True,
                        }
                    )
                    if page_created:
                        created_pages += 1
                        self.stdout.write(self.style.SUCCESS(f'    → Created page: {child_slug}'))
                    else:
                        updated_pages += 1
                        self.stdout.write(f'    → Page exists: {child_slug}')

        # Summary
        self.stdout.write('\n' + '═' * 60)
        if dry_run:
            self.stdout.write(self.style.WARNING('\n[DRY RUN] No changes made.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n✓ Created {created_menus} menu items'))
            self.stdout.write(self.style.SUCCESS(f'✓ Created {created_pages} new pages'))
            self.stdout.write(f'• {updated_pages} pages already existed')
        self.stdout.write('\n' + '═' * 60 + '\n')
