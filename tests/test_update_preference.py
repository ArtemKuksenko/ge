from datetime import datetime

import aiounittest

from update_preference import UpdatePreference
from validators.allow_request_types import allow_request_types
from validators.update_preference_const import update_preference_const as up
from validators.update_preference_const import update_preference_const as upc


class TestUpdatePreference(aiounittest.AsyncTestCase):
    def test_add_request_to_update_preference(self):
        u = UpdatePreference()
        queue = [
            ({"i": i, upc.recipient: i}, datetime.utcnow())
            for i in range(10)
        ]
        for row in queue:
            u._add_request_to_update_preference(row)
            u._add_request_to_update_preference(row)

        assert dict(u._UpdatePreference__update_preference_queue) == {
            row[0][upc.recipient]: [row, row]
            for row in queue
        }

    def test_clean_rows_from_queue(self):
        u = UpdatePreference()
        queue = [
            ({"i": i, upc.recipient: i}, datetime.utcnow())
            for i in range(10)
        ]
        for row in queue:
            u._add_request_to_update_preference(row)
            u._add_request_to_update_preference(row)
        data = [queue.pop(0)]
        u._UpdatePreference__clean_rows_from_queue(
            data, data[0][0][upc.recipient]
        )
        dict_queue = {
            row[0][upc.recipient]: [row, row]
            for row in queue
        }
        dict_queue[0] = []
        assert dict(
            u._UpdatePreference__update_preference_queue
        ) == dict_queue

    def test_valid_update_preference(self):
        u = UpdatePreference()
        assert not u._valid_update_preference({"hello": "hello"})
        assert not u._valid_update_preference({
            up.action: allow_request_types.update_preference,
            up.tm: "2142-08-23T02:40:12-0700",
        })
        assert u._valid_update_preference({
            up.action: allow_request_types.update_preference,
            up.tm: "2142-08-23T02:40:12-0700",
            up.recipient: 123,
            up.personal_package: True,
            up.marketing_package: True
        })
        assert not u._valid_update_preference({
            up.action: allow_request_types.update_preference,
            up.tm: "2142-08-23T02:40:12-0700",
            up.recipient: 123,
        })
        assert u._valid_update_preference({
            up.action: allow_request_types.update_preference,
            up.tm: "2142-08-23T02:40:12-0700",
            up.recipient: 123,
            up.personal_package: True
        })
        assert u._valid_update_preference({
            up.action: allow_request_types.update_preference,
            up.tm: "2142-08-23T02:40:12-0700",
            up.recipient: 123,
            up.personal_package: False
        })
        assert u._valid_update_preference({
            up.action: allow_request_types.update_preference,
            up.tm: "2142-08-23T02:40:12-0700",
            up.recipient: 123,
            up.marketing_package: False
        })

    def test_get_drop_packages(self):
        u = UpdatePreference()
        u_test = UpdatePreference()
        res = []
        q_tm = None
        for i in range(10):
            tm = datetime.utcnow() - datetime.fromtimestamp(i*100)
            row_1 = ({
                "i": i, upc.recipient: 777, upc.tm: tm
             }, datetime.utcnow())
            row_2 = ({
                 "i": i, upc.recipient: 888, upc.tm: tm
             }, datetime.utcnow())
            u._add_request_to_update_preference(row_1)
            u._add_request_to_update_preference(row_2)
            u_test._add_request_to_update_preference(row_2)
            if i == 5:
                q_tm = row_1[0][upc.tm]
                u_test._add_request_to_update_preference(row_1)
            elif i > 5:
                res.append(row_1)
            elif i < 5:
                u_test._add_request_to_update_preference(row_1)

        res.sort(
            key=lambda row: row[0][upc.tm]
        )
        assert res == u._UpdatePreference__get_drop_packages(
            date=q_tm, recipient_id=777
        )

        tst_res = u._UpdatePreference__update_preference_queue
        etalon_res = u_test._UpdatePreference__update_preference_queue
        assert tst_res == etalon_res

    async def test_processed_update_recipient_packages(self):
        u = UpdatePreference()
        for i in range(10):
            tm = datetime.utcnow() - datetime.fromtimestamp(i * 60 * 60 * 24)
            row = ({
                upc.recipient: i,
                upc.tm: tm,
                "marketing": bool(i % 2)
             }, datetime.utcnow())
            u._add_request_to_update_preference(row)
        await u._processed_update_recipient_packages()

        for i in range(10):
            assert u._recipient_info[i]["marketing"] == bool(i % 2)
