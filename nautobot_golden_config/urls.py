"""Django urlpatterns declaration for config compliance plugin."""
from django.urls import path

from nautobot.extras.views import ObjectChangeLogView
from . import views, models

app_name = "nautobot_golden_config"

urlpatterns = [
    path("golden/", views.GoldenConfigurationListView.as_view(), name="goldenconfiguration_list"),
    path("golden/delete/", views.GoldenConfigurationBulkDeleteView.as_view(), name="goldenconfiguration_bulk_delete"),
    path("config-compliance/", views.ConfigComplianceListView.as_view(), name="configcompliance_list"),
    path("config-compliance/delete/", views.ConfigComplianceBulkDeleteView.as_view(), name="compliance_bulk_delete"),
    path("config-compliance/overview/", views.ConfigComplianceOverview.as_view(), name="configcompliance_report"),
    path("config-compliance/<uuid:pk>", views.ConfigComplianceView.as_view(), name="configcompliance"),
    path(
        "config-compliance/<uuid:pk>/delete/",
        views.ConfigComplianceDeleteView.as_view(),
        name="configcompliance_delete",
    ),
    path(
        "config-compliance/<uuid:pk>/<str:config_type>/",
        views.ConfigComplianceDetails.as_view(),
        name="configcompliance_details",
    ),
    path(
        "config-compliance/filtered/<uuid:pk>/<str:compliance>/",
        views.ComplianceDeviceFilteredReport.as_view(),
        name="configcompliance_filter_report",
    ),
    path("compliance-rules/", views.ComplianceRuleListView.as_view(), name="compliancerule_list"),
    path("compliance-rules/add/", views.ComplianceRuleEditView.as_view(), name="compliancerule_add"),
    path(
        "compliance-rules/delete/",
        views.ComplianceRuleBulkDeleteView.as_view(),
        name="compliancerule_bulk_delete",
    ),
    path("compliance-rules/<uuid:pk>/edit/", views.ComplianceRuleEditView.as_view(), name="compliancerule_edit"),
    path(
        "compliance-rules/<uuid:pk>/delete/",
        views.ComplianceRuleDeleteView.as_view(),
        name="compliancerule_delete",
    ),
    path("compliance-features/", views.ComplianceFeatureListView.as_view(), name="compliancefeature_list"),
    path("compliance-features/add/", views.ComplianceFeatureEditView.as_view(), name="compliancefeature_add"),
    path(
        "compliance-features/delete/",
        views.ComplianceFeatureBulkDeleteView.as_view(),
        name="compliancefeature_bulk_delete",
    ),
    path(
        "compliance-features/<uuid:pk>/edit/", views.ComplianceFeatureEditView.as_view(), name="compliancefeature_edit"
    ),
    path(
        "compliance-features/<uuid:pk>/delete/",
        views.ComplianceFeatureDeleteView.as_view(),
        name="compliancefeature_delete",
    ),
    path("settings/", views.GoldenConfigSettingsView.as_view(), name="goldenconfigsettings"),
    path("settings/edit/", views.GoldenConfigSettingsEditView.as_view(), name="goldenconfigsettings_edit"),
    path(
        "settings/changelog/",
        ObjectChangeLogView.as_view(),
        name="goldenconfigsettings_changelog",
        kwargs={"model": models.GoldenConfigSettings},
    ),
    path("line-removal/", views.ConfigRemoveListView.as_view(), name="configremove_list"),
    path("line-removal/add/", views.ConfigRemoveEditView.as_view(), name="configremove_add"),
    path(
        "line-removal/import/",
        views.ConfigRemoveBulkImportView.as_view(),
        name="configremove_import",
    ),
    path(
        "line-removal/edit/",
        views.ConfigRemoveBulkEditView.as_view(),
        name="configremove_bulk_edit",
    ),
    path(
        "line-removal/delete/",
        views.ConfigRemoveBulkDeleteView.as_view(),
        name="configremove_bulk_delete",
    ),
    path("line-removal/<uuid:pk>/", views.ConfigRemoveView.as_view(), name="configremove"),
    path(
        "line-removal/<uuid:pk>/edit/",
        views.ConfigRemoveEditView.as_view(),
        name="configremove_edit",
    ),
    path("line-replace/", views.ConfigReplaceListView.as_view(), name="configreplace_list"),
    path("line-replace/add/", views.ConfigReplaceEditView.as_view(), name="configreplace_add"),
    path("line-replace/import/", views.ConfigReplaceBulkImportView.as_view(), name="configreplace_import"),
    path("line-replace/edit/", views.ConfigReplaceBulkEditView.as_view(), name="configreplace_bulk_edit"),
    path(
        "line-replace/delete/",
        views.ConfigReplaceBulkDeleteView.as_view(),
        name="configreplace_bulk_delete",
    ),
    path("line-replace/<uuid:pk>/", views.ConfigReplaceView.as_view(), name="configreplace"),
    path("line-replace/<uuid:pk>/edit/", views.ConfigReplaceEditView.as_view(), name="configreplace_edit"),
    path(
        "line-replace/delete/",
        views.ConfigReplaceBulkDeleteView.as_view(),
        name="configreplace_bulk_delete",
    ),
]
