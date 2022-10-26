class AllowPackageTypes:
    @property
    def marketing(self) -> str:
        return "marketing"

    @property
    def personal(self) -> str:
        return "personal"


allow_package_types = AllowPackageTypes()
allow_package_types_list = [
    getattr(allow_package_types, key)
    for key in dir(allow_package_types) if not key.startswith('__')
]
