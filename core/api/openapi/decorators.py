"""Reusable drf-spectacular decorators for Persian API documentation."""

from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view

COMMON_LIST_PARAMS = [
    OpenApiParameter(
        name="page",
        type=int,
        location=OpenApiParameter.QUERY,
        description="شماره صفحه (پیش‌فرض: ۱)",
        required=False,
    ),
    OpenApiParameter(
        name="page_size",
        type=int,
        location=OpenApiParameter.QUERY,
        description="تعداد رکورد در هر صفحه (پیش‌فرض: ۲۰، حداکثر: ۱۰۰)",
        required=False,
    ),
    OpenApiParameter(
        name="search",
        type=str,
        location=OpenApiParameter.QUERY,
        description="جستجو در فیلدهای متنی قابل جستجو",
        required=False,
    ),
    OpenApiParameter(
        name="ordering",
        type=str,
        location=OpenApiParameter.QUERY,
        description="مرتب‌سازی (مثال: -created_at یا name)",
        required=False,
    ),
]


def tagged_viewset(tag: str, fa_name: str, *, extra_list_params=None):
    """Apply Persian OpenAPI docs to a standard ModelViewSet."""

    list_params = list(COMMON_LIST_PARAMS)
    if extra_list_params:
        list_params.extend(extra_list_params)

    auth_note = (
        "نیاز به احراز هویت دارد. هدر Authorization: Token <session_key> "
        "یا کوکی نشست Django را ارسال کنید."
    )

    return extend_schema_view(
        list=extend_schema(
            tags=[tag],
            summary=f"فهرست {fa_name}",
            description=(
                f"دریافت لیست paginated از {fa_name}.\n\n"
                f"{auth_note}\n\n"
                "پاسخ شامل فیلدهای count، next، previous و results است."
            ),
            parameters=list_params,
        ),
        create=extend_schema(
            tags=[tag],
            summary=f"ایجاد {fa_name}",
            description=(
                f"ثبت رکورد جدید {fa_name}.\n\n"
                f"{auth_note}\n\n"
                "بدنه درخواست باید مطابق schema مدل باشد."
            ),
        ),
        retrieve=extend_schema(
            tags=[tag],
            summary=f"جزئیات {fa_name}",
            description=(
                f"دریافت یک رکورد {fa_name} با شناسه.\n\n"
                f"{auth_note}"
            ),
        ),
        update=extend_schema(
            tags=[tag],
            summary=f"بروزرسانی کامل {fa_name}",
            description=(
                f"جایگزینی کامل فیلدهای {fa_name}.\n\n"
                f"{auth_note}"
            ),
        ),
        partial_update=extend_schema(
            tags=[tag],
            summary=f"بروزرسانی جزئی {fa_name}",
            description=(
                f"بروزرسانی بخشی از فیلدهای {fa_name}.\n\n"
                f"{auth_note}"
            ),
        ),
        destroy=extend_schema(
            tags=[tag],
            summary=f"حذف {fa_name}",
            description=(
                f"حذف رکورد {fa_name}.\n\n"
                f"{auth_note}"
            ),
        ),
    )


def tagged_readonly_viewset(tag: str, fa_name: str, *, extra_list_params=None):
    """Apply Persian OpenAPI docs to a ReadOnlyModelViewSet."""

    list_params = list(COMMON_LIST_PARAMS)
    if extra_list_params:
        list_params.extend(extra_list_params)

    auth_note = (
        "نیاز به احراز هویت دارد. هدر Authorization: Token <session_key> "
        "یا کوکی نشست Django را ارسال کنید."
    )

    return extend_schema_view(
        list=extend_schema(
            tags=[tag],
            summary=f"فهرست {fa_name}",
            description=(
                f"دریافت لیست paginated از {fa_name}.\n\n"
                f"{auth_note}\n\n"
                "پاسخ شامل فیلدهای count، next، previous و results است."
            ),
            parameters=list_params,
        ),
        retrieve=extend_schema(
            tags=[tag],
            summary=f"جزئیات {fa_name}",
            description=(
                f"دریافت یک رکورد {fa_name} با شناسه.\n\n"
                f"{auth_note}"
            ),
        ),
    )
