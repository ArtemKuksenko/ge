import aiounittest
import ujson as json

from galaxy_express import GalaxyExpress
from validators.allow_package_types import allow_package_types
from validators.allow_request_types import allow_request_types
from validators.send_package_const import send_package_data_const as sp
from validators.update_preference_const import update_preference_const as up


class TestGalaxyExpress(aiounittest.AsyncTestCase):
    async def test_deliver_a_one_package(self):
        g = GalaxyExpress()
        await g.get_request("error")
        await g.get_request(json.dumps({
            up.action: allow_request_types.update_preference,
            up.tm: "2142-08-23T02:40:12-0700",
        }))
        await g.get_request(json.dumps({
            sp.action: allow_request_types.send_package,
            sp.tm: "2142-08-23T02:40:12-0700",
            sp.sender: 5,
            sp.recipient: 21,
            sp.package_id: 18571,
            sp.package_type: allow_package_types.marketing
        }))
        assert g._packages_dropped == 0
        assert g._packages_delivered == 0
        await g.package_sending_finish()
        assert g._packages_dropped == 0
        assert g._packages_delivered == 1

    async def test_try_to_deliver_deprecated_package(self):
        g = GalaxyExpress()
        await g.get_request(json.dumps({
            sp.action: allow_request_types.send_package,
            sp.tm: "2142-08-23T02:40:12-0700",
            sp.sender: 5,
            sp.recipient: 21,
            sp.package_id: 18571,
            sp.package_type: allow_package_types.marketing
        }))
        await g.get_request(json.dumps({
            up.action: allow_request_types.update_preference,
            up.tm: "2000-07-23T02:40:12-0700",
            up.recipient: 21,
            up.marketing_package: False
        }))
        # not enough time
        assert g._packages_dropped == 0
        await g.package_sending_finish()
        assert g._packages_dropped == 1
        pass

    async def test_deprecated_after_sending_package(self):
        g = GalaxyExpress()
        await g.get_request(json.dumps({
            sp.action: allow_request_types.send_package,
            sp.tm: "2142-08-23T02:40:12-0700",
            sp.sender: 5,
            sp.recipient: 21,
            sp.package_id: 18571,
            sp.package_type: allow_package_types.marketing
        }))
        await g.get_request(json.dumps({
            up.action: allow_request_types.update_preference,
            up.tm: "2200-07-23T02:40:12-0700",
            up.recipient: 21,
            up.marketing_package: False
        }))
        assert g._packages_dropped == 0
        await g.package_sending_finish()
        assert g._packages_dropped == 0
        assert g._packages_delivered == 1

    async def test_limits_different_days(self):
        g = GalaxyExpress()
        for i in range(10):
            await g.get_request(json.dumps({
                sp.action: allow_request_types.send_package,
                sp.tm: f"214{i}-08-23T02:40:12-0700",
                sp.sender: 5,
                sp.recipient: 21,
                sp.package_id: 18571,
                sp.package_type: allow_package_types.marketing
            }))
        await g.package_sending_finish()
        assert g._packages_dropped == 0
        assert g._packages_delivered == 10

    async def test_limits_one_day(self):
        g = GalaxyExpress()
        for _ in range(10):
            await g.get_request(json.dumps({
                sp.action: allow_request_types.send_package,
                sp.tm: "2140-08-23T02:40:12-0700",
                sp.sender: 5,
                sp.recipient: 21,
                sp.package_id: 18571,
                sp.package_type: allow_package_types.marketing
            }))
        await g.package_sending_finish()
        assert g._packages_dropped == 9
        assert g._packages_delivered == 1

    def test_valid_send_package_data(self):
        g = GalaxyExpress()

        assert not g._valid_data({"hello": "hello"})
        assert not g._valid_data({
            sp.action: allow_request_types.send_package + "error",
            sp.tm: "2142-08-23T02:40:12-0700",
            sp.sender: 5,
            sp.recipient: 21,
            sp.package_id: 18571,
            sp.package_type: allow_package_types.marketing
        })
