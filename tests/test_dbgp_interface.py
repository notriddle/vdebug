import sys
sys.path.append('../plugin/python/')
import unittest
import dbgp.connection
import dbgp.interface
import dbgp.response
from mock import MagicMock, patch

class InterfaceTest(unittest.TestCase):      
    """Test the Interface class in the dbgp module."""

    init_msg = """<?xml version="1.0"
        encoding="iso-8859-1"?>\n<init
        xmlns="urn:debugger_interface_v1"
        xmlns:xdebug="http://xdebug.org/dbgp/xdebug"
        fileuri="file:///usr/local/bin/cake" language="PHP"
        interface_version="1.0" appid="30130"
        idekey="netbeans-xdebug"><engine
        version="2.2.0"><![CDATA[Xdebug]]></engine><author><![CDATA[Derick
        Rethans]]></author><url><![CDATA[http://xdebug.org]]></url><copyright><![CDATA[Copyright
        (c) 2002-2012 by Derick
        Rethans]]></copyright></init>"""

    def setUp(self):
        with patch('dbgp.connection.Connection') as c:
            self.c = c.return_value
            self.c.recv_msg.return_value = self.init_msg
            self.c.isconnected.return_value = 1
            self.p = dbgp.interface.Interface(self.c)

    def test_init_msg_parsed(self):
        """Test that the init message from the debugger is
        parsed successfully"""
        assert self.p.language == "PHP"
        assert self.p.version == "1.0"
        assert self.p.idekey == "netbeans-xdebug"

    def test_status_send_adds_trans_id(self):
        """Test that the status command sends the right
        format command and adds a transaction ID"""
        self.p.conn.send_msg = MagicMock()
        self.p.status()
        self.p.conn.send_msg.assert_called_once_with('status -i 1')

    def test_status_retval(self):
        """Test that the status command receives a message from the interface."""
        self.p.conn.recv_msg.return_value = """<?xml
            version="1.0" encoding="iso-8859-1"?>\n
            <response command="status"
                      status="starting"
                      reason="ok"
                      transaction_id="transaction_id">
                message data
            </response>"""
        status_res = self.p.status()
        assert str(status_res) == "starting"

    def test_run_retval(self):
        """Test that the run command receives a message from the interface."""
        self.p.conn.recv_msg.return_value = """<?xml
            version="1.0" encoding="iso-8859-1"?>\n
            <response command="run"
                      status="running"
                      reason="ok"
                      transaction_id="transaction_id">
                message data
            </response>"""
        status_res = self.p.run()
        assert str(status_res) == "running"

    def test_step_into_retval(self):
        """Test that the step_into command receives a message from the interface."""
        self.p.conn.recv_msg.return_value = """<?xml
            version="1.0" encoding="iso-8859-1"?>\n
            <response command="step_into"
                      status="break"
                      reason="ok"
                      transaction_id="transaction_id">
                message data
            </response>"""
        status_res = self.p.run()
        assert str(status_res) == "break"

    def test_step_over_retval(self):
        """Test that the step_over command receives a message from the interface."""
        self.p.conn.recv_msg.return_value = """<?xml
            version="1.0" encoding="iso-8859-1"?>\n
            <response command="step_into"
                      status="break"
                      reason="ok"
                      transaction_id="transaction_id">
                message data
            </response>"""
        status_res = self.p.run()
        assert str(status_res) == "break"

    def test_step_out_retval(self):
        """Test that the step_out command receives a message from the interface."""
        self.p.conn.recv_msg.return_value = """<?xml
            version="1.0" encoding="iso-8859-1"?>\n
            <response command="step_into"
                      status="break"
                      reason="ok"
                      transaction_id="transaction_id">
                message data
            </response>"""
        status_res = self.p.run()
        assert str(status_res) == "break"

    def test_stop_retval(self):
        """Test that the stop command receives a message from the interface."""
        self.p.conn.recv_msg.return_value = """<?xml
            version="1.0" encoding="iso-8859-1"?>\n
            <response command="stop"
                      status="stopping"
                      reason="ok"
                      transaction_id="transaction_id">
                message data
            </response>"""
        status_res = self.p.run()
        assert str(status_res) == "stopping"

    def test_detatch_retval(self):
        """Test that the detatch command receives a message from the interface."""
        self.p.conn.recv_msg.return_value = """<?xml
            version="1.0" encoding="iso-8859-1"?>\n
            <response command="detatch"
                      status="stopped"
                      reason="ok"
                      transaction_id="transaction_id">
                message data
            </response>"""
        status_res = self.p.run()
        assert str(status_res) == "stopped"

    def test_feature_get_retval(self):
        """Test that the feature_get command receives a message from the interface."""
        self.p.conn.recv_msg.return_value = """<?xml
            version="1.0" encoding="iso-8859-1"?>\n<response
            xmlns="urn:debugger_interface_v1"
            xmlns:xdebug="http://xdebug.org/dbgp/xdebug"
            command="feature_get" transaction_id="2"
            feature_name="encoding"
            supported="1"><![CDATA[iso-8859-1]]></response>"""
        res = self.p.feature_get('encoding')
        self.assertEqual(str(res),"iso-8859-1")
        self.assertEqual(res.is_supported(),1)

class interfaceInvalidInitTest(unittest.TestCase):

    init_msg = """<?xml version="1.0"
        encoding="iso-8859-1"?>\n<init
        xmlns="urn:debugger_interface_v1"
        xmlns:xdebug="http://xdebug.org/dbgp/xdebug"
        fileuri="file:///usr/local/bin/cake" language="PHP"
        interface_version="1.0" appid="30130"
        idekey="netbeans-xdebug"><engine
        version="2.2.0"><![CDATA[Xdebug]]></engine><author><![CDATA[Derick
        Rethans]]></author><url><![CDATA[http://xdebug.org]]></url><copyright><![CDATA[Copyright
        (c) 2002-2012 by Derick
        Rethans]]></copyright></init>"""

    invalid_init_msg = """<?xml version="1.0"
        encoding="iso-8859-1"?>\n<invalid
        xmlns="urn:debugger_interface_v1">\n</invalid>"""

    def test_invalid_response_raises_error(self):
        with patch('dbgp.connection.Connection') as c:
            c = c.return_value
            c.recv_msg.return_value = self.invalid_init_msg
            c.isconnected.return_value = 1
            re = "Invalid XML response from debugger"
            self.assertRaisesRegexp(dbgp.response.ResponseError,re,dbgp.interface.Interface,c)

    def test_wrong_idekey_raises_exception(self):
        with patch('dbgp.connection.Connection') as c:
            c = c.return_value
            c.recv_msg.return_value = self.init_msg
            c.isconnected.return_value = 1
            self.assertRaises(dbgp.interface.WrongIDEKeyException,dbgp.interface.Interface,c,'other-ide-key')

