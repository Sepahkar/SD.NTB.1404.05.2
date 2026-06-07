from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import ConstValue
from .models import Lesson
from .models import  Class
from .models import ClassOffer
from .models import Department
from .models import Person


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