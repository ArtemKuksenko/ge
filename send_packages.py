from datetime import datetime

from pydantic import ValidationError

from utils import get_day_from_date
from validators.send_package_const import send_package_data_const as spc
from validators.send_package_const import send_package_data_const_keys
from validators.send_package_data import SendPackageData


class SendPackages:
    def __init__(self):
        self._send_package_queue = []

    @staticmethod
    def _valid_send_package(data: dict) -> None | SendPackageData:
        if set(data.keys()) - send_package_data_const_keys:
            return

        try:
            return SendPackageData(**data)
        except ValidationError:
            return

    def _add_request_to_send_packages(
            self, queue_row: tuple[dict, datetime]
    ) -> None:
        self._send_package_queue.append(queue_row)

    def __clean_send_packages_from_queue(
            self, data: list[tuple[dict, datetime]]
    ) -> None:
        self._send_package_queue = [
            row for row in self._send_package_queue
            if row not in data
        ]

    def _get_first_packaged_clean_count(
            self, package_id: int, tm: datetime
    ) -> tuple[dict, int]:
        day = get_day_from_date(tm)
        packages = [
            row for row in self._send_package_queue
            if all([
                row[0][spc.package_id] == package_id,
                get_day_from_date(row[0][spc.tm]) == day
            ])
        ]
        if not packages:
            raise Exception(f"No package by {package_id}")

        packages.sort(key=lambda row: row[0][spc.tm])
        res = packages.pop(0)

        self.__clean_send_packages_from_queue(packages + [res])
        return res, len(packages)
