from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import ConstValue, Term
from .models import Lesson
from .models import  Class
from .models import ClassOffer
from .models import Department
from .models import Person
from .models import Tendency
from .models import Student
from .models import Internship
from .models import StudentPayments
from .models import Employee
from .models import EducationBranch



class HasParentFilter(admin.SimpleListFilter):
    title = _("سلسله‌مراتب")
    parameter_name = "hierarchy"

    def lookups(self, request, model_admin):
        return (
            ("root", _("فقط ریشه (بدون والد)")),
            ("child", _("فقط زیرمجموعه (دارای والد)")),
            ("has_children", _("دارای فرزند")),
            ("leaf", _("برگ (بدون فرزند)")),
        )

    def queryset(self, request, queryset):
        if self.value() == "root":
            return queryset.filter(parent__isnull=True)
        if self.value() == "child":
            return queryset.filter(parent__isnull=False)
        if self.value() == "has_children":
            return queryset.annotate(_child_count=Count("children")).filter(_child_count__gt=0)
        if self.value() == "leaf":
            return queryset.annotate(_child_count=Count("children")).filter(_child_count=0)
        return queryset


class ParentFilter(admin.SimpleListFilter):
    title = _("والد")
    parameter_name = "parent_id"

    def lookups(self, request, model_admin):
        parents = (
            ConstValue.objects.filter(children__isnull=False)
            .distinct()
            .order_by("caption", "code")[:50]
        )
        return [(p.pk, str(p)) for p in parents]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(parent_id=self.value())
        return queryset


class EmptyFieldFilter(admin.SimpleListFilter):
    title = _("فیلدهای خالی")
    parameter_name = "empty_field"

    def lookups(self, request, model_admin):
        return (
            ("name", _("نام مقدار خالی")),
            ("value", _("مقدار خالی")),
            ("value_title", _("عنوان مقدار ثابت خالی")),
            ("caption", _("عنوان خالی")),
        )

    def queryset(self, request, queryset):
        mapping = {
            "name": Q(name="") | Q(name__isnull=True),
            "value": Q(value="") | Q(value__isnull=True),
            "value_title": Q(value_title="") | Q(value_title__isnull=True),
            "caption": Q(caption="") | Q(caption__isnull=True),
        }
        if self.value() in mapping:
            return queryset.filter(mapping[self.value()])
        return queryset


@admin.register(ConstValue)
class ConstValueAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "hierarchy_indent",
        "caption",
        "code",
        "name",
        "value",
        "value_title",
        "parent_link",
        "children_count",
        "is_active_badge",
    )
    list_display_links = ("caption", "code")
    list_filter = (
        "is_active",
        HasParentFilter,
        ParentFilter,
        EmptyFieldFilter,
        ("parent", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        "id",
        "caption",
        "code",
        "name",
        "value",
        "value_title",
        "parent__caption",
        "parent__code",
        "parent__name",
        "parent__value",
        "children__caption",
        "children__code",
    )
    search_help_text = _(
        "جستجو در عنوان، کد، نام، مقدار، عنوان مقدار ثابت، والد و فرزندان"
    )
    autocomplete_fields = ("parent",)
    list_select_related = ("parent",)
    ordering = ("parent_id", "caption", "code")
    list_per_page = 50
    save_on_top = True
    actions = ("activate_selected", "deactivate_selected")

    fieldsets = (
        (
            _("شناسه و وضعیت"),
            {"fields": ("code", "caption", "is_active")},
        ),
        (
            _("سلسله‌مراتب"),
            {"fields": ("parent",)},
        ),
        (
            _("مقادیر"),
            {"fields": ("name", "value", "value_title")},
        ),
    )

    @admin.display(description=_("عنوان (سلسله)"))
    def hierarchy_indent(self, obj):
        depth = 0
        current = obj.parent
        while current and depth < 10:
            depth += 1
            current = current.parent
        prefix = "— " * depth if depth else ""
        return format_html("{}{}", prefix, obj.caption or "—")

    @admin.display(description=_("والد"))
    def parent_link(self, obj):
        if not obj.parent_id:
            return "—"
        url = f"/admin/core/constvalue/{obj.parent_id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.parent)

    @admin.display(description=_("فرزندان"))
    def children_count(self, obj):
        return obj.children.count()

    @admin.display(description=_("فعال"), boolean=True)
    def is_active_badge(self, obj):
        return obj.is_active

    @admin.action(description=_("فعال‌سازی موارد انتخاب‌شده"))
    def activate_selected(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _("%(count)d مورد فعال شد.") % {"count": updated})

    @admin.action(description=_("غیرفعال‌سازی موارد انتخاب‌شده"))
    def deactivate_selected(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _("%(count)d مورد غیرفعال شد.") % {"count": updated})

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("parent").prefetch_related("children")

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term.isdigit():
            queryset |= self.model.objects.filter(pk=int(search_term))
            use_distinct = True
        return queryset, use_distinct
#=============================================================================================================
#الهه هاشم آبادی

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):

    list_display = (
        "lesson_code",
        "title",
        "department",
        "education_branch",
        "units",
        "practical_units",
        "theoretical_units",
        "lesson_type",
        "minimum_score",
        "active_status",
        "prerequisite_count",
    )

    list_display_links = (
        "lesson_code",
        "title",
    )

    list_filter = (
        "is_active",
        "department",
        "education_branch",
        "lesson_language",
        "lesson_type",
    )

    search_fields = (
        "lesson_code",
        "title",
        "department__department_title",
        "department__name",
        "education_branch__title",
    )

    search_help_text = (
        "جستجو بر اساس کد درس، عنوان درس، دانشکده و رشته"
    )

    #autocomplete_fields = (
    #    "department",
     #   "education_branch",
     #   "lesson_language",
        
    #)

    filter_horizontal = (
        "prerequisites",
    )

    list_select_related = (
        "department",
        "education_branch",
        "lesson_language",
    )

    ordering = (
        "lesson_code",
    )

    list_per_page = 50
    save_on_top = True

    actions = (
        "activate_selected",
        "deactivate_selected",
    )

    fieldsets = (
        (
            "اطلاعات اصلی درس",
            {
                "fields": (
                    "lesson_code",
                    "title",
                    "department",
                    "education_branch",
                )
            }
        ),

        (
            "واحدها",
            {
                "fields": (
                    "units",
                    "theoretical_units",
                    "practical_units",
                )
            }
        ),

        (
            "مشخصات آموزشی",
            {
                "fields": (
                    "lesson_type",
                    "lesson_language",
                    "lesson_hours",
                    "minimum_score",
                )
            }
        ),

        (
            "پیش نیازها",
            {
                "fields": (
                    "prerequisites",
                )
            }
        ),

        (
            "فایل ها",
            {
                "fields": (
                    "syllabus_file",
                )
            }
        ),

        (
            "وضعیت",
            {
                "fields": (
                    "is_active",
                )
            }
        ),
    )

    @admin.display(boolean=True, description="فعال")
    def active_status(self, obj):
        return obj.is_active

    @admin.display(description="تعداد پیش نیاز")
    def prerequisite_count(self, obj):
        return obj.prerequisites.count()

    @admin.action(description="فعال سازی دروس انتخاب شده")
    def activate_selected(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f"{updated} درس فعال شد."
        )

    @admin.action(description="غیرفعال سازی دروس انتخاب شده")
    def deactivate_selected(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"{updated} درس غیرفعال شد."
        )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "department",
                "education_branch",
                "lesson_language",
            )
            .prefetch_related(
                "prerequisites",
            )
        )
#---------------------------------
@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):

    list_display = (
        "class_number",
        "lesson",
        "term",
        "class_day",
        "class_time",
        "class_location",
        "max_capacity",
        "attendance_status",
        "recorded_status",
        "class_type",
    )

    list_display_links = (
        "class_number",
        "lesson",
    )

    list_filter = (
        "class_day",
        "attendance_mandatory",
        "recorded_sessions_available",
        "class_type",
        "term",
        "tendency",
    )

    search_fields = (
        "class_number",
        "lesson__title",
        "lesson__lesson_code",
        "class_location",
    )

    search_help_text = (
        "جستجو بر اساس شماره کلاس، عنوان درس، کد درس و محل برگزاری"
    )

      #autocomplete_fields = (
       # "lesson",
       # "term",
       # "tendency",
       # "class_type",
    #)
    

    list_select_related = (
        "lesson",
        "term",
        "tendency",
        "class_type",
    )

    ordering = (
        "class_number",
    )

    list_per_page = 50
    save_on_top = True

    actions = (
        "enable_recordings",
        "disable_recordings",
        "make_attendance_mandatory",
        "make_attendance_optional",
    )

    fieldsets = (
        (
            "اطلاعات کلاس",
            {
                "fields": (
                    "class_number",
                    "lesson",
                    "term",
                    "tendency",
                )
            }
        ),
        (
            "زمان و مکان",
            {
                "fields": (
                    "class_day",
                    "class_time",
                    "class_location",
                )
            }
        ),
        (
            "ظرفیت و غیبت",
            {
                "fields": (
                    "max_capacity",
                    "max_absence_limit",
                )
            }
        ),
        (
            "تنظیمات آموزشی",
            {
                "fields": (
                    "attendance_mandatory",
                    "recorded_sessions_available",
                    "class_type",
                )
            }
        ),
    )

    @admin.display(boolean=True, description="حضور اجباری")
    def attendance_status(self, obj):
        return obj.attendance_mandatory

    @admin.display(boolean=True, description="جلسات ضبط شده")
    def recorded_status(self, obj):
        return obj.recorded_sessions_available

    @admin.action(description="فعال سازی جلسات ضبط شده")
    def enable_recordings(self, request, queryset):
        updated = queryset.update(recorded_sessions_available=True)
        self.message_user(request, f"{updated} کلاس بروزرسانی شد.")

    @admin.action(description="غیرفعال سازی جلسات ضبط شده")
    def disable_recordings(self, request, queryset):
        updated = queryset.update(recorded_sessions_available=False)
        self.message_user(request, f"{updated} کلاس بروزرسانی شد.")

    @admin.action(description="اجباری کردن حضور")
    def make_attendance_mandatory(self, request, queryset):
        updated = queryset.update(attendance_mandatory=True)
        self.message_user(request, f"{updated} کلاس بروزرسانی شد.")

    @admin.action(description="اختیاری کردن حضور")
    def make_attendance_optional(self, request, queryset):
        updated = queryset.update(attendance_mandatory=False)
        self.message_user(request, f"{updated} کلاس بروزرسانی شد.")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "lesson",
                "term",
                "tendency",
                "class_type",
            )
        )
#----------------------------------------------
@admin.register(ClassOffer)
class ClassOfferAdmin(admin.ModelAdmin):

    list_display = (
        "class_group",
        "teacher",
        "term",
        "lesson_name",
        "teacher_name",
    )

    list_display_links = (
        "class_group",
        "teacher",
    )

    list_filter = (
        "term",
        "teacher",
    )

    search_fields = (
        "class_group__class_number",
        "teacher__full_name",
        "term__term_title",
        "term__name",
    )

    search_help_text = (
        "جستجو بر اساس شماره کلاس، نام استاد و ترم"
    )

     #autocomplete_fields = (
       # "class_group",
       # "teacher",
        #"term",
    #)

    list_select_related = (
        "class_group",
        "teacher",
        "term",
    )

    ordering = (
        "term__term_title",
         "term__term_id"
    )

    list_per_page = 50
    save_on_top = True

    fieldsets = (
        (
            "اطلاعات ارائه درس",
            {
                "fields": (
                    "class_group",
                    "teacher",
                    "term",
                )
            }
        ),
    )

    @admin.display(description="درس")
    def lesson_name(self, obj):
        if obj.class_group and obj.class_group.lesson:
            return obj.class_group.lesson.title
        return "-"

    @admin.display(description="نام استاد")
    def teacher_name(self, obj):
        if obj.teacher:
            return obj.teacher.full_name
        return "-"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "class_group",
                "teacher",
                "term",
                "class_group__lesson",
            )
        )
#=============================================================================================================
# =============================================================================
# Department, Atena Nik Ram
# =============================================================================

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        "department_code",
        "department_title",
        "dean_name",
        "student_count",
        "phone_number",
        "establish_year_display",
    )

    list_display_links = (
        "department_code",
        "department_title",
    )

    list_filter = (
        "establish_year",
    )

    search_fields = (
        "department_code",
        "department_title",
        "dean_name",
        "name",
        "phone_number",
        "department_address",
    )

    search_help_text = (
        "جستجو بر اساس کد دانشکده، عنوان دانشکده، رئیس دانشکده و گروه آموزشی"
    )

    ordering = (
        "department_title",
    )

    list_per_page = 50
    save_on_top = True

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "department_code",
                    "department_title",
                    "name",
                )
            }
        ),

        (
            "مدیریت و آمار",
            {
                "fields": (
                    "dean_name",
                    "student_count",
                    "establish_year",
                )
            }
        ),

        (
            "اطلاعات تماس",
            {
                "fields": (
                    "phone_number",
                    "website_url",
                    "department_address",
                )
            }
        ),
    )

    @admin.display(description="سال تأسیس")
    def establish_year_display(self, obj):
        if obj.establish_year:
            return obj.establish_year.year
        return "-"


# =============================================================================
# Person, Atena Nik Ram
# =============================================================================

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "full_name",
        "national_code",
        "gender",
        "is_active",
        "is_online",
        "is_email_verified",
        "account_locked",
    )

    list_display_links = (
        "username",
        "full_name",
    )

    list_filter = (
        "is_active",
        "is_online",
        "is_email_verified",
        "account_locked",
        "gender",
        "is_foreign",
        "marital_status",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "full_name",
        "national_code",
        "nationality",
    )

    search_help_text = (
        "جستجو بر اساس نام کاربری، نام، نام خانوادگی، نام کامل و کد ملی"
    )

    ordering = ("username",)

    list_per_page = 50
    save_on_top = True

    actions = (
        "activate_selected",
        "deactivate_selected",
        "lock_accounts",
        "unlock_accounts",
    )

    fieldsets = (
        (
            "اطلاعات کاربری",
            {
                "fields": (
                    "username",
                    "password",
                    "is_active",
                    "is_online",
                )
            },
        ),
        (
            "اطلاعات هویتی",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "full_name",
                    "national_code",
                    "gender",
                    "birth_date",
                    "place_of_birth",
                    "nationality",
                    "is_foreign",
                )
            },
        ),
        (
            "اطلاعات تماس",
            {
                "fields": (
                    "postal_code",
                    "emergency_phone",
                )
            },
        ),
        (
            "وضعیت حساب",
            {
                "fields": (
                    "is_email_verified",
                    "failed_login",
                    "account_locked",
                    "last_login_at",
                )
            },
        ),
        (
            "اطلاعات تکمیلی",
            {
                "fields": (
                    "preferred_language",
                    "religion",
                    "marital_status",
                    "security_question",
                    "security_answer",
                )
            },
        ),
    )

    @admin.action(description="فعال سازی کاربران انتخاب شده")
    def activate_selected(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} کاربر فعال شد.")

    @admin.action(description="غیرفعال سازی کاربران انتخاب شده")
    def deactivate_selected(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} کاربر غیرفعال شد.")

    @admin.action(description="قفل کردن حساب های انتخاب شده")
    def lock_accounts(self, request, queryset):
        updated = queryset.update(account_locked=True)
        self.message_user(request, f"{updated} حساب قفل شد.")

    @admin.action(description="باز کردن حساب های انتخاب شده")
    def unlock_accounts(self, request, queryset):
        updated = queryset.update(account_locked=False)
        self.message_user(request, f"{updated} حساب باز شد.")



# =============================================================================
# Tendency , Soheil Aliasghary
# =============================================================================

class ClassByTendencyInline(admin.TabularInline):
    model = Class
    fk_name = "tendency"
    extra = 0
    show_change_link = True
    fields = (
        "class_number",
        "lesson",
        "term",
        "class_day",
        "class_time",
        "class_location",
        "max_capacity",
    )
    readonly_fields = (
        "class_number",
    )

class TendencyByEducationBranchInline(admin.TabularInline):
    model = Tendency
    fk_name = "field"
    fields = (
        "tendency_code",
        "tendency_name",
    )

@admin.register(EducationBranch)
class EducationBranchAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "department",
        "degree_level",
    )

    list_display_links = (
        "title",
       "department",

    )

    list_filter = (
        "department",
    )

    search_help_text = (
        "جستجو بر اساس عنوان رشته تحصیلی"
    )

    search_fields = (
        "title",
    )

    inlines = (TendencyByEducationBranchInline,)


   


@admin.register(Tendency)
class TendencyAdmin(admin.ModelAdmin):

    list_display = (
        "tendency_code",
        "tendency_name",
        "total_units",
        "is_active",
        "class_count",
    )

    list_display_links = (
        "tendency_code",
        "tendency_name",
    )

    list_filter = (
        "is_active",
        "field",
    )

    search_fields = (
        "tendency_code",
        "tendency_name",
    )

    search_help_text = (
        "جستجو بر اساس کد گرایش و نام گرایش"
    )

    ordering = (
        "tendency_name",
    )

    list_per_page = 50
    save_on_top = True

    actions = (
        "activate_selected",
        "deactivate_selected",
    )

    inlines = (ClassByTendencyInline,)

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "tendency_code",
                    "tendency_name",
                    "field",
                )
            }
        ),

        (
            "جزئیات",
            {
                "fields": (
                    "total_units",
                    "is_active",
                    "description",
                )
            }
        ),
    )

    @admin.display(description="تعداد کلاس‌ها")
    def class_count(self, obj):
        return obj.classes.count()

    @admin.action(description="فعال سازی گرایش‌های انتخاب شده")
    def activate_selected(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} گرایش فعال شد.")

    @admin.action(description="غیرفعال سازی گرایش‌های انتخاب شده")
    def deactivate_selected(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} گرایش غیرفعال شد.")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("classes")
        )

# =============================================================================
# Term , Soheil Aliasghary
# =============================================================================

class ClassByTermInline(admin.TabularInline):
    model = Class
    fk_name = "term"
    extra = 0
    show_change_link = True
    fields = (
        "class_number",
        "lesson",
        "tendency",
        "class_day",
        "class_time",
        "class_location",
        "max_capacity",
    )
    readonly_fields = (
        "class_number",
    )


class ClassOfferByTermInline(admin.TabularInline):
    model = ClassOffer
    fk_name = "term"
    extra = 0
    show_change_link = True
    fields = (
        "class_group",
        "teacher",
    )


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):

    list_display = (
        "term_id",
        "term_title",
        "start_term",
        "end_term",
        "is_current",
        "registration_start",
        "class_count",
    )

    list_display_links = (
        "term_id",
        "term_title",
    )

    list_filter = (
        "is_current",
    )

    search_fields = (
        "term_id",
        "term_title",
        "name",
    )

    search_help_text = (
        "جستجو بر اساس شناسه ترم، عنوان ترم و نام ترم"
    )

    ordering = (
        "-term_id",
    )

    list_per_page = 50
    save_on_top = True

    actions = (
        "set_as_current",
        "unset_as_current",
    )

    inlines = (
        ClassByTermInline,
        ClassOfferByTermInline,
    )

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "term_id",
                    "term_title",
                    "name",
                    "is_current",
                )
            }
        ),
        (
            "بازه زمانی",
            {
                "fields": (
                    "start_term",
                    "end_term",
                    "registration_start",
                )
            }
        ),
    )

    @admin.display(description="تعداد کلاس‌ها")
    def class_count(self, obj):
        return obj.classes.count()

    @admin.action(description="تنظیم به عنوان ترم جاری")
    def set_as_current(self, request, queryset):
        Term.objects.update(is_current=False)
        updated = queryset.update(is_current=True)
        self.message_user(request, f"{updated} ترم به عنوان ترم جاری تنظیم شد.")

    @admin.action(description="حذف از ترم جاری")
    def unset_as_current(self, request, queryset):
        updated = queryset.update(is_current=False)
        self.message_user(request, f"{updated} ترم از حالت جاری خارج شد.")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "classes",
                "classoffer_set",
            )
        )
# =============================================================================
# Internship , Fateme Ganji
# =============================================================================

@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "company",
        "start_date",
        "finish_date",
        "evaluation_score",
    )

    list_display_links = (
        "student",
        "company",
    )

    list_filter = (
        "evaluation_score",
        "start_date",
    )

    search_fields = (
        "student__student_number",
        "company__name",
    )

    search_help_text = (
        "جستجو بر اساس شماره دانشجویی یا نام شرکت"
    )

    ordering = (
        "-start_date",
    )

    list_per_page = 50
    save_on_top = True

    fieldsets = (
        (
            "اطلاعات کارآموزی",
            {
                "fields": (
                    "student",
                    "company",
                    "start_date",
                    "finish_date",
                    "evaluation_score",
                )
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("student", "company")
        )
        
# =============================================================================
# Payments , Fateme Ganji
# =============================================================================
@admin.register(StudentPayments)
class StudentPaymentsAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "amount",
        "payment_datetime",
        "is_confirmed",
        "tracking_code",
        "reference_bank",
        "payment_method",
        "installment_count",
    )

    list_display_links = ("tracking_code",)

    list_filter = (
        "is_confirmed",
        "payment_method",
    )

    search_fields = (
        "tracking_code",
        "reference_bank",
        "student__student_number",
    )

    search_help_text = "جستجو بر اساس کد پیگیری، بانک مرجع یا شماره دانشجویی"

    ordering = ("-payment_datetime",)

    list_per_page = 50
    save_on_top = True

    fieldsets = (
        (
            "دانشجو",
            {"fields": ("student",)},
        ),
        (
            "اطلاعات پرداخت",
            {
                "fields": (
                    "amount",
                    "payment_datetime",
                    "payment_method",
                    "installment_count",
                ),
            },
        ),
        (
            "وضعیت",
            {
                "fields": (
                    "is_confirmed",
                    "tracking_code",
                    "reference_bank",
                ),
            },
        ),
    )

    actions = ("confirm_payments",)

    @admin.action(description="تأیید پرداخت‌های انتخاب‌شده")
    def confirm_payments(self, request, queryset):
        updated = queryset.update(is_confirmed=True)
        self.message_user(request, f"{updated} پرداخت تأیید شد.")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("student")
            
# =============================================================================
# Employee Reyhaneh Jahanbakhsh
# =============================================================================
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):

    list_display = (
        "employee_code",
        "person",
        "department",
        "position",
        "supervisor",
        "employment_type",
        "salary",
        "hire_date",
        "active_status",
    )

    list_display_links = (
        "employee_code",
        "person",
    )

    list_filter = (
        "is_active",
        "department",
        "position",
        "employment_type",
        "work_shift",
        ("hire_date", admin.DateFieldListFilter),
    )

    search_fields = (
        "employee_code",
        "personnel_code",
        "person__username",
        "person__full_name",
        "person__first_name",
        "person__last_name",
        "first_name",
        "last_name",
        "department__department_title",
        "insurance_number",
        "bank_account_number",
    )

    search_help_text = (
        "جستجو بر اساس کد پرسنلی، نام کارمند، نام کاربری، دانشکده، شماره بیمه و شماره حساب"
    )

    autocomplete_fields = (
        "person",
        "department",
        "position",
        "employment_type",
        "work_shift",
        "supervisor",
    )

    list_select_related = (
        "person",
        "department",
        "position",
        "employment_type",
        "work_shift",
        "supervisor",
    )

    ordering = (
        "employee_code",
    )

    list_per_page = 50
    save_on_top = True

    actions = (
        "activate_selected",
        "deactivate_selected",
    )

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "person",
                    "employee_code",
                    "personnel_code",
                    "department",
                )
            }
        ),

        (
            "اطلاعات شغلی",
            {
                "fields": (
                    "position",
                    "employment_type",
                    "work_shift",
                    "supervisor",
                    "hire_date",
                )
            }
        ),

        (
            "اطلاعات مالی",
            {
                "fields": (
                    "salary",
                    "overtime_hours",
                    "bank_account_number",
                    "insurance_number",
                )
            }
        ),

        (
            "اطلاعات تکمیلی",
            {
                "fields": (
                    "office_room_number",
                    "first_name",
                    "last_name",
                )
            }
        ),

        (
            "وضعیت",
            {
                "fields": (
                    "is_active",
                )
            }
        ),
    )

    @admin.display(boolean=True, description="فعال")
    def active_status(self, obj):
        return obj.is_active

    @admin.action(description="فعال سازی کارکنان انتخاب شده")
    def activate_selected(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f"{updated} کارمند فعال شد."
        )

    @admin.action(description="غیرفعال سازی کارکنان انتخاب شده")
    def deactivate_selected(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"{updated} کارمند غیرفعال شد."
        )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "person",
                "department",
                "position",
                "employment_type",
                "work_shift",
                "supervisor",
                "supervisor__person",
            )
        )

# =============================================================================
# Student , Nima Movahedi
# =============================================================================

class StudentClassInline(admin.TabularInline):
    model = Class
    fk_name = "student"
    extra = 0
    show_change_link = True

    fields = (
        "class_group",
        "final_score",
        "attendance_count",
        "is_passed",
        "register_date",
    )

    readonly_fields = (
        "register_date",
    )
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        "student_number",
        "full_name",
        "department",
        "branch",
        "tendency",
        "entry_year",
        "gpa",
        "is_active",
        "graduation_status",
    )

    list_display_links = (
        "student_number",
        "full_name",
    )

    list_filter = (
        "is_active",
        "graduation_status",
        "department",
        "branch",
        "tendency",
        "entry_year",
        "military_status",
        "payment_type",
        "dormitory_status",
    )

    search_fields = (
        "student_number",
        "first_name",
        "last_name",
        "educational_email",
        "person__first_name",
        "person__last_name",
        "person__national_code",
    )

    search_help_text = (
        "جستجو بر اساس شماره دانشجویی، نام، نام خانوادگی و کد ملی"
    )

    list_select_related = (
        "person",
        "department",
        "branch",
        "tendency",
        "advisor_teacher",
        "blood_type",
    )

    ordering = (
        "student_number",
    )

    list_per_page = 50
    save_on_top = True

    actions = (
        "activate_students",
        "deactivate_students",
        "graduate_students",
        "ungraduate_students",
    )

    fieldsets = (
        (
            "اطلاعات دانشجو",
            {
                "fields": (
                    "person",
                    "student_number",
                    "entry_year",
                    "department",
                    "branch",
                    "tendency",
                )
            }
        ),
        (
            "اطلاعات آموزشی",
            {
                "fields": (
                    "gpa",
                    "current_term_gpa",
                    "gpa_rank",
                    "taken_units",
                    "academic_warning_count",
                    "advisor_teacher",
                    "expected_graduation_date",
                )
            }
        ),
        (
            "وضعیت دانشجو",
            {
                "fields": (
                    "is_active",
                    "graduation_status",
                    "dormitory_status",
                    "military_status",
                    "payment_type",
                )
            }
        ),
        (
            "اطلاعات تماس",
            {
                "fields": (
                    "educational_email",
                    "emergency_contact_name",
                    "emergency_contact_relation",
                    "blood_type",
                )
            }
        ),
    )

    @admin.display(description="نام دانشجو")
    def full_name(self, obj):
        if obj.person:
            return str(obj.person)

        return f"{obj.first_name} {obj.last_name}".strip()

    @admin.action(description="فعال کردن دانشجویان")
    def activate_students(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} دانشجو فعال شد.")

    @admin.action(description="غیرفعال کردن دانشجویان")
    def deactivate_students(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} دانشجو غیرفعال شد.")

    @admin.action(description="فارغ‌التحصیل کردن")
    def graduate_students(self, request, queryset):
        updated = queryset.update(graduation_status=True)
        self.message_user(request, f"{updated} دانشجو فارغ‌التحصیل شد.")

    @admin.action(description="لغو فارغ‌التحصیلی")
    def ungraduate_students(self, request, queryset):
        updated = queryset.update(graduation_status=False)
        self.message_user(request, f"{updated} دانشجو بروزرسانی شد.")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "person",
                "department",
                "branch",
                "tendency",
                "advisor_teacher",
                "blood_type",
            )
        )