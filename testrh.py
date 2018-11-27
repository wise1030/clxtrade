
from tradeapi.rhGateway import RhGateway
from vnpy.trader.vtEngine import *
def test():
    from PyQt4 import QtCore
    import sys

    def print_log(event):
        log = event.dict_['data']
        print ':'.join([log.logTime, log.logContent])

    app = QtCore.QCoreApplication(sys.argv)

    eventEngine = EventEngine()
    eventEngine.register(EVENT_LOG, print_log)
    eventEngine.start()

    gateway = RhGateway(eventEngine,'RH','Test')
    gateway.connect()
    # gateway.sendOrder()

    sys.exit(app.exec_())


if __name__ == '__main__':
    test()