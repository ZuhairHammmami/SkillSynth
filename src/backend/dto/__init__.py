"""DTO package — four modules over the 15-table reduced schema.

auth.py (identity), catalog.py (catalog), learning.py (learning),
admin.py (admin + engagement feed). Re-exports keep the historical
`from backend.dto import X` import style used by routers.
"""

from backend.dto.auth import (
    PasswordValidator, RegisterInput, ProfileOut, ProfileUpdate,
    PasswordChange, ResetRequest, ResetConfirm, Token,
)
from backend.dto.catalog import (
    CategoryCreate, CategoryOut, CategoryUpdate,
    SkillCreate, SkillOut, SkillUpdate,
    ResourceCreate, ResourceOut, ResourceUpdate,
    JobRoleCreate, JobRoleOut, JobRoleUpdate,
)
from backend.dto.learning import (
    WizardRoleInfo, WizardPreferencesOptions, WizardOptionsOut,
    DetailedPreferences, GeneratePathIn, StepResource, StepOut,
    PathOut, PathDetailOut, ProgressPathOut, ProgressDashboardOut,
    StepCompletionResponse, GraphNode, GraphEdge, GraphCategory,
    GraphOut, GapPrerequisite, GapItem, GapsOut, RecommendationItem,
    RecommendationsOut, GeneratedPathSummary, PathSkillsUpdate, PathUpdate,
)
from backend.dto.admin import (
    AdminCreateUser, AdminUserUpdate, AdminUserOut,
    UserActivityReport, ContentEngagementReport, SystemHealthReport,
    PathAdminView, EventUserInfo, ActivityItemOut,
    AggregatedReportOut, AdminDashboardResponse,
)

__all__ = [
    "PasswordValidator", "RegisterInput", "ProfileOut", "ProfileUpdate",
    "PasswordChange", "ResetRequest", "ResetConfirm", "Token",
    "CategoryCreate", "CategoryOut", "CategoryUpdate",
    "SkillCreate", "SkillOut", "SkillUpdate",
    "ResourceCreate", "ResourceOut", "ResourceUpdate",
    "JobRoleCreate", "JobRoleOut", "JobRoleUpdate",
    "WizardRoleInfo", "WizardPreferencesOptions", "WizardOptionsOut",
    "DetailedPreferences", "GeneratePathIn", "StepResource", "StepOut",
    "PathOut", "PathDetailOut", "ProgressPathOut", "ProgressDashboardOut",
    "StepCompletionResponse", "GraphNode", "GraphEdge", "GraphCategory",
    "GraphOut", "GapPrerequisite", "GapItem", "GapsOut",
    "RecommendationItem", "RecommendationsOut", "GeneratedPathSummary",
    "PathSkillsUpdate", "PathUpdate",
    "AdminCreateUser", "AdminUserUpdate", "AdminUserOut",
    "UserActivityReport", "ContentEngagementReport", "SystemHealthReport",
    "PathAdminView", "EventUserInfo", "ActivityItemOut",
    "AggregatedReportOut", "AdminDashboardResponse",
]
