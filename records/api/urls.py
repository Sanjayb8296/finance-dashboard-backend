from django.urls import path

from records.api.views import (
    RecordBulkCreateView,
    RecordDetailView,
    RecordExportView,
    RecordListCreateView,
)

urlpatterns = [
    path("records/", RecordListCreateView.as_view(), name="record-list-create"),
    path("records/bulk/", RecordBulkCreateView.as_view(), name="record-bulk-create"),
    path("records/export/", RecordExportView.as_view(), name="record-export"),
    path("records/<int:record_id>/", RecordDetailView.as_view(), name="record-detail"),
]
