-- Applies to the pre-existing DOTX cloud schema, not a fresh empty database.
-- RLS does not restrict TRUNCATE. Remove unnecessary non-CRUD table privileges.
REVOKE TRUNCATE, REFERENCES, TRIGGER ON TABLE
    public.profiles,
    public.reading_list,
    public.user_bookmarks,
    public.user_devices,
    public.user_history_optin,
    public.user_settings
FROM authenticated;
