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
#GET /index.html HTTP/1.1


http_get_v2 = Template(name='HTTP_GET_V2', fields = [
    String('GET', name='method', fuzzable=False),
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


model.connect(http_get_v2)
fuzzer = ServerFuzzer()
fuzzer.set_model(model)
fuzzer.set_target(target)
fuzzer.set_store_all_reports(True)
os.remove("fuzz_session.sqlite")
fuzzer.set_session_file("fuzz_session.sqlite")
fuzzer.set_interface(WebInterface())


fuzzer.start()
print 'finished!'
