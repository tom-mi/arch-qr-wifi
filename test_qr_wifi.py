import unittest

from qr_wifi import parse_qr_data, Wifi, netctl_content


class TestQrWifi(unittest.TestCase):

    def test_parse_qr_data(self):
        tests = [
            (b'QR-Code:http://example.com', None),
            (b'QR-Code:WIFI:T:WPA;S:mynetwork;P:mypass;;', Wifi('mynetwork', 'wpa', 'mypass')),
            (b'QR-Code:WIFI:T:WEP;S:mynetwork;P:mypass;H;', Wifi('mynetwork', 'wep', 'mypass', True)),
            (b'QR-Code:WIFI:T:;S:mynetwork;P:;;', Wifi('mynetwork', 'none', '')),
            (b'QR-Code:WIFI:T:WEP;S:my\\;net\\;work;P:my\\;pass\\;word;;', Wifi('my;net;work', 'wep', 'my;pass;word')),
            (b'QR-Code:WIFI:T:WEP;S:my\\:net\\:work;P:my\\:pass\\:word;;', Wifi('my:net:work', 'wep', 'my:pass:word')),
            (b'QR-Code:WIFI:T:WEP;S:my\\.net\\.work;P:my\\.pass\\.word;;', Wifi('my.net.work', 'wep', 'my.pass.word')),
            (b'QR-Code:WIFI:T:WEP;S:my\\\\net\\\\work;P:my\\\\pass\\\\;;', Wifi('my\\net\\work', 'wep', 'my\\pass\\')),
            (b'QR-Code:WIFI:T:WEP;S:my\\\\network;P:my\\\\pass\\\\\\;;;', Wifi('my\\network', 'wep', 'my\\pass\\;')),
        ]

        for line, expected in tests:
            with self.subTest(data=line):
                self.assertEqual(parse_qr_data(line), expected)

    def test_netctl_content(self):
        wifi = Wifi('my network', 'wpa', 's3cr3t with spaces', True)
        interface = 'wlan0'

        content = netctl_content(interface, wifi)
        lines = content.splitlines()

        self.assertIn("Interface=wlan0", lines)
        self.assertIn("Connection=wireless", lines)
        self.assertIn("ESSID='my network'", lines)
        self.assertIn("Security=wpa", lines)
        self.assertIn("Key='s3cr3t with spaces'", lines)
        self.assertIn("Hidden=yes", lines)
        self.assertIn("IP=dhcp", lines)

    def test_netctl_content_for_key_with_quote(self):
        wifi = Wifi('my network', 'wpa', '"key with quote')
        interface = 'wlan0'

        content = netctl_content(interface, wifi)
        lines = content.splitlines()

        self.assertIn("Key='\"\"\"key with quote\"'", lines)

    def test_netctl_content_for_open_network(self):
        wifi = Wifi('my network', 'none')
        interface = 'wlan0'

        content = netctl_content(interface, wifi)
        lines = content.splitlines()

        self.assertIn("Interface=wlan0", lines)
        self.assertIn("Connection=wireless", lines)
        self.assertIn("ESSID='my network'", lines)
        self.assertIn("Security=none", lines)
        self.assertIn("IP=dhcp", lines)

        self.assertEqual(len(lines), 6)


if __name__ == '__main__':
    unittest.main()
