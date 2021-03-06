from kitty.controllers import BaseController
from kitty.data.data_manager import DataManager, DataManagerTask
from kitty.fuzzers import ServerFuzzer
from kitty.interfaces import WebInterface
from kitty.model import GraphModel

from rest.target import TcpTarget
from rest.controller import MyController

from katnip.legos import url
from katnip.legos.json import dict_to_JsonObject

target = TcpTarget("tcp target","0.0.0.0",5000)

controller = BaseController("my controlller")
target.set_controller(controller)

model = GraphModel()

from kitty.model import *


class Method(String):
    _encoder_type_ = StrEncoder
    lib = None

    def __init__(self, value, max_size=None, encoder=ENC_STR_DEFAULT, fuzzable=True, name=None):
        super(Method, self).__init__(value=value, max_size=max_size, encoder=encoder, fuzzable=fuzzable, name=name)

    def _get_class_lib(self):
        lib = []
        methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "INVALID", ""]
        for method in methods:
            lib.append((method, "method - " + method))
        return lib

http_get_v3 = Template(name='HTTP_GET_V3', fields = [
    Method('GET', name='method', fuzzable=True), # 7 + iteration
    Delimiter(' ', name='space1', fuzzable=False),
    url.Path('somewhere/else', name='path'),
    Delimiter(' ', name='space2'),
    String('HTTP', name='protocol name'),
    Delimiter('/', name='fws1'),
    Dword(1, name='major version', encoder=ENC_INT_DEC),
    Delimiter('.', name='dot1'),
    Dword(1, name='minor version', encoder=ENC_INT_DEC),
    Static('\r\n'),
    Static('Host: 127.0.0.1:5000'),
    Static('\r\n'),
    Static('Connection: close'),
    Static('\r\n\r\n', name='eom')
])

model.connect(http_get_v3)
fuzzer = ServerFuzzer()
fuzzer.set_model(model)
fuzzer.set_target(target)
fuzzer.set_store_all_reports(True)
os.remove("fuzz_session.sqlite")
fuzzer.set_session_file("fuzz_session.sqlite")
fuzzer.set_interface(WebInterface())


fuzzer.start()
print 'finished!'