"""Scenario content catalog for the 96-scenario pilot."""

from __future__ import annotations

from dataclasses import dataclass

from proofpath.benchmark.models import Domain


@dataclass(frozen=True)
class TaskTemplate:
    archetype: str
    noun: str
    field: str
    initial: object
    target: object
    verb: str


CATALOG: dict[Domain, tuple[TaskTemplate, ...]] = {
    Domain.FILESYSTEM: (
        TaskTemplate("replace_content", "file", "content", "draft-v1", "approved-v2", "replace"),
        TaskTemplate("rename", "file", "name", "notes.tmp", "notes.txt", "rename"),
        TaskTemplate("set_owner", "file", "owner", "team-red", "team-blue", "change"),
        TaskTemplate("set_mode", "file", "mode", "read-only", "read-write", "change"),
        TaskTemplate("set_tag", "file", "tag", "draft", "released", "retag"),
        TaskTemplate("move_folder", "file", "folder", "/incoming", "/processed", "move"),
        TaskTemplate("set_encoding", "file", "encoding", "latin-1", "utf-8", "convert"),
        TaskTemplate("archive", "file", "archived", False, True, "archive"),
        TaskTemplate("set_checksum", "file", "checksum", "sha-old", "sha-new", "update"),
        TaskTemplate("set_retention", "file", "retention_days", 7, 30, "change"),
        TaskTemplate("set_visibility", "file", "visibility", "team", "private", "change"),
        TaskTemplate("set_version", "file", "release", "1.0", "1.1", "promote"),
    ),
    Domain.DATABASE: (
        TaskTemplate("update_status", "record", "status", "pending", "approved", "update"),
        TaskTemplate("assign_owner", "record", "owner", "queue-a", "queue-b", "assign"),
        TaskTemplate("change_priority", "record", "priority", 2, 4, "change"),
        TaskTemplate("correct_region", "record", "region", "north", "south", "correct"),
        TaskTemplate("set_active", "record", "active", False, True, "activate"),
        TaskTemplate("update_limit", "record", "limit", 10, 25, "update"),
        TaskTemplate("set_category", "record", "category", "general", "special", "classify"),
        TaskTemplate("update_version", "record", "version_label", "v1", "v2", "update"),
        TaskTemplate("correct_code", "record", "code", "X-100", "X-101", "correct"),
        TaskTemplate("set_reviewed", "record", "reviewed", False, True, "mark"),
        TaskTemplate("change_queue", "record", "queue", "intake", "resolved", "move"),
        TaskTemplate("set_expiry", "record", "expiry_day", 10, 20, "extend"),
    ),
    Domain.PROFILE: (
        TaskTemplate("update_city", "profile", "city", "Houston", "Dallas", "update"),
        TaskTemplate("update_phone", "profile", "phone", "555-0100", "555-0199", "update"),
        TaskTemplate("update_locale", "profile", "locale", "en-US", "es-US", "change"),
        TaskTemplate("update_timezone", "profile", "timezone", "UTC", "America/Chicago", "change"),
        TaskTemplate("set_contact", "profile", "contact_method", "email", "sms", "change"),
        TaskTemplate("update_postal", "profile", "postal_code", "77001", "75201", "correct"),
        TaskTemplate("set_alerts", "profile", "alerts_enabled", False, True, "enable"),
        TaskTemplate("update_language", "profile", "language", "English", "Spanish", "change"),
        TaskTemplate("set_access", "profile", "access_tier", "basic", "standard", "change"),
        TaskTemplate("update_name", "profile", "display_name", "A. Rivera", "Alex Rivera", "update"),
        TaskTemplate("set_digest", "profile", "digest", "weekly", "daily", "change"),
        TaskTemplate("set_units", "profile", "units", "imperial", "metric", "change"),
    ),
    Domain.CALENDAR: (
        TaskTemplate("reschedule_day", "event", "day", "2026-10-05", "2026-10-06", "reschedule"),
        TaskTemplate("reschedule_time", "event", "time", "09:00", "10:30", "reschedule"),
        TaskTemplate("change_room", "event", "room", "R-101", "R-202", "move"),
        TaskTemplate("set_title", "event", "title", "Draft Review", "Final Review", "rename"),
        TaskTemplate("set_duration", "event", "duration_minutes", 30, 45, "extend"),
        TaskTemplate("cancel", "event", "status", "scheduled", "cancelled", "cancel"),
        TaskTemplate("restore", "event", "status", "cancelled", "scheduled", "restore"),
        TaskTemplate("set_visibility", "event", "visibility", "public", "private", "change"),
        TaskTemplate("set_host", "event", "host", "user-1", "user-2", "reassign"),
        TaskTemplate("set_reminder", "event", "reminder_minutes", 10, 30, "change"),
        TaskTemplate("set_conference", "event", "conference", "none", "mock-video", "add"),
        TaskTemplate("set_capacity", "event", "capacity", 10, 20, "increase"),
    ),
    Domain.MESSAGING: (
        TaskTemplate("change_subject", "message", "subject", "Draft", "Approved", "change"),
        TaskTemplate("change_body", "message", "body", "old text", "revised text", "replace"),
        TaskTemplate("queue", "message", "status", "draft", "queued", "queue"),
        TaskTemplate("cancel", "message", "status", "queued", "cancelled", "cancel"),
        TaskTemplate("set_channel", "message", "channel", "email-mock", "chat-mock", "change"),
        TaskTemplate("set_priority", "message", "priority", "normal", "high", "change"),
        TaskTemplate("set_template", "message", "template", "welcome-a", "welcome-b", "change"),
        TaskTemplate("set_sender", "message", "sender", "bot-a", "bot-b", "change"),
        TaskTemplate("set_expiry", "message", "expiry_hours", 24, 48, "extend"),
        TaskTemplate("set_locale", "message", "locale", "en", "fr", "translate"),
        TaskTemplate("set_tracking", "message", "tracking", False, True, "enable"),
        TaskTemplate("set_batch", "message", "batch", "batch-1", "batch-2", "move"),
    ),
    Domain.CONFIGURATION: (
        TaskTemplate("feature_flag", "setting", "enabled", False, True, "enable"),
        TaskTemplate("change_limit", "setting", "limit", 100, 125, "increase"),
        TaskTemplate("change_route", "setting", "route", "cluster-a", "cluster-b", "reroute"),
        TaskTemplate("set_timeout", "setting", "timeout_ms", 1000, 1500, "change"),
        TaskTemplate("set_retries", "setting", "retries", 2, 3, "increase"),
        TaskTemplate("set_mode", "setting", "mode", "observe", "enforce", "change"),
        TaskTemplate("set_region", "setting", "region", "us-east", "us-central", "change"),
        TaskTemplate("set_cache", "setting", "cache", "off", "on", "enable"),
        TaskTemplate("set_level", "setting", "log_level", "info", "warning", "change"),
        TaskTemplate("set_pool", "setting", "pool_size", 4, 8, "increase"),
        TaskTemplate("set_version", "setting", "api_version", "v1", "v2", "upgrade"),
        TaskTemplate("set_rollout", "setting", "rollout_percent", 10, 25, "increase"),
    ),
    Domain.COMMERCE: (
        TaskTemplate("change_address", "order", "city", "Houston", "Dallas", "change"),
        TaskTemplate("change_quantity", "order", "quantity", 1, 2, "change"),
        TaskTemplate("set_hold", "order", "status", "open", "held", "hold"),
        TaskTemplate("release_hold", "order", "status", "held", "open", "release"),
        TaskTemplate("change_item", "order", "item", "sku-100", "sku-101", "replace"),
        TaskTemplate("set_shipping", "order", "shipping", "standard", "express", "change"),
        TaskTemplate("set_note", "order", "note", "none", "gift", "add"),
        TaskTemplate("set_warehouse", "order", "warehouse", "wh-a", "wh-b", "reroute"),
        TaskTemplate("set_packaging", "order", "packaging", "box", "recycled-box", "change"),
        TaskTemplate("set_window", "order", "delivery_window", "morning", "afternoon", "change"),
        TaskTemplate("set_contact", "order", "contact", "555-0100", "555-0199", "change"),
        TaskTemplate("set_pickup", "order", "fulfillment", "delivery", "pickup", "change"),
    ),
    Domain.SUBSCRIPTION: (
        TaskTemplate("change_plan", "subscription", "plan", "basic", "plus", "change"),
        TaskTemplate("pause", "subscription", "status", "active", "paused", "pause"),
        TaskTemplate("resume", "subscription", "status", "paused", "active", "resume"),
        TaskTemplate("cancel", "subscription", "status", "active", "cancelled", "cancel"),
        TaskTemplate("reactivate", "subscription", "status", "cancelled", "active", "reactivate"),
        TaskTemplate("set_cycle", "subscription", "cycle", "monthly", "annual", "change"),
        TaskTemplate("set_seats", "subscription", "seats", 2, 4, "increase"),
        TaskTemplate("set_region", "subscription", "region", "us-east", "us-central", "change"),
        TaskTemplate("set_addon", "subscription", "addon", "none", "reports", "add"),
        TaskTemplate("set_renewal", "subscription", "renewal", True, False, "disable"),
        TaskTemplate("set_tier", "subscription", "support_tier", "standard", "priority", "change"),
        TaskTemplate("set_notice", "subscription", "notice_days", 7, 14, "extend"),
    ),
}


def validate_catalog() -> None:
    if set(CATALOG) != set(Domain):
        raise ValueError("catalog must cover every domain")
    for domain, templates in CATALOG.items():
        if len(templates) != 12:
            raise ValueError(f"{domain.value} has {len(templates)} templates, expected 12")
        names = [template.archetype for template in templates]
        if len(names) != len(set(names)):
            raise ValueError(f"{domain.value} has duplicate archetypes")
