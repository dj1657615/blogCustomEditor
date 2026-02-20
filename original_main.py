# -*- coding: utf-8 -*-

import sys
import traceback
from PyQt5 import QtCore
from caller import chromeAutoUpdate
from controller import working


class UpdateWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal(bool, str)

    @QtCore.pyqtSlot()
    def run(self):
        try:
            print("[update] start")
            chromeAutoUpdate.update()
            print("[update] done")
            self.finished.emit(True, "update ok")
        except Exception as e:
            self.finished.emit(False, str(e))


def main():
    # GUI 필요 없음 → QCoreApplication
    app = QtCore.QCoreApplication(sys.argv)

    update_worker = UpdateWorker()
    update_thread = QtCore.QThread()
    update_worker.moveToThread(update_thread)

    holder = {"work_thread": None}

    def start_working_and_exit_update_thread(ok, msg):
        print(f"[update] finished ok={ok} msg={msg}")

        if not ok:
            print("[update] failed, but continue to start working...")

        print("[working] start")
        holder["work_thread"] = working.Thread()
        holder["work_thread"].start()

        update_thread.quit()

    update_worker.finished.connect(start_working_and_exit_update_thread)
    update_worker.finished.connect(update_thread.quit)
    update_thread.finished.connect(lambda: print("[update_thread] quit"))

    update_thread.started.connect(update_worker.run)
    update_thread.start()

    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        traceback.print_exc()
        with open("error_log.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise
