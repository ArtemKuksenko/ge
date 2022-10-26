from collections import defaultdict
from datetime import datetime

from pydantic import ValidationError

from validators.update_preference_const import update_preference_const as upc
from validators.update_preference_const import update_preference_const_keys
from validators.update_preference_data import UpdatePreferenceData


class UpdatePreference:
    def __init__(self):
        self.__update_preference_queue = defaultdict(list)

        self._recipient_info = defaultdict(lambda: {
            upc.marketing_package: True,
            upc.personal_package: True,
            "days_limit": defaultdict(lambda: {
                "personal_package_limit": 3,
                "marketing_package_limit": 1
            })
        })

    def _add_request_to_update_preference(
            self, queue_row: tuple[dict, datetime]
    ) -> None:
        data, _ = queue_row
        recipient_id = data[upc.recipient]
        self.__update_preference_queue[recipient_id].append(queue_row)

    @staticmethod
    def _valid_update_preference(data: dict) -> None | UpdatePreferenceData:
        if set(data.keys()) - update_preference_const_keys:
            return

        marketing_in = upc.marketing_package in data
        personal_in = upc.personal_package in data

        if not (marketing_in or personal_in):
            return

        try:
            return UpdatePreferenceData(**data)
        except ValidationError:
            return

    def __clean_rows_from_queue(
            self, data: list[dict], recipient_id: int
    ) -> None:
        self.__update_preference_queue[recipient_id] = [
            row for row in self.__update_preference_queue[recipient_id]
            if row not in data
        ]

    def __get_drop_packages(
            self, date: datetime = None, recipient_id: int = None
    ) -> list[tuple[dict, datetime]]:
        if recipient_id is None:
            update_preference_data = []
            for rec in self.__update_preference_queue.keys():
                update_preference_data += self.__get_drop_packages(date, rec)
            return update_preference_data

        update_preference_data = self.__update_preference_queue[recipient_id]

        if date:
            update_preference_data = [
                row for row in update_preference_data
                if row[0][upc.tm] < date
            ]

        self.__clean_rows_from_queue(update_preference_data, recipient_id)

        update_preference_data.sort(
            key=lambda row: row[0][upc.tm]
        )
        return update_preference_data

    async def _processed_update_recipient_packages(
            self, date: datetime = None, recipient_id: int = None
    ) -> None:
        update_preference_data = self.__get_drop_packages(date, recipient_id)

        for row, _ in update_preference_data:
            recipient_id = row[upc.recipient]
            recipient_db = self._recipient_info[recipient_id]
            if upc.personal_package in row:
                recipient_db[upc.personal_package] = row[upc.personal_package]
            if upc.marketing_package in row:
                recipient_db[
                    upc.marketing_package
                ] = row[upc.marketing_package]
