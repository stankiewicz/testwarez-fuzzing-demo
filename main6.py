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

http_post_json = Template(name='HTTP_Post_json', fields=[
    Method('POST', name='method', fuzzable=False),
    Delimiter(' ', name='space1', fuzzable=False),
    url.Path('api/pet',name='path',fuzzable=False),
    Delimiter(' ', name='space2',fuzzable=False),
    Static('HTTP', name='protocol name'),
    Delimiter('/', name='fws1',fuzzable=False),
    Dword(1, name='major version',
          encoder=ENC_INT_DEC,fuzzable=False),
    Delimiter('.', name='dot1',fuzzable=False),
    Dword(1, name='minor version',
          encoder=ENC_INT_DEC,fuzzable=False),
    Static('\r\n'),
    Static('Host: 127.0.0.1:5000'),
    Static('\r\n'),
    Static('Content-Type: application/json'),
    Static('\r\n'),
    Static('Accept: */*'),
    Static('\r\n'),
    Static('Content-Length: '),
    Size(
            name='size in bytes',
            sized_field='chunk',
            length=32,encoder=ENC_INT_DEC,
            calc_func=lambda x: len(x) / 8
        ),
    Static('\r\n\r\n'),
    Container(name='chunk', fields=[dict_to_JsonObject({'breed':'Husky','id':1, 'name':'Bingo','tag':'friendly'})]),

    Static('\r\n\r\n', name='eom')                  # 4. The double "new lines" ("\r\n\r\n") at the end of the request
])

model.connect(http_post_json)
fuzzer = ServerFuzzer()
fuzzer.set_model(model)
fuzzer.set_target(target)
fuzzer.set_store_all_reports(True)
os.remove("fuzz_session.sqlite")
fuzzer.set_session_file("fuzz_session.sqlite")
fuzzer.set_interface(WebInterface())


fuzzer.start()
print 'finished!'





# manager = fuzzer.dataman.get_session_info_manager()
# session_info = manager.get_session_info()
#
#
# def get_results(manager):
#     report_manager = manager._reports
#     reports = report_manager.get_report_test_ids()
#     expanded_report = map(lambda key: report_manager.get(key),reports)
#     return expanded_report
#
#
# get_results_task = DataManagerTask(get_results)
# fuzzer.dataman.submit_task(get_results_task)
# results = get_results_task.get_results()

#report_manager = fuzzer.dataman.get_reports_manager()
#reports  = report_manager.get_report_test_ids()

#payloads = map(lambda report: report.to_dict(encoding='utf-8')['transmission_0x0000'],results)

#for p in payloads:
#    print 'request (raw)', p['request (raw)']
#    print 'response (raw)', p['response (raw)']

#fuzzer.stop()
#print 'stopped'
#my_stack.start()