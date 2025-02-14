
from rest_framework.pagination import PageNumberPagination


def paginate_and_serialize(queryset, request, serializer_class, page_size):
    paginator = PageNumberPagination()
    paginator.page_size = page_size
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = serializer_class(paginated_queryset, many=True)
    return paginator.get_paginated_response({"status": True, "page_size": paginator.page_size, "data": serializer.data})
