from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        if hasattr(queryset, "query") and not queryset.query.order_by:
            queryset = queryset.order_by("pk")
        return super().paginate_queryset(queryset, request, view=view)
