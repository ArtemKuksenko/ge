import random
import unittest
from datetime import datetime

from send_packages import SendPackages
from validators.allow_package_types import allow_package_types
from validators.allow_request_types import allow_request_types
from validators.send_package_const import send_package_data_const as sp


class TestGalaxyExpress(unittest.TestCase):
    def test_add_request_to_send_packages(self):
        s = SendPackages()
        queue = [
            ({"i": i}, datetime.utcnow())
            for i in range(10)
        ]
        for row in queue:
            s._add_request_to_send_packages(row)

        assert queue == s._send_package_queue

    def test_valid_send_package(self):
        s = SendPackages()
        assert not s._valid_send_package({})
        assert not s._valid_send_package({
            "hello": "hello",
            sp.action: allow_request_types.send_package,
            sp.tm: "2142-08-23T02:40:12-0700",
            sp.sender: 5,
            sp.recipient: 21,
            sp.package_id: 18571,
            sp.package_type: allow_package_types.marketing
        })
        assert not s._valid_send_package({
            sp.action: allow_request_types.send_package,
            sp.tm: "2142-08-23T02:40:12-0700",
            sp.sender: 5,
            sp.recipient: 21,
            sp.package_id: 18571,
            sp.package_type: allow_package_types.marketing + "error"
        })
        assert s._valid_send_package({
            sp.action: allow_request_types.send_package,
            sp.tm: "2142-08-23T02:40:12-0700",
            sp.sender: 5,
            sp.recipient: 21,
            sp.package_id: 18571,
            sp.package_type: allow_package_types.marketing
        })
        assert s._valid_send_package({
            sp.action: allow_request_types.send_package,
            sp.tm: "2142-08-23T02:40:12-0700",
            sp.sender: 5,
            sp.recipient: 21,
            sp.package_id: 18571,
            sp.package_type: allow_package_types.personal
        })

    def test_clean_send_packages_from_queue(self):
        s = SendPackages()
        queue = [
            ({"i": i}, datetime.utcnow())
            for i in range(10)
        ]
        s._send_package_queue = queue
        s._SendPackages__clean_send_packages_from_queue(queue[:5])
        assert s._send_package_queue == queue[5:]

    def test_get_first_packaged_dropped_count_and_clean_other(self):
        s = SendPackages()
        tail = [
            ({
                 "i": i,
                 sp.package_id: 888,
                 sp.tm: datetime.utcnow()
             }, datetime.utcnow())
            for i in range(10)
        ]
        random.shuffle(tail)
        queue = [
            ({
                 "i": i,
                 sp.package_id: 777,
                 sp.tm: datetime.utcnow()
            }, datetime.utcnow())
            for i in range(10)
        ]
        res_etalon = queue[0]
        random.shuffle(queue)
        s._send_package_queue = queue + tail

        res = s._get_first_packaged_clean_count(
            777, datetime.utcnow()
        )
        assert res_etalon[0], 9 == res
        assert s._send_package_queue == tail
