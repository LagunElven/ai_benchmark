# Billing window and daylight saving time

Fix `BillingWindow.elapsedHours`. It receives local date-times in one named time zone
and must return the elapsed number of whole hours between them. The result must account
for the zone's daylight-saving gap or overlap, not merely subtract the wall-clock
fields. Reject null arguments, a null zone, or an end that is not after the start.

Keep the existing API, do not modify tests, and change only the implementation file.
Return a `file_changes_v1` response.
