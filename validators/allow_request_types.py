class AllowRequestTypes:
    @property
    def send_package(self) -> str:
        return "send_package"

    @property
    def update_preference(self) -> str:
        return "update_preference"


allow_request_types = AllowRequestTypes()
