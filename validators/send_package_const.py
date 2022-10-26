class SendPackageDataConst:
    @property
    def action(self) -> str:
        return "action"

    @property
    def sender(self) -> str:
        return "sender_id"

    @property
    def recipient(self) -> str:
        return "recipient_id"

    @property
    def package_id(self) -> str:
        return "package_id"

    @property
    def package_type(self) -> str:
        return "package_type"

    @property
    def tm(self) -> str:
        return "timestamp"


send_package_data_const = SendPackageDataConst()
send_package_data_const_keys = {
    getattr(send_package_data_const, key)
    for key in dir(send_package_data_const) if not key.startswith('__')
}
