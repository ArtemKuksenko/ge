class UpdatePreferenceConst:
    @property
    def action(self) -> str:
        return "action"

    @property
    def recipient(self) -> str:
        return "recipient_id"

    @property
    def personal_package(self) -> str:
        return "personal"

    @property
    def marketing_package(self) -> str:
        return "marketing"

    @property
    def tm(self) -> str:
        return "timestamp"


update_preference_const = UpdatePreferenceConst()
update_preference_const_keys = {
    getattr(update_preference_const, key)
    for key in dir(update_preference_const) if not key.startswith('__')
}
