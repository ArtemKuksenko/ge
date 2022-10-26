from asyncio import sleep
from datetime import datetime

import ujson as json
from ujson import JSONDecodeError

from send_packages import SendPackages
from settings import settings
from update_preference import UpdatePreference
from utils import get_day_from_date
from validators.allow_request_types import allow_request_types as rt
from validators.send_package_const import send_package_data_const as spc
from validators.send_package_data import SendPackageData
from validators.update_preference_const import update_preference_const as upc
from validators.update_preference_data import UpdatePreferenceData


class GalaxyExpress(SendPackages, UpdatePreference):
    def __init__(self):
        SendPackages.__init__(self)
        UpdatePreference.__init__(self)
        self._packages_delivered = 0
        self._packages_dropped = 0
        self.finished = False

    async def get_request(self, input_s: str) -> None:
        try:
            data = json.loads(input_s)
        except JSONDecodeError:
            return

        valid_data = self._valid_data(data)
        if not valid_data:
            return
        data[spc.tm] = getattr(valid_data, spc.tm)
        self._add_request_to_requests_queue(data)

    async def process_send_packages(self) -> None:
        while not self.finished:
            await sleep(0.05)
            if not self._send_package_queue:
                continue
            row, request_coming = self._send_package_queue[0]
            duration_time = datetime.utcnow() - request_coming
            if duration_time.total_seconds() > settings.time_out:
                await self._process_send_package(
                    row[spc.package_id], row[spc.tm]
                )

    async def package_sending_finish(self) -> None:
        self._send_package_queue.sort(key=lambda row: row[0][spc.tm])
        if self._send_package_queue:
            row, _ = self._send_package_queue[0]
            await self._process_send_package(row[spc.package_id], row[spc.tm])
            await self.package_sending_finish()
        else:
            await self._processed_update_recipient_packages()
            print({
                "packages_delivered": self._packages_delivered,
                "packages_dropped": self._packages_dropped
            })

    def _add_request_to_requests_queue(self, data: dict) -> None:
        queue_row = data, datetime.utcnow()
        if data[spc.action] == rt.send_package:
            self._add_request_to_send_packages(queue_row)
        elif data[spc.action] == rt.update_preference:
            self._add_request_to_update_preference(queue_row)
        else:
            raise Exception(f"{data[spc.action]} is not valid request type.")

    def _deliver_package(self, package: dict) -> None:
        self._packages_delivered += 1
        print(package)

    async def _process_send_package(
            self, package_id: int, tm: datetime
    ) -> None:
        data, dropped_count = self._get_first_packaged_clean_count(
            package_id, tm
        )
        self._packages_dropped += dropped_count

        recipient_id, tm = data[0][spc.recipient], data[0][spc.tm]

        await self._processed_update_recipient_packages(
            date=tm, recipient_id=recipient_id
        )

        recipient_db = self._recipient_info[recipient_id]
        limits = recipient_db["days_limit"][get_day_from_date(tm)]

        if data[0][spc.package_type] == upc.marketing_package:
            if not recipient_db[upc.marketing_package]:
                self._packages_dropped += 1
                return
            if not limits["marketing_package_limit"]:
                self._packages_dropped += 1
                return
            limits["marketing_package_limit"] -= 1
            self._deliver_package(data)
        elif data[0][spc.package_type] == upc.personal_package:
            if not recipient_db[upc.personal_package]:
                self._packages_dropped += 1
                return
            if not limits["personal_package_limit"]:
                self._packages_dropped += 1
                return
            limits["personal_package_limit"] -= 1
            self._deliver_package(data)
        else:
            raise Exception(
                f"raise no such {data[0][spc.package_type]} package type."
            )

    def _valid_data(
            self, data: dict
    ) -> None | SendPackageData | UpdatePreferenceData:
        match data.get(spc.action):
            case rt.send_package:
                return self._valid_send_package(data)
            case rt.update_preference:
                return self._valid_update_preference(data)
